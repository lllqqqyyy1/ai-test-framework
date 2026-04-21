"""
AI 测试脚本生成器
根据接口文档生成可执行的 pytest 测试脚本
"""
import json
import re
from langchain.prompts import ChatPromptTemplate
from apps.llm.base import LLMServiceFactory

class TestScriptGenerator:
    """测试脚本生成器"""
    
    def __init__(self, provider="qwen"):
        """
        初始化生成器
        
        Args:
            provider: LLM 提供商名称
        """
        self.llm = LLMServiceFactory.get_llm(provider)
    
    def generate_test_script(self, interface_doc, script_name="test_api"):
        """
        生成 pytest 测试脚本
        
        Args:
            interface_doc: 接口文档描述
            script_name: 脚本名称
            
        Returns:
            str: 生成的 Python 测试脚本代码
            
        Raises:
            Exception: 生成失败时抛出异常
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是资深测试开发工程师,精通 Python、pytest 和 requests 库。请根据用户提供的接口文档,生成完整、可执行的 pytest 自动化测试脚本。

严格要求:
1. 使用 Python 3.x + pytest + requests 库
2. 必须包含以下测试场景:
   - 正向测试(正确参数,验证成功响应)
   - 反向测试(错误参数、缺少参数、类型错误)
   - 边界值测试(最小值、最大值、空值)
   - 异常场景(超时、网络错误、服务端错误)

3. 代码规范要求:
   - 使用 pytest.mark.parametrize 进行参数化测试
   - 每个测试函数要有详细的 docstring 说明
   - 使用 assert 进行断言,断言信息要清晰明确
   - 包含 setup/teardown 或 fixture 处理测试数据
   - 提取公共代码为辅助函数

4. 测试脚本结构:
   - 导入必要的库
   - 定义全局常量(BASE_URL, HEADERS 等)
   - 定义 fixture(测试数据准备)
   - 测试函数(按功能分组)
   - 辅助函数(可选)

5. 输出格式:
   - 只输出 Python 代码,不要包含任何 Markdown 标记(如 ```python)
   - 不要包含解释性文字
   - 确保代码语法正确,可以直接运行

示例接口文档:
POST /api/login
参数: phone(手机号), code(验证码)
返回: {{code: 0, message: "success", data: {{token, user_id}}}}"""),
            ("user", "请根据以下接口文档生成测试脚本:\n\n{interface_doc}")
        ])
        
        # 构建调用链
        chain = prompt | self.llm
        
        # 调用 LLM
        response = chain.invoke({"interface_doc": interface_doc})
        code = response.content
        
        # 清理代码(移除可能的 Markdown 标记)
        code = self._clean_code(code)
        
        return code
    
    def _clean_code(self, code):
        """
        清理生成的代码,移除 Markdown 标记
        
        Args:
            code: 原始代码字符串
            
        Returns:
            str: 清理后的代码
        """
        # 移除 ```python 或 ``` 标记
        code = re.sub(r'^```python\s*', '', code, flags=re.MULTILINE)
        code = re.sub(r'^```\s*$', '', code, flags=re.MULTILINE)
        code = code.strip()
        
        return code
