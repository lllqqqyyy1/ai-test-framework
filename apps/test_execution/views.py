"""
测试执行视图
提供测试脚本生成、执行、报告分析等 API
"""
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from apps.test_execution.models import TestScript, TestTask, TestReport
from apps.test_execution.executor import TestExecutor
from apps.ai_agents.test_script_generator.generator import TestScriptGenerator
from apps.ai_agents.report_analyzer.analyzer import ReportAnalyzer

# 初始化执行器
executor = TestExecutor()

@csrf_exempt
@require_http_methods(["POST"])
def generate_test_script(request):
    """
    AI 生成测试脚本 API
    
    请求体:
    {
        "interface_doc": "接口文档描述",
        "script_name": "脚本名称",
        "provider": "qwen" 或 "deepseek"
    }
    """
    try:
        data = json.loads(request.body)
        interface_doc = data.get("interface_doc")
        script_name = data.get("script_name", "test_api")
        provider = data.get("provider", "qwen")
        
        if not interface_doc:
            return JsonResponse({
                "success": False,
                "message": "缺少 interface_doc 参数"
            }, status=400)
        
        # 生成脚本
        generator = TestScriptGenerator(provider)
        script_content = generator.generate_test_script(interface_doc, script_name)
        
        # 保存到数据库
        test_script = TestScript.objects.create(
            name=script_name,
            interface_doc=interface_doc,
            script_content=script_content,
            status='ready'
        )
        
        return JsonResponse({
            "success": True,
            "script_id": test_script.id,
            "script_content": script_content,
            "message": "测试脚本生成成功"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"生成失败: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_test_script(request):
    """
    保存测试脚本到文件
    
    请求体:
    {
        "script_id": 脚本ID,
        "script_name": 脚本名称
    }
    """
    try:
        data = json.loads(request.body)
        script_id = data.get("script_id")
        
        if not script_id:
            return JsonResponse({
                "success": False,
                "message": "缺少 script_id 参数"
            }, status=400)
        
        # 获取脚本
        try:
            test_script = TestScript.objects.get(id=script_id)
        except TestScript.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "脚本不存在"
            }, status=404)
        
        # 保存到文件
        script_path = executor.save_script(test_script.name, test_script.script_content)
        test_script.script_file = script_path
        test_script.save()
        
        return JsonResponse({
            "success": True,
            "script_path": script_path,
            "message": "脚本已保存到文件"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"保存失败: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def execute_test(request):
    """
    执行测试
    
    请求体:
    {
        "script_id": 脚本ID,
        "script_path": "脚本文件路径" (可选,如果有则直接使用)
    }
    """
    try:
        data = json.loads(request.body)
        script_id = data.get("script_id")
        script_path = data.get("script_path")
        
        if not script_id and not script_path:
            return JsonResponse({
                "success": False,
                "message": "需要提供 script_id 或 script_path"
            }, status=400)
        
        # 获取脚本路径
        if not script_path:
            try:
                test_script = TestScript.objects.get(id=script_id)
                if not test_script.script_file:
                    # 先保存到文件
                    script_path = executor.save_script(test_script.name, test_script.script_content)
                    test_script.script_file = script_path
                    test_script.save()
                else:
                    script_path = test_script.script_file
            except TestScript.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": "脚本不存在"
                }, status=404)
        
        # 创建测试任务
        test_script = TestScript.objects.get(id=script_id) if script_id else None
        test_task = TestTask.objects.create(
            script=test_script,
            status='running'
        )
        
        # 执行测试
        result = executor.execute_test(script_path, f"task_{test_task.id}")
        
        # 更新任务状态
        test_task.status = 'completed' if result['success'] else 'failed'
        test_task.result_file = result.get('json_path', '')
        test_task.report_file = result.get('report_path', '')
        test_task.total_cases = result.get('total', 0)
        test_task.passed_cases = result.get('passed', 0)
        test_task.failed_cases = result.get('failed', 0)
        test_task.error_message = result.get('error', '')
        test_task.duration = result.get('duration', 0)
        test_task.save()
        
        # 保存报告
        if result.get('json_path') and os.path.exists(result['json_path']):
            json_data = executor.get_json_report_data(result['json_path'])
            TestReport.objects.create(
                task=test_task,
                report_type='json',
                report_content=json.dumps(json_data, ensure_ascii=False)
            )
        
        return JsonResponse({
            "success": True,
            "task_id": test_task.id,
            "result": result,
            "message": "测试执行完成"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"执行失败: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def analyze_test_report(request):
    """
    AI 分析测试报告
    
    请求体:
    {
        "task_id": 任务ID,
        "report_data": {...} (可选,直接提供报告数据)
    }
    """
    try:
        data = json.loads(request.body)
        task_id = data.get("task_id")
        report_data = data.get("report_data")
        
        # 获取报告数据
        if not report_data and task_id:
            try:
                test_task = TestTask.objects.get(id=task_id)
                if test_task.result_file and os.path.exists(test_task.result_file):
                    report_data = executor.get_json_report_data(test_task.result_file)
                else:
                    # 构造简单报告数据
                    report_data = {
                        "summary": {
                            "total": test_task.total_cases,
                            "passed": test_task.passed_cases,
                            "failed": test_task.failed_cases
                        },
                        "error": test_task.error_message
                    }
            except TestTask.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": "任务不存在"
                }, status=404)
        
        if not report_data:
            return JsonResponse({
                "success": False,
                "message": "缺少报告数据"
            }, status=400)
        
        # AI 分析
        provider = data.get("provider", "qwen")
        analyzer = ReportAnalyzer(provider)
        analysis = analyzer.analyze_report(report_data)
        
        # 保存分析结果
        if task_id:
            try:
                test_task = TestTask.objects.get(id=task_id)
                # 更新或创建报告
                report, created = TestReport.objects.get_or_create(
                    task=test_task,
                    report_type='json',
                    defaults={'report_content': json.dumps(report_data, ensure_ascii=False)}
                )
                report.ai_analysis = analysis
                report.save()
            except:
                pass
        
        return JsonResponse({
            "success": True,
            "analysis": analysis,
            "message": "报告分析完成"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"分析失败: {str(e)}"
        }, status=500)

@require_http_methods(["GET"])
def get_script_list(request):
    """获取脚本列表"""
    try:
        scripts = TestScript.objects.all()[:50]
        script_list = []
        for s in scripts:
            script_list.append({
                "id": s.id,
                "name": s.name,
                "status": s.status,
                "created_at": s.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "has_file": bool(s.script_file)
            })
        
        return JsonResponse({
            "success": True,
            "scripts": script_list
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_task_list(request):
    """获取任务列表"""
    try:
        tasks = TestTask.objects.select_related('script').all()[:50]
        task_list = []
        for t in tasks:
            task_list.append({
                "id": t.id,
                "script_name": t.script.name if t.script else "未知",
                "status": t.status,
                "total": t.total_cases,
                "passed": t.passed_cases,
                "failed": t.failed_cases,
                "duration": t.duration,
                "executed_at": t.executed_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            "success": True,
            "tasks": task_list
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)
