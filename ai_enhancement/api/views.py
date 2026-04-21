"""
AI增强层 - API接口视图
提供AI生成用例、分析报告等接口
"""
import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ai_enhancement.generators.case_generator import AICaseGenerator
from ai_enhancement.generators.report_analyzer import AIReportAnalyzer
from ai_enhancement.models.models import AIGeneratedCase, AIAnalysisTask


@csrf_exempt
@require_http_methods(["POST"])
def generate_cases(request):
    """
    AI生成测试用例
    
    POST /api/ai/generate-cases/
    
    请求体:
    {
        "api_doc": "接口文档描述",
        "case_name": "用例名称前缀",
        "provider": "qwen",
        "save_to_db": true
    }
    
    返回:
    {
        "success": true,
        "yaml_path": "YAML文件路径",
        "yaml_content": "YAML内容",
        "case_count": 10
    }
    """
    try:
        data = json.loads(request.body)
        
        api_doc = data.get('api_doc', '')
        case_name = data.get('case_name', 'test_api')
        provider = data.get('provider', 'qwen')
        save_to_db = data.get('save_to_db', True)
        
        if not api_doc:
            return JsonResponse({
                'success': False,
                'error': '接口文档不能为空'
            })
        
        # 调用AI生成器
        generator = AICaseGenerator()
        result = generator.generate_cases(
            api_doc=api_doc,
            case_name=case_name,
            provider=provider
        )
        
        # 保存到数据库
        if save_to_db:
            saved_count = _save_cases_to_db(
                result['cases_data'],
                result['yaml_path'],
                result['yaml_content'],
                api_doc,
                provider
            )
            result['saved_to_db'] = saved_count
        
        return JsonResponse({
            'success': True,
            'yaml_path': result['yaml_path'],
            'yaml_content': result['yaml_content'],
            'case_count': result['case_count'],
            'saved_to_db': result.get('saved_to_db', 0)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def _save_cases_to_db(cases_data, yaml_path, yaml_content, api_doc, provider):
    """保存用例到数据库"""
    saved_count = 0
    
    for case in cases_data:
        ai_case = AIGeneratedCase(
            name=case.get('case_name', '未命名用例'),
            yaml_content=yaml_content,
            yaml_file_path=yaml_path,
            api_doc=api_doc,
            ai_provider=provider,
            status='draft'
        )
        ai_case.save()
        saved_count += 1
    
    return saved_count


@csrf_exempt
@require_http_methods(["POST"])
def analyze_allure(request):
    """
    AI分析Allure测试报告
    
    POST /api/ai/analyze-allure/
    
    请求体:
    {
        "allure_results_dir": "allure-results目录路径",
        "provider": "qwen",
        "save_to_db": true
    }
    
    返回:
    {
        "success": true,
        "summary": "测试摘要",
        "ai_analysis": "AI分析报告",
        "total": 10,
        "passed": 8,
        "failed": 2
    }
    """
    try:
        data = json.loads(request.body)
        
        allure_results_dir = data.get('allure_results_dir', '')
        provider = data.get('provider', 'qwen')
        save_to_db = data.get('save_to_db', True)
        
        if not allure_results_dir:
            return JsonResponse({
                'success': False,
                'error': 'allure_results_dir不能为空'
            })
        
        # 调用AI分析器
        analyzer = AIReportAnalyzer()
        result = analyzer.analyze_report(
            allure_results_dir=allure_results_dir,
            provider=provider
        )
        
        # 保存任务到数据库
        if save_to_db:
            task = AIAnalysisTask(
                task_name=f"报告分析_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                task_type='report_analysis',
                input_data=json.dumps({'allure_results_dir': allure_results_dir}),
                output_data=result['ai_analysis'],
                ai_provider=provider,
                status='completed'
            )
            task.save()
            result['task_id'] = task.id
        
        return JsonResponse({
            'success': True,
            'summary': result['summary'],
            'ai_analysis': result['ai_analysis'],
            'total': result['total'],
            'passed': result['passed'],
            'failed': result['failed'],
            'broken': result['broken'],
            'task_id': result.get('task_id')
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["GET"])
def get_cases(request):
    """
    获取AI生成的用例列表
    
    GET /api/ai/cases/
    
    返回:
    {
        "success": true,
        "cases": [...]
    }
    """
    try:
        cases = AIGeneratedCase.objects.all()[:50]  # 最近50条
        
        cases_list = []
        for case in cases:
            cases_list.append({
                'id': case.id,
                'name': case.name,
                'priority': case.priority,
                'yaml_file_path': case.yaml_file_path,
                'status': case.status,
                'ai_provider': case.ai_provider,
                'generated_at': case.generated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'success': True,
            'cases': cases_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["GET"])
def get_tasks(request):
    """
    获取AI分析任务列表
    
    GET /api/ai/tasks/
    
    返回:
    {
        "success": true,
        "tasks": [...]
    }
    """
    try:
        tasks = AIAnalysisTask.objects.all()[:50]  # 最近50条
        
        tasks_list = []
        for task in tasks:
            tasks_list.append({
                'id': task.id,
                'task_name': task.task_name,
                'task_type': task.task_type,
                'status': task.status,
                'ai_provider': task.ai_provider,
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'success': True,
            'tasks': tasks_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
