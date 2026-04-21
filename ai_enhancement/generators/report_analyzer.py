"""
AI测试报告分析器
分析Allure测试结果,自动生成失败原因分析和修复建议
"""
from ai_enhancement.converters.allure_parser import AllureReportParser
from apps.llm.base import LLMServiceFactory


class AIReportAnalyzer:
    """AI测试报告分析器"""
    
    def analyze_report(self, allure_results_dir, provider="qwen"):
        """
        分析Allure测试报告
        
        Args:
            allure_results_dir: allure-results目录路径
            provider: AI模型提供商
            
        Returns:
            dict: {
                'summary': 测试摘要,
                'ai_analysis': AI分析报告,
                'failed_count': 失败用例数
            }
        """
        # 1. 解析Allure结果
        parser = AllureReportParser()
        parsed_data = parser.parse_allure_results(allure_results_dir)
        
        # 2. 提取失败用例
        failed_tests = parser.extract_failed_tests(parsed_data)
        
        # 3. 获取测试摘要
        summary = parser.get_test_summary(parsed_data)
        
        # 4. 调用AI分析
        if failed_tests:
            ai_analysis = self._call_ai_analysis(parsed_data, failed_tests, provider)
        else:
            ai_analysis = "🎉 所有测试用例均通过,无需分析!"
        
        return {
            'summary': summary,
            'ai_analysis': ai_analysis,
            'failed_count': len(failed_tests),
            'total': parsed_data['total'],
            'passed': parsed_data['passed'],
            'failed': parsed_data['failed'],
            'broken': parsed_data['broken']
        }
    
    def _call_ai_analysis(self, parsed_data, failed_tests, provider):
        """调用AI分析失败用例"""
        llm = LLMServiceFactory.create(provider=provider, temperature=0.5)
        
        prompt = self._build_analysis_prompt(parsed_data, failed_tests)
        
        response = llm.invoke(prompt)
        
        return response.content
    
    def _build_analysis_prompt(self, parsed_data, failed_tests):
        """构建分析Prompt"""
        total = parsed_data['total']
        passed = parsed_data['passed']
        failed = parsed_data['failed']
        broken = parsed_data['broken']
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        prompt = f"""你是资深测试专家和开发工程师,请分析以下Allure测试报告。

## 测试概览
- 总用例数: {total}
- 通过: {passed}
- 失败: {failed}
- 中断: {broken}
- 通过率: {pass_rate:.2f}%

## 失败用例详情(共{len(failed_tests)}个)

"""
        
        # 添加失败用例信息(最多10个)
        for i, test in enumerate(failed_tests[:10], 1):
            prompt += f"""
### 失败用例 {i}: {test['name']}
- **状态**: {test['status']}
- **错误信息**: {test['error_message']}
- **耗时**: {test['duration']:.2f}s
"""
            
            if test.get('steps'):
                prompt += "- **失败步骤**:\n"
                for step in test['steps'][:3]:  # 最多3个失败步骤
                    prompt += f"  - {step.get('name', 'Unknown')}: {step.get('error', '')}\n"
            
            prompt += "\n"
        
        prompt += """
请提供以下详细分析:

### 1. 失败原因分类
将失败用例按问题类型分类:
- **接口错误**: 接口返回不符合预期(状态码错误、响应体错误等)
- **数据错误**: 测试数据问题(数据缺失、格式错误等)
- **断言错误**: 测试断言逻辑问题(断言条件错误、期望值错误等)
- **环境问题**: 测试环境问题(网络超时、服务不可用等)
- **代码缺陷**: 被测代码bug
- **其他**: 其他原因

### 2. 每个失败用例的详细分析
对每个失败用例:
- 分析可能的失败原因
- 指出具体的错误位置
- 评估问题严重程度(高/中/低)

### 3. 修复建议
针对每类问题,给出具体的、可操作的修复建议:
- 需要修改测试代码的,给出修改方案
- 需要修改接口实现的,说明预期行为
- 需要调整测试数据的,给出正确数据示例

### 4. 风险评估
- 当前测试质量评估
- 潜在风险分析
- 是否建议发布

### 5. 改进建议
- 测试用例改进建议
- 测试框架改进建议
- 测试流程改进建议

请使用Markdown格式,结构清晰,建议具体可操作。"""
        
        return prompt
