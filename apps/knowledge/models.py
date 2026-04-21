"""
知识库模型 (用于 Milvus 向量检索)
"""
from django.db import models

class KnowledgeBase(models.Model):
    """知识库数据模型"""
    
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    vector_id = models.CharField(max_length=100, verbose_name='Milvus 向量 ID', blank=True, default='')
    category = models.CharField(max_length=50, verbose_name='分类', blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'knowledge_base'
        verbose_name = '知识库'
        verbose_name_plural = '知识库'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
