"""
测试用例生成器
使用 LLM 生成功能测试用例和接口测试用例
"""
import json
import re
from langchain.prompts import ChatPromptTemplate
from apps.llm.base import LLMServiceFactory

class TestCaseGenerator:
    """测试用例生成器"""
    
    def __init__(self, provider="deepseek"):
        """
        初始化生成器
        
        Args:
            provider: LLM 提供商名称
        """
        self.llm = LLMServiceFactory.get_llm(provider)
    
    def generate_functional_cases(self, requirements):
        """
        生成功能测试用例
        
        Args:
            requirements: 需求描述文本
            
        Returns:
            list: 测试用例列表,每个用例为字典格式
            
        Raises:
            Exception: 生成失败时抛出异常
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是资深测试工程师,专注于软件质量保障。请根据用户提供的需求描述,生成结构化、专业的功能测试用例。

要求:
1. 每个用例必须包含以下字段:
   - title: 用例标题(简洁明了)
   - description: 用例描述(详细说明测试目的)
   - test_steps: 测试步骤(使用编号列表,步骤清晰)
   - expected_results: 预期结果(明确描述期望的行为)

2. 测试覆盖要求:
   - 正向场景(正常业务流程)
   - 反向场景(异常输入、错误处理)
   - 边界值测试
   - 用户体验相关场景

3. 输出格式:
   - 必须输出合法的 JSON 数组
   - 数组中每个元素是一个用例对象
   - 只输出 JSON,不要包含任何其他文字、解释或 Markdown 标记

示例格式:
[
  {{
    "title": "正常登录流程测试",
    "description": "验证用户使用正确的手机号和验证码能够成功登录",
    "test_steps": "1. 打开登录页面\\n2. 输入正确的手机号\\n3. 点击获取验证码\\n4. 输入收到的验证码\\n5. 点击登录按钮",
    "expected_results": "成功跳转到首页,显示用户信息"
  }}
]"""),
            ("user", "需求描述:{requirements}")
        ])
        
        # 构建调用链
        chain = prompt | self.llm
        
        # 调用 LLM
        response = chain.invoke({"requirements": requirements})
        content = response.content
        
        # 解析 JSON 响应
        return self._parse_json_response(content)
    
    def generate_interface_cases(self, interface_desc):
        """
        生成接口测试用例
        
        Args:
            interface_desc: 接口描述文本
            
        Returns:
            list: 测试用例列表,每个用例为字典格式
            
        Raises:
            Exception: 生成失败时抛出异常
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是资深接口测试工程师,专注于 API 质量保障。请根据用户提供的接口描述,生成结构化、专业的接口测试用例。

要求:
1. 每个用例必须包含以下字段:
   - title: 用例标题(简洁明了)
   - description: 用例描述(详细说明测试目的)
   - test_steps: 测试步骤(包含请求方法、URL、请求参数、请求头等)
   - expected_results: 预期结果(包含 HTTP 状态码、响应数据结构)

2. 测试覆盖要求:
   - 正常场景(正确的请求参数和数据)
   - 异常参数测试(缺少必填字段、参数类型错误、参数长度超限)
   - 边界值测试(最小值、最大值、空值)
   - 权限测试(未授权、Token 过期、权限不足)
   - 安全性测试(SQL 注入、XSS 攻击)

3. 输出格式:
   - 必须输出合法的 JSON 数组
   - 数组中每个元素是一个用例对象
   - 只输出 JSON,不要包含任何其他文字、解释或 Markdown 标记

示例格式:
[
  {{
    "title": "正常登录接口测试",
    "description": "验证使用正确的手机号和验证码能够成功调用登录接口",
    "test_steps": "POST /api/login\\n请求头: Content-Type: application/json\\n请求体: {{\"phone\": \"13800138000\", \"code\": \"123456\"}}",
    "expected_results": "HTTP 200, 返回 {{\"code\": 0, \"message\": \"success\", \"data\": {{\"token\": \"xxx\", \"user_id\": 123}}}}"
  }}
]"""),
            ("user", "接口描述:{interface_desc}")
        ])
        
        # 构建调用链
        chain = prompt | self.llm
        
        # 调用 LLM
        response = chain.invoke({"interface_desc": interface_desc})
        content = response.content
        
        # 解析 JSON 响应
        return self._parse_json_response(content)
    
    def _parse_json_response(self, content):
        """
        解析 LLM 返回的 JSON 响应
        
        Args:
            content: LLM 返回的文本内容
            
        Returns:
            list: 解析后的测试用例列表
            
        Raises:
            ValueError: JSON 解析失败时抛出异常
        """
        try:
            # 尝试直接解析 JSON
            cases = json.loads(content)
            if isinstance(cases, list):
                return cases
            else:
                raise ValueError("返回的数据格式不正确,期望数组类型")
        except json.JSONDecodeError:
            # 如果直接解析失败,尝试提取 JSON 部分
            try:
                # 匹配 JSON 数组
                json_match = re.search(r'\[[\s\S]*\]', content)
                if json_match:
                    json_str = json_match.group()
                    cases = json.loads(json_str)
                    return cases
                else:
                    raise ValueError("无法从响应中提取 JSON 数据")
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON 解析失败: {str(e)}\n原始内容: {content[:200]}")
            except Exception as e:
                raise ValueError(f"提取 JSON 失败: {str(e)}")
