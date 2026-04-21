"""
LLM 服务模块
提供统一的 LLM 调用接口,支持多种模型提供商
"""
import os
from django.conf import settings
from langchain_openai import ChatOpenAI

class LLMServiceFactory:
    """LLM 服务工厂,动态创建不同模型的客户端"""
    
    @staticmethod
    def get_llm(provider=None):
        """
        获取 LLM 实例
        
        Args:
            provider: LLM 提供商名称 ('deepseek' 或 'qwen'),默认使用配置文件中的默认提供商
            
        Returns:
            ChatOpenAI: LangChain 的聊天模型实例
            
        Raises:
            ValueError: 当提供商不存在或 API Key 未配置时
        """
        if provider is None:
            provider = settings.LLM_PROVIDERS.get('default_provider', 'deepseek')
        
        providers = settings.LLM_PROVIDERS
        if provider not in providers:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")
        
        config = providers[provider]
        api_key = config.get('api_key')
        
        if not api_key:
            raise ValueError(f"{provider} 的 API Key 未配置,请在 .env 文件中设置")
        
        # 创建 ChatOpenAI 实例
        # temperature=0.3 保证生成的内容稳定性
        llm = ChatOpenAI(
            api_key=api_key,
            base_url=config['base_url'],
            model_name=config['model'],
            temperature=0.3,
            max_tokens=4000,
        )
        
        return llm
    
    @staticmethod
    def get_available_providers():
        """获取所有可用的 LLM 提供商列表"""
        providers = settings.LLM_PROVIDERS.copy()
        providers.pop('default_provider', None)
        return list(providers.keys())
