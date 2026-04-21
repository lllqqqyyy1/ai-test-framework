"""
AI增强层 - URL路由配置
"""
from django.urls import path
from ai_enhancement.api import views

app_name = 'ai_enhancement'

urlpatterns = [
    # AI生成用例
    path('generate-cases/', views.generate_cases, name='generate_cases'),
    
    # AI分析Allure报告
    path('analyze-allure/', views.analyze_allure, name='analyze_allure'),
    
    # 获取AI用例列表
    path('cases/', views.get_cases, name='get_cases'),
    
    # 获取AI任务列表
    path('tasks/', views.get_tasks, name='get_tasks'),
]
