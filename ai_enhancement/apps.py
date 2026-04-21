"""
AI增强层 - Django应用配置
"""
from django.apps import AppConfig


class AIEnhancementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_enhancement'
    verbose_name = 'AI增强模块'
