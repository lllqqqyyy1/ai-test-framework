"""
URL Configuration for AI Test Case Generator
"""
from django.contrib import admin
from django.urls import path, include
from apps.core.views import generate_test_cases, save_test_case, index_view
from apps.test_execution.views import (
    generate_test_script,
    save_test_script,
    execute_test,
    analyze_test_report,
    get_script_list,
    get_task_list
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # 原有 API 接口
    path('api/generate/', generate_test_cases, name='api_generate'),
    path('api/save-test-case/', save_test_case, name='api_save_test_case'),
    # 测试脚本生成与执行 API
    path('api/generate-script/', generate_test_script, name='api_generate_script'),
    path('api/save-script/', save_test_script, name='api_save_script'),
    path('api/execute-test/', execute_test, name='api_execute_test'),
    path('api/analyze-report/', analyze_test_report, name='api_analyze_report'),
    path('api/script-list/', get_script_list, name='api_script_list'),
    path('api/task-list/', get_task_list, name='api_task_list'),
    # AI增强层 API
    path('api/ai/', include('ai_enhancement.api.urls')),
    # 前端页面
    path('', index_view, name='index'),
]
