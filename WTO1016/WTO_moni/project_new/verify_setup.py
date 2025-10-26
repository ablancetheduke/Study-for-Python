#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千问API配置验证脚本
验证API Key配置和系统设置是否正确

运行方法：
python verify_setup.py
"""

import os
import sys
import json

def check_api_configuration():
    """检查API配置"""
    print("[检查] 千问API配置...")
    print()

    # 检查run.py中的配置
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        runpy_path = os.path.join(script_dir, 'run.py')
        with open(runpy_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查API Key
        if 'API_KEY = "sk-8378737e0bb44d1a90cb7056af722e55"' in content:
            print("[成功] API Key配置正确")
        else:
            print("[失败] API Key配置不正确")
            return False

        # 检查API URL
        if 'API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"' in content:
            print("[成功] API端点配置正确")
        else:
            print("[失败] API端点配置不正确")
            return False

        # 检查函数名
        if 'def call_qianwen_api(' in content:
            print("[成功] API函数名正确")
        else:
            print("[失败] API函数名不正确")
            return False

    except FileNotFoundError:
        print("[失败] 找不到run.py文件")
        return False
    except Exception as e:
        print(f"[失败] 检查配置时出错: {e}")
        return False

    return True

def check_dependencies():
    """检查依赖项"""
    print("[检查] 系统依赖...")
    print()

    required_modules = [
        'flask', 'pymongo', 'requests', 'PyPDF2', 'docx',
        'jieba', 'sklearn', 'numpy', 'dateutil'
    ]

    missing_modules = []
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
            print(f"[成功] {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"[失败] {module}")

    if missing_modules:
        print(f"\n[警告] 缺少依赖模块: {', '.join(missing_modules)}")
        print("请运行: pip install -r requirements.txt")
        return False

    print("\n[成功] 所有依赖模块已安装")
    return True

def check_files():
    """检查必要文件"""
    print("[检查] 系统文件...")
    print()

    required_files = [
        'run.py',
        'app/__init__.py',
        'app/routes.py',
        'app/models.py',
        'requirements.txt'
    ]

    missing_files = []
    for file in required_files:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, file)
        if os.path.exists(file_path):
            print(f"[成功] {file}")
        else:
            missing_files.append(file)
            print(f"[失败] {file}")

    if missing_files:
        print(f"\n[失败] 缺少必要文件: {', '.join(missing_files)}")
        return False

    print("\n[成功] 所有必要文件存在")
    return True

def main():
    """主验证函数"""
    print("千问API配置验证")
    print("=" * 50)
    print()

    all_good = True

    # 检查配置
    if not check_api_configuration():
        all_good = False

    print()

    # 检查依赖
    if not check_dependencies():
        all_good = False

    print()

    # 检查文件
    if not check_files():
        all_good = False

    print()
    print("=" * 50)

    if all_good:
        print("[完成] 配置验证通过！")
        print("[成功] 系统已准备好使用千问API生成宣言")
        print()
        print("下一步：")
        print("1. 启动MongoDB数据库")
        print("2. 运行: python run.py")
        print("3. 访问浏览器开始使用WTO模拟谈判系统")
    else:
        print("[失败] 配置验证失败！")
        print("请检查上述错误并修复")

    return all_good

if __name__ == "__main__":
    main()
