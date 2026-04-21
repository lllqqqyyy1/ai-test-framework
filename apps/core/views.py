"""
核心视图 - 提供 API 接口和页面渲染
"""
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.ai_agents.test_case_generator.generator import TestCaseGenerator
from apps.core.models import TestCase

def index_view(request):
    """首页视图"""
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def generate_test_cases(request):
    """
    生成测试用例 API
    
    请求体 (JSON):
    {
        "input_type": "requirements" 或 "interface",
        "input": "需求描述或接口描述文本",
        "provider": "deepseek" 或 "qwen" (可选,默认 deepseek)
    }
    
    返回 (JSON):
    {
        "success": true/false,
        "test_cases": [...],  // 成功时返回
        "message": "错误信息"  // 失败时返回
    }
    """
    try:
        # 解析请求体
        data = json.loads(request.body)
        input_type = data.get("input_type")
        input_text = data.get("input")
        provider = data.get("provider", "deepseek")
        
        # 参数验证
        if not input_type:
            return JsonResponse({
                "success": False,
                "message": "缺少 input_type 参数 (requirements 或 interface)"
            }, status=400)
        
        if not input_text:
            return JsonResponse({
                "success": False,
                "message": "缺少 input 参数 (需求描述或接口描述)"
            }, status=400)
        
        if input_type not in ["requirements", "interface"]:
            return JsonResponse({
                "success": False,
                "message": "input_type 必须是 'requirements' 或 'interface'"
            }, status=400)
        
        # 生成测试用例
        generator = TestCaseGenerator(provider)
        
        if input_type == "requirements":
            cases = generator.generate_functional_cases(input_text)
        else:  # interface
            cases = generator.generate_interface_cases(input_text)
        
        # 返回成功响应
        return JsonResponse({
            "success": True,
            "test_cases": cases,
            "count": len(cases)
        })
        
    except ValueError as e:
        # 参数错误或解析失败
        return JsonResponse({
            "success": False,
            "message": f"参数错误: {str(e)}"
        }, status=400)
        
    except Exception as e:
        # 其他错误
        return JsonResponse({
            "success": False,
            "message": f"生成失败: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_test_case(request):
    """
    保存测试用例到数据库 API
    
    请求体 (JSON):
    {
        "test_cases": [
            {
                "title": "用例标题",
                "description": "用例描述",
                "test_steps": "测试步骤",
                "expected_results": "预期结果"
            }
        ],
        "requirements": "需求描述",
        "code_snippet": "代码片段" (可选),
        "case_type": "functional" 或 "interface",
        "priority": "high", "medium" 或 "low" (可选,默认 medium)
    }
    
    返回 (JSON):
    {
        "success": true/false,
        "message": "操作结果信息",
        "saved_count": 10  // 成功保存的数量
    }
    """
    try:
        # 解析请求体
        data = json.loads(request.body)
        test_cases = data.get("test_cases")
        requirements = data.get("requirements", "")
        code_snippet = data.get("code_snippet", "")
        case_type = data.get("case_type", "functional")
        priority = data.get("priority", "medium")
        
        # 参数验证
        if not test_cases or not isinstance(test_cases, list):
            return JsonResponse({
                "success": False,
                "message": "缺少 test_cases 参数或格式不正确"
            }, status=400)
        
        if not requirements:
            return JsonResponse({
                "success": False,
                "message": "缺少 requirements 参数"
            }, status=400)
        
        # 批量保存测试用例
        saved_count = 0
        for case in test_cases:
            TestCase.objects.create(
                title=case.get("title", "未命名用例"),
                description=case.get("description", ""),
                requirements=requirements,
                code_snippet=code_snippet,
                test_steps=case.get("test_steps", ""),
                expected_results=case.get("expected_results", ""),
                case_type=case_type,
                priority=priority
            )
            saved_count += 1
        
        # 返回成功响应
        return JsonResponse({
            "success": True,
            "message": f"成功保存 {saved_count} 个测试用例",
            "saved_count": saved_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "请求体 JSON 格式不正确"
        }, status=400)
        
    except Exception as e:
        # 数据库错误或其他异常
        return JsonResponse({
            "success": False,
            "message": f"保存失败: {str(e)}"
        }, status=500)
