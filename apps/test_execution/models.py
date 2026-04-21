"""
自动化测试执行相关模型
基于 pytest 框架的测试脚本、任务和报告管理
"""
from django.db import models

class TestScript(models.Model):
    """测试脚本模型 - AI 生成的 pytest 测试脚本"""
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('ready', '就绪'),
        ('running', '执行中'),
        ('completed', '已完成'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='脚本名称')
    description = models.TextField(blank=True, default='', verbose_name='脚本描述')
    interface_doc = models.TextField(verbose_name='接口文档')
    script_content = models.TextField(verbose_name='脚本内容')
    script_file = models.CharField(max_length=500, blank=True, default='', verbose_name='脚本文件路径')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'test_scripts'
        verbose_name = '测试脚本'
        verbose_name_plural = '测试脚本'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class TestTask(models.Model):
    """测试任务模型 - 自动化测试执行任务"""
    
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '执行失败'),
    ]
    
    script = models.ForeignKey(TestScript, on_delete=models.CASCADE, related_name='tasks', verbose_name='测试脚本')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    result_file = models.CharField(max_length=500, blank=True, default='', verbose_name='结果文件路径')
    report_file = models.CharField(max_length=500, blank=True, default='', verbose_name='报告文件路径')
    total_cases = models.IntegerField(default=0, verbose_name='总用例数')
    passed_cases = models.IntegerField(default=0, verbose_name='通过数')
    failed_cases = models.IntegerField(default=0, verbose_name='失败数')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    executed_at = models.DateTimeField(auto_now_add=True, verbose_name='执行时间')
    duration = models.FloatField(default=0, verbose_name='执行时长(秒)')
    
    class Meta:
        db_table = 'test_tasks'
        verbose_name = '测试任务'
        verbose_name_plural = '测试任务'
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"{self.script.name} - {self.get_status_display()}"


class TestReport(models.Model):
    """测试报告模型 - 自动化测试生成的标准化报告"""
    
    task = models.ForeignKey(TestTask, on_delete=models.CASCADE, related_name='reports', verbose_name='测试任务')
    report_type = models.CharField(max_length=50, choices=[('html', 'HTML报告'), ('json', 'JSON数据'), ('allure', 'Allure报告')], default='html', verbose_name='报告类型')
    report_content = models.TextField(verbose_name='报告内容')
    ai_analysis = models.TextField(blank=True, default='', verbose_name='AI分析结果')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'test_reports'
        verbose_name = '测试报告'
        verbose_name_plural = '测试报告'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task.script.name} - {self.get_report_type_display()}"
