"""
自动化测试执行引擎
基于 pytest 框架执行 AI 生成的测试脚本,生成标准化测试报告
"""
import os
import sys
import subprocess
import json
import time
from pathlib import Path
from django.conf import settings

class TestExecutor:
    """自动化测试执行器 - 封装 pytest 测试执行逻辑"""
    
    def __init__(self, base_dir=None):
        """
        初始化执行器
        
        Args:
            base_dir: 项目基础目录,默认为 settings.BASE_DIR
        """
        self.base_dir = base_dir or settings.BASE_DIR
        self.test_scripts_dir = self.base_dir / 'test_scripts'
        self.test_reports_dir = self.base_dir / 'test_reports'
        
        # 确保目录存在
        self.test_scripts_dir.mkdir(exist_ok=True)
        self.test_reports_dir.mkdir(exist_ok=True)
    
    def save_script(self, script_name, script_content):
        """
        保存测试脚本到文件
        
        Args:
            script_name: 脚本名称
            script_content: 脚本内容
            
        Returns:
            str: 脚本文件路径
        """
        # 清理文件名
        safe_name = "".join(c for c in script_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name}_{int(time.time())}.py"
        filepath = self.test_scripts_dir / filename
        
        # 写入脚本
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return str(filepath)
    
    def execute_test(self, script_path, report_name="test_report"):
        """
        执行 pytest 测试
        
        Args:
            script_path: 测试脚本路径
            report_name: 报告名称
            
        Returns:
            dict: 执行结果 {
                'success': bool,
                'total': int,
                'passed': int,
                'failed': int,
                'error': str,
                'report_path': str,
                'json_path': str,
                'duration': float
            }
        """
        start_time = time.time()
        
        try:
            # 确保脚本存在
            if not os.path.exists(script_path):
                return {
                    'success': False,
                    'error': f'测试脚本不存在: {script_path}'
                }
            
            # 生成报告文件路径
            timestamp = int(time.time())
            html_report = self.test_reports_dir / f"{report_name}_{timestamp}.html"
            json_report = self.test_reports_dir / f"{report_name}_{timestamp}.json"
            
            # 构建 pytest 命令
            cmd = [
                sys.executable,  # 使用当前 Python 解释器
                '-m', 'pytest',
                script_path,
                '-v',  # 详细输出
                f'--html={html_report}',  # HTML 报告
                '--self-contained-html',  # 独立 HTML
                f'--json={json_report}',  # JSON 报告
                '--tb=short',  # 简短的 traceback
            ]
            
            # 执行测试
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                cwd=str(self.base_dir)
            )
            
            duration = time.time() - start_time
            
            # 解析结果
            return self._parse_test_result(
                result,
                str(html_report),
                str(json_report),
                duration
            )
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '测试执行超时(5分钟)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'执行异常: {str(e)}'
            }
    
    def _parse_test_result(self, process_result, html_report, json_report, duration):
        """
        解析测试结果
        
        Args:
            process_result: subprocess.CompletedProcess 对象
            html_report: HTML 报告路径
            json_report: JSON 报告路径
            duration: 执行时长
            
        Returns:
            dict: 解析后的结果
        """
        import re
        
        # 默认结果
        result = {
            'success': process_result.returncode == 0,
            'total': 0,
            'passed': 0,
            'failed': 0,
            'error': process_result.stderr if process_result.returncode != 0 else '',
            'report_path': html_report if os.path.exists(html_report) else '',
            'json_path': json_report if os.path.exists(json_report) else '',
            'duration': duration
        }
        
        # 方法 1: 从 stdout 解析 pytest 输出 (最可靠)
        try:
            output = process_result.stdout + '\n' + process_result.stderr
            
            # 匹配 pytest 输出格式: "10 passed, 2 failed, 1 warning in 1.23s"
            # 或 "16 failed in 2.34s"
            # 或 "3 passed, 13 failed in 1.45s"
            
            passed_match = re.search(r'(\d+)\s+passed', output)
            failed_match = re.search(r'(\d+)\s+failed', output)
            error_match = re.search(r'(\d+)\s+error', output)
            skipped_match = re.search(r'(\d+)\s+skipped', output)
            
            if passed_match:
                result['passed'] = int(passed_match.group(1))
            if failed_match:
                result['failed'] = int(failed_match.group(1))
            if error_match:
                # errors 也算失败
                result['failed'] += int(error_match.group(1))
            
            result['total'] = result['passed'] + result['failed']
            
            # 如果解析成功,直接返回
            if result['total'] > 0:
                print(f"从 stdout 解析结果: {result['total']} total, {result['passed']} passed, {result['failed']} failed")
                return result
                
        except Exception as e:
            print(f"从 stdout 解析失败: {e}")
        
        # 方法 2: 尝试从 JSON 报告解析
        if os.path.exists(json_report):
            try:
                with open(json_report, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                print(f"JSON 报告格式: {list(json_data.keys())}")
                    
                # 解析 pytest-json 格式
                if 'summary' in json_data:
                    result['total'] = json_data['summary'].get('total', 0)
                    result['passed'] = json_data['summary'].get('passed', 0)
                    result['failed'] = json_data['summary'].get('failed', 0)
                    print(f"从 JSON summary 解析: {result}")
                    
                # 解析其他 JSON 格式 (tests 数组)
                elif 'tests' in json_data:
                    result['total'] = len(json_data['tests'])
                    result['passed'] = sum(1 for t in json_data['tests'] if t.get('outcome') == 'passed')
                    result['failed'] = sum(1 for t in json_data['tests'] if t.get('outcome') == 'failed')
                    print(f"从 JSON tests 数组解析: {result}")
                    
                # 其他可能的格式
                elif 'collectors' in json_data:
                    # pytest-reportlog 格式
                    tests = [item for item in json_data.get('test_reports', [])]
                    result['total'] = len(tests)
                    result['passed'] = sum(1 for t in tests if t.get('outcome') == 'passed')
                    result['failed'] = sum(1 for t in tests if t.get('outcome') == 'failed')
                    print(f"从 JSON test_reports 解析: {result}")
                    
            except Exception as e:
                print(f"JSON 报告解析失败: {e}")
                result['error'] += f'\n解析 JSON 报告失败: {str(e)}'
        
        # 如果所有方法都失败,尝试从 collected 信息解析
        if result['total'] == 0:
            try:
                output = process_result.stdout
                # 匹配 "collected 16 items"
                collected_match = re.search(r'collected\s+(\d+)\s+items?', output)
                if collected_match:
                    result['total'] = int(collected_match.group(1))
                    print(f"从 collected 信息解析: {result['total']} items")
            except:
                pass
        
        return result
    
    def get_report_content(self, report_path):
        """
        读取报告内容
        
        Args:
            report_path: 报告文件路径
            
        Returns:
            str: 报告内容
        """
        if not os.path.exists(report_path):
            return ''
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ''
    
    def get_json_report_data(self, json_path):
        """
        读取 JSON 报告数据(用于 AI 分析)
        
        Args:
            json_path: JSON 报告路径
            
        Returns:
            dict: JSON 报告数据
        """
        if not os.path.exists(json_path):
            return {}
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
