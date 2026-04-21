"""
Allure报告解析器
解析Allure测试结果,提取失败用例信息
"""
import json
import os
from pathlib import Path


class AllureReportParser:
    """Allure报告解析器"""
    
    def parse_allure_results(self, results_dir):
        """
        解析Allure结果文件
        
        Args:
            results_dir: allure-results目录路径
            
        Returns:
            dict: {
                'total': 总数,
                'passed': 通过数,
                'failed': 失败数,
                'broken': 中断数,
                'tests': 测试列表
            }
        """
        results_path = Path(results_dir)
        if not results_path.exists():
            raise FileNotFoundError(f"Allure结果目录不存在: {results_dir}")
        
        test_results = []
        
        # 解析所有result.json文件
        for result_file in results_path.glob('*-result.json'):
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
                
                test_info = self._parse_test_result(result_data)
                test_results.append(test_info)
                
            except Exception as e:
                print(f"解析文件失败 {result_file}: {e}")
        
        # 统计数据
        stats = {
            'total': len(test_results),
            'passed': sum(1 for t in test_results if t['status'] == 'passed'),
            'failed': sum(1 for t in test_results if t['status'] == 'failed'),
            'broken': sum(1 for t in test_results if t['status'] == 'broken'),
            'skipped': sum(1 for t in test_results if t['status'] == 'skipped'),
            'tests': test_results
        }
        
        return stats
    
    def _parse_test_result(self, result_data):
        """解析单个测试结果"""
        # 计算持续时间(毫秒转秒)
        start = result_data.get('start', 0)
        stop = result_data.get('stop', 0)
        duration = (stop - start) / 1000 if start and stop else 0
        
        # 提取状态详情
        status_details = result_data.get('statusDetails', {})
        
        return {
            'name': result_data.get('name', 'Unknown'),
            'status': result_data.get('status', 'unknown'),
            'error_message': status_details.get('message', ''),
            'error_trace': status_details.get('trace', ''),
            'duration': duration,
            'steps': self._parse_steps(result_data.get('steps', [])),
            'attachments': result_data.get('attachments', []),
            'labels': result_data.get('labels', []),
            'start': start,
            'stop': stop
        }
    
    def _parse_steps(self, steps):
        """解析测试步骤"""
        parsed_steps = []
        
        for step in steps:
            parsed_step = {
                'name': step.get('name', ''),
                'status': step.get('status', 'unknown'),
                'duration': (step.get('stop', 0) - step.get('start', 0)) / 1000,
            }
            
            # 递归解析子步骤
            if 'steps' in step:
                parsed_step['sub_steps'] = self._parse_steps(step['steps'])
            
            # 提取错误信息
            if step.get('statusDetails'):
                parsed_step['error'] = step['statusDetails'].get('message', '')
            
            parsed_steps.append(parsed_step)
        
        return parsed_steps
    
    def extract_failed_tests(self, parsed_data):
        """
        提取失败的测试用例
        
        Args:
            parsed_data: parse_allure_results返回的数据
            
        Returns:
            list: 失败用例列表
        """
        failed_tests = []
        
        for test in parsed_data['tests']:
            if test['status'] in ['failed', 'broken']:
                failed_info = {
                    'name': test['name'],
                    'status': test['status'],
                    'error_message': test['error_message'],
                    'error_trace': test['error_trace'],
                    'steps': self._extract_failed_steps(test['steps']),
                    'duration': test['duration'],
                    'attachments': test.get('attachments', [])
                }
                failed_tests.append(failed_info)
        
        return failed_tests
    
    def _extract_failed_steps(self, steps):
        """提取失败的步骤"""
        failed_steps = []
        
        for step in steps:
            if step.get('status') in ['failed', 'broken']:
                failed_step = {
                    'name': step.get('name', ''),
                    'status': step.get('status'),
                    'error': step.get('error', ''),
                    'duration': step.get('duration', 0)
                }
                failed_steps.append(failed_step)
            
            # 递归检查子步骤
            if 'sub_steps' in step:
                failed_steps.extend(self._extract_failed_steps(step['sub_steps']))
        
        return failed_steps
    
    def get_test_summary(self, parsed_data):
        """
        获取测试摘要
        
        Args:
            parsed_data: parse_allure_results返回的数据
            
        Returns:
            str: 格式化的测试摘要
        """
        total = parsed_data['total']
        passed = parsed_data['passed']
        failed = parsed_data['failed']
        broken = parsed_data['broken']
        skipped = parsed_data.get('skipped', 0)
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        summary = f"""## 测试摘要

- **总用例数**: {total}
- **通过**: {passed}
- **失败**: {failed}
- **中断**: {broken}
- **跳过**: {skipped}
- **通过率**: {pass_rate:.2f}%
"""
        
        return summary
