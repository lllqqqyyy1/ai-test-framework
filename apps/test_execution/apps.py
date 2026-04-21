from django.apps import AppConfig

class TestExecutionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.test_execution'
    verbose_name = '自动化测试执行引擎'
