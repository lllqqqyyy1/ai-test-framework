"""
测试用例模型
"""
from django.db import models

class TestCase(models.Model):
    """测试用例数据模型"""
    
    CASE_TYPE_CHOICES = [
        ('functional', '功能测试用例'),
        ('interface', '接口测试用例'),
    ]
    
    PRIORITY_CHOICES = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='用例标题')
    description = models.TextField(verbose_name='用例描述')
    requirements = models.TextField(verbose_name='需求描述')
    code_snippet = models.TextField(blank=True, default='', verbose_name='代码片段')
    test_steps = models.TextField(verbose_name='测试步骤')
    expected_results = models.TextField(verbose_name='预期结果')
    case_type = models.CharField(max_length=20, choices=CASE_TYPE_CHOICES, verbose_name='用例类型')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'test_cases'
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_case_type_display()})"
