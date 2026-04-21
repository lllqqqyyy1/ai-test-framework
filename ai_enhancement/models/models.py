"""
AI增强层数据模型
存储AI生成的测试用例和分析任务
"""
from django.db import models


class AIGeneratedCase(models.Model):
    """AI生成的测试用例"""
    
    PRIORITY_CHOICES = [
        ('P0', 'P0-核心功能'),
        ('P1', 'P1-重要功能'),
        ('P2', 'P2-一般功能'),
        ('P3', 'P3-边缘功能'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('ready', '就绪'),
        ('executed', '已执行'),
        ('passed', '通过'),
        ('failed', '失败'),
    ]
    
    # 基本信息
    name = models.CharField(max_length=200, verbose_name='用例名称')
    priority = models.CharField(max_length=2, choices=PRIORITY_CHOICES, default='P1', verbose_name='优先级')
    description = models.TextField(blank=True, default='', verbose_name='用例描述')
    
    # YAML内容
    yaml_content = models.TextField(verbose_name='YAML用例内容')
    yaml_file_path = models.CharField(max_length=500, blank=True, default='', verbose_name='YAML文件路径')
    
    # 接口信息
    api_endpoint = models.CharField(max_length=500, blank=True, default='', verbose_name='接口路径')
    api_method = models.CharField(max_length=10, default='POST', verbose_name='请求方法')
    
    # 元数据
    source = models.CharField(max_length=50, default='ai_generated', verbose_name='来源')
    ai_provider = models.CharField(max_length=50, default='qwen', verbose_name='AI模型')
    api_doc = models.TextField(blank=True, default='', verbose_name='接口文档')
    
    # 时间戳
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    
    class Meta:
        db_table = 'ai_generated_cases'
        verbose_name = 'AI生成的测试用例'
        verbose_name_plural = verbose_name
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.name} ({self.priority})"


class AIAnalysisTask(models.Model):
    """AI分析任务"""
    
    TASK_TYPE_CHOICES = [
        ('case_generation', '用例生成'),
        ('report_analysis', '报告分析'),
        ('script_generation', '脚本生成'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    # 任务信息
    task_name = models.CharField(max_length=200, verbose_name='任务名称')
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES, verbose_name='任务类型')
    
    # 输入输出
    input_data = models.TextField(verbose_name='输入数据')
    output_data = models.TextField(blank=True, default='', verbose_name='输出结果')
    
    # AI配置
    ai_provider = models.CharField(max_length=50, default='qwen', verbose_name='AI模型')
    
    # 元数据
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    
    class Meta:
        db_table = 'ai_analysis_tasks'
        verbose_name = 'AI分析任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task_name} ({self.task_type})"
