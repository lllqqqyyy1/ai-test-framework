"""
AI 测试报告分析器
分析测试报告,找出失败原因并给出修复建议
"""
import json
from langchain.prompts import ChatPromptTemplate
from apps.llm.base import LLMServiceFactory

class ReportAnalyzer:
    """测试报告分析器"""
    
    def __init__(self, provider="qwen"):
        """
        初始化分析器
        
        Args:
            provider: LLM 提供商名称
        """
        self.llm = LLMServiceFactory.get_llm(provider)
    
    def analyze_report(self, test_report_data):
        """
        AI 分析测试报告
        
        Args:
            test_report_data: 测试报告数据(dict 或 JSON 字符串)
            
        Returns:
            str: AI 分析结果,包含失败原因和修复建议
            
        Raises:
            Exception: 分析失败时抛出异常
        """
        # 如果是字符串,解析为 JSON
        if isinstance(test_report_data, str):
            try:
                test_report_data = json.loads(test_report_data)
            except:
                pass
        
        # 转换为 JSON 字符串用于 prompt
        report_json = json.dumps(test_report_data, ensure_ascii=False, indent=2)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是资深测试专家和调试专家,擅长分析测试报告、定位 Bug 根因并给出修复建议。

你的任务:
1. **测试报告 Summary**:
   - 总用例数、通过数、失败数、通过率
   - 整体测试质量评估

2. **失败用例详细分析**(对每个失败用例):
   - **用例名称**: 失败的测试用例
   - **失败原因**: 分析断言失败的根本原因
   - **错误信息**: 解读错误堆栈和异常信息
   - **可能 Bug 位置**: 推测后端/前端可能的 Bug 位置
   - **修复建议**: 给出具体的修复方案(代码级别)
   - **优先级**: 评估 Bug 的严重程度(P0-P3)

3. **整体建议**:
   - 测试覆盖度评估
   - 需要补充的测试场景
   - 代码质量改进建议

输出格式要求:
- 使用 Markdown 格式,结构清晰
- 使用表格展示统计信息
- 代码建议用代码块标注
- 语气专业、建议具体可操作"""),
            ("user", "请分析以下测试报告:\n\n{report_data}")
        ])
        
        # 构建调用链
        chain = prompt | self.llm
        
        # 调用 LLM
        response = chain.invoke({"report_data": report_json})
        analysis = response.content
        
        return analysis
    
    def analyze_failed_cases_only(self, failed_cases):
        """
        只分析失败的测试用例
        
        Args:
            failed_cases: 失败用例列表
            
        Returns:
            str: 分析结果
        """
        cases_json = json.dumps(failed_cases, ensure_ascii=False, indent=2)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是调试专家,请专注分析失败的测试用例。

对每个失败用例,请提供:
1. 失败原因深度分析
2. 根因定位(前端/后端/测试代码)
3. 具体修复建议(含代码示例)
4. 预防措施

只输出分析结果,不要复述用例内容。"""),
            ("user", "失败的测试用例:\n\n{cases}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"cases": cases_json})
        
        return response.content
