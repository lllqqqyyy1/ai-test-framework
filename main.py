#!/usr/bin/env python
"""
Django development server starter
启动端口: 9002
"""
import os
import sys


def main():
    """启动 Django 开发服务器"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入 Django。请确认已安装 Django 并激活虚拟环境。"
        ) from exc
    
    # 默认端口 9002
    port = sys.argv[1] if len(sys.argv) > 1 else '9002'
    
    print(f"正在启动 Django 开发服务器...")
    print(f"访问地址: http://127.0.0.1:{port}")
    print(f"按 CONTROL-C 停止服务器")
    
    execute_from_command_line([sys.argv[0], 'runserver', f'0.0.0.0:{port}'])


if __name__ == '__main__':
    main()
