#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WTO会议系统快速部署脚本

运行方法：
python setup.py

功能：
1. 检查并安装依赖
2. 创建.env文件
3. 验证配置
4. 启动系统
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """运行命令并显示描述"""
    print(f"\n[INFO] {description}")
    print(f"[CMD] {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description}失败")
        print(f"错误信息: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    print("\n[INFO] 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"[SUCCESS] Python版本: {version.major}.{version.minor} (符合要求)")
        return True
    else:
        print(f"[ERROR] Python版本: {version.major}.{version.minor} (需要Python 3.7+)")
        return False

def install_dependencies():
    """安装依赖包"""
    return run_command(
        "pip install -r requirements.txt",
        "安装Python依赖包"
    )

def create_env_file():
    """创建.env文件"""
    print("\n[INFO] 创建.env配置文件...")

    env_file = Path('.env')
    if env_file.exists():
        print(f"[INFO] .env文件已存在: {env_file.absolute()}")
        return True

    # 复制模板文件
    template_file = Path('.env.example')
    if not template_file.exists():
        print(f"[ERROR] 模板文件不存在: {template_file.absolute()}")
        return False

    try:
        import shutil
        shutil.copy(template_file, env_file)
        print(f"[SUCCESS] 已创建.env文件: {env_file.absolute()}")
        print(f"[WARNING] 请编辑.env文件，填入您的实际配置信息！")
        return True
    except Exception as e:
        print(f"[ERROR] 创建.env文件失败: {e}")
        return False

def verify_configuration():
    """验证配置"""
    print("\n[INFO] 验证系统配置...")
    try:
        result = subprocess.run([sys.executable, 'verify_config.py'], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("[SUCCESS] 配置验证通过")
            return True
        else:
            print("[WARNING] 配置验证发现问题，请根据提示修复")
            return False
    except Exception as e:
        print(f"[ERROR] 配置验证失败: {e}")
        return False

def start_system():
    """启动系统"""
    print("\n[INFO] 启动WTO会议系统...")
    print("[INFO] 系统将在 http://127.0.0.1:5000 启动")
    print("[INFO] 按Ctrl+C停止系统")
    print("[INFO] 启动日志:")
    print("=" * 50)

    try:
        # 启动Flask应用
        subprocess.run([sys.executable, 'run.py'], check=True)
    except KeyboardInterrupt:
        print("\n[INFO] 系统已停止")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] 系统启动失败: {e}")

def main():
    """主函数"""
    print("WTO会议系统快速部署工具")
    print("=" * 50)

    steps = [
        check_python_version,
        install_dependencies,
        create_env_file,
        verify_configuration
    ]

    success_count = 0
    for step in steps:
        if step():
            success_count += 1
        else:
            print(f"\n[WARNING] 步骤失败，但继续执行...")

    print(f"\n{"=" * 50}")
    print(f"部署完成: {success_count}/{len(steps)} 步骤成功")

    if success_count == len(steps):
        print("所有步骤完成！准备启动系统...")
        start_system()
    else:
        print("部分步骤失败，请检查上述错误信息")
        print("修复问题后，可以重新运行: python setup.py")
        print("或者手动启动系统: python run.py")

if __name__ == '__main__':
    main()
