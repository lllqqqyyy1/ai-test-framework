"""
AI测试用例生成器
根据接口文档生成YAML格式的测试用例,保存到文件和数据库
"""
import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from apps.llm.base import LLMServiceFactory


class AICaseGenerator:
    """AI测试用例生成器 - 生成符合框架规范的YAML用例"""
    
    def __init__(self, base_dir=None):
        """
        初始化生成器
        
        Args:
            base_dir: 项目基础目录
        """
        self.base_dir = base_dir or Path(__file__).parent.parent.parent
        self.yaml_output_dir = self.base_dir / 'automation_framework' / 'data' / 'ai_generated'
        self.yaml_output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_cases(self, api_doc, case_name="test_api", provider="qwen"):
        """
        根据接口文档生成测试用例
        
        Args:
            api_doc: 接口文档描述
            case_name: 用例名称
            provider: AI模型提供商
            
        Returns:
            dict: {
                'yaml_content': YAML内容,
                'yaml_path': YAML文件路径,
                'cases_data': 用例数据,
                'case_count': 用例数量
            }
        """
        # 1. 调用AI生成用例
        cases_data = self._call_ai(api_doc, case_name, provider)
        
        # 2. 转换为框架YAML格式
        yaml_content = self._convert_to_framework_yaml(cases_data, case_name)
        
        # 3. 保存到YAML文件
        yaml_path = self._save_to_yaml(yaml_content, case_name)
        
        return {
            'yaml_content': yaml_content,
            'yaml_path': str(yaml_path),
            'cases_data': cases_data,
            'case_count': len(cases_data)
        }
    
    def _call_ai(self, api_doc, case_name, provider):
        """调用AI生成测试用例"""
        llm = LLMServiceFactory.create(provider=provider, temperature=0.7)
        
        prompt = self._build_prompt(api_doc, case_name)
        
        response = llm.invoke(prompt)
        
        # 解析AI响应
        cases_data = self._parse_ai_response(response.content)
        
        return cases_data
    
    def _build_prompt(self, api_doc, case_name):
        """构建AI Prompt"""
        return f"""你是资深测试工程师,请根据以下接口文档生成测试用例。

接口文档:
{api_doc}

用例名称前缀: {case_name}

要求:
1. 覆盖以下测试场景:
   - 正向测试(正确参数,验证成功响应)
   - 反向测试(错误参数、缺少参数、类型错误)
   - 边界值测试(最小值、最大值、空值)
   - 异常测试(网络超时、服务错误)

2. 每个用例必须包含以下字段:
   - case_name: 用例名称(中文描述)
   - data: 请求参数
   - validation: 验证规则(使用contains/eq/neq等断言)
   - extract: 需要提取的字段(可选,使用JSONPath格式)

3. 返回JSON数组格式,不要包含任何Markdown标记

示例格式:
[
  {{
    "case_name": "用户登录-正确用户名和密码",
    "data": {{
      "user_name": "test01",
      "passwd": "admin123"
    }},
    "validation": [
      {{"contains": {{"error_code": "none"}}}},
      {{"eq": {{"msg": "登录成功"}}}}
    ],
    "extract": {{
      "token": "$.token"
    }}
  }},
  {{
    "case_name": "用户登录-密码错误",
    "data": {{
      "user_name": "test01",
      "passwd": "wrong_password"
    }},
    "validation": [
      {{"eq": {{"error_code": "1001"}}}},
      {{"contains": {{"msg": "密码错误"}}}}
    ]
  }}
]

请生成8-12个测试用例。"""
    
    def _parse_ai_response(self, content):
        """解析AI响应"""
        # 尝试提取JSON数组
        import re
        
        # 移除可能的Markdown代码块标记
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        # 尝试解析JSON
        try:
            cases_data = json.loads(content)
            if isinstance(cases_data, list):
                return cases_data
        except json.JSONDecodeError:
            pass
        
        # 尝试用正则提取
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            try:
                cases_data = json.loads(match.group())
                return cases_data
            except:
                pass
        
        raise ValueError(f"AI响应格式错误,无法解析为JSON数组:\n{content[:200]}")
    
    def _convert_to_framework_yaml(self, cases_data, case_name):
        """转换为框架YAML格式"""
        # 提取接口信息(从第一用例推测,或从API文档解析)
        api_info = self._extract_api_info(cases_data[0] if cases_data else {})
        
        # 构建YAML结构
        yaml_data = {
            'baseInfo': {
                'api_name': case_name,
                'url': api_info.get('url', '/api/endpoint'),
                'method': api_info.get('method', 'post'),
                'header': api_info.get('header', {
                    'Content-Type': 'application/json'
                })
            },
            'testCase': []
        }
        
        # 转换每个用例
        for case in cases_data:
            yaml_case = {
                'case_name': case.get('case_name', '未命名用例'),
                'data': case.get('data', {}),
                'validation': case.get('validation', []),
            }
            
            # 可选字段
            if 'extract' in case:
                yaml_case['extract'] = case['extract']
            
            yaml_data['testCase'].append(yaml_case)
        
        # 转换为YAML字符串
        yaml_content = yaml.dump(
            yaml_data,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            encoding='utf-8'
        ).decode('utf-8')
        
        return yaml_content
    
    def _extract_api_info(self, first_case):
        """从用例中提取API信息"""
        # 这里可以根据实际情况解析
        # 暂时返回默认值
        return {
            'url': '/api/endpoint',
            'method': 'post',
            'header': {'Content-Type': 'application/json'}
        }
    
    def _save_to_yaml(self, yaml_content, case_name):
        """保存到YAML文件"""
        timestamp = int(datetime.now().timestamp())
        filename = f"{case_name}_{timestamp}.yaml"
        yaml_path = self.yaml_output_dir / filename
        
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        return yaml_path
    
    def save_to_database(self, cases_data, yaml_path, api_doc, provider="qwen"):
        """
        保存用例到数据库
        
        Args:
            cases_data: 用例数据
            yaml_path: YAML文件路径
            api_doc: 接口文档
            provider: AI模型
            
        Returns:
            int: 保存的用例数量
        """
        try:
            from apps.core.models import TestCase
            
            saved_count = 0
            
            for case in cases_data:
                # 构建测试步骤
                test_steps = f"请求参数: {json.dumps(case.get('data', {}), ensure_ascii=False)}"
                expected_results = f"验证规则: {json.dumps(case.get('validation', []), ensure_ascii=False)}"
                
                # 创建用例记录
                test_case = TestCase(
                    title=case.get('case_name', '未命名用例'),
                    description=f"AI生成的测试用例\n\n接口文档:\n{api_doc}",
                    test_steps=test_steps,
                    expected_results=expected_results,
                    case_type='interface',
                    priority='P1',
                    input_type='ai_generated',
                    ai_provider=provider,
                    yaml_file_path=yaml_path
                )
                test_case.save()
                saved_count += 1
            
            return saved_count
            
        except Exception as e:
            print(f"保存到数据库失败: {e}")
            return 0
