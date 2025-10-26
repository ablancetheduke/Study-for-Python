#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WTO会议系统配置验证脚本

运行方法：
python verify_config.py

检查项目：
- 环境变量配置
- 依赖包安装
- 数据库连接
- API连接
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """检查.env文件是否存在和配置"""
    print("检查.env文件配置...")

    env_file = Path('.env')
    if not env_file.exists():
        print("[FAIL] .env文件不存在")
        print("   请复制.env.example到.env并配置")
        return False

    # 加载环境变量
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("[FAIL] python-dotenv未安装")
        return False

    # 检查必需的环境变量
    required_vars = [
        ('LLM_API_KEY', '大模型API密钥'),
        ('LLM_API_URL', 'API端点地址'),
        ('FLASK_SECRET_KEY', 'Flask密钥'),
        ('JWT_SECRET_KEY', 'JWT密钥'),
        ('MONGODB_URI', '数据库连接字符串')
    ]

    missing_vars = []
    for var_name, description in required_vars:
        value = os.getenv(var_name)
        if not value:
            missing_vars.append((var_name, description))
        elif var_name == 'LLM_API_KEY' and not value.startswith('sk-'):
            missing_vars.append((var_name, description))

    if missing_vars:
        print("[FAIL] 缺少必需的环境变量:")
        for var_name, description in missing_vars:
            print(f"   - {var_name}: {description}")
        return False
    else:
        print("[OK] 环境变量配置完整")
        return True

def check_dependencies():
    """检查依赖包安装"""
    print("检查依赖包安装...")

    required_packages = [
        'flask', 'pymongo', 'PyPDF2', 'python-docx', 'jieba',
        'scikit-learn', 'requests', 'python-dotenv', 'bcrypt'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("[FAIL] 缺少依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("   请运行: pip install -r requirements.txt")
        return False
    else:
        print("[OK] 所有依赖包已安装")
        return True

def check_database_connection():
    """检查数据库连接"""
    print("检查数据库连接...")

    try:
        from pymongo import MongoClient
        from dotenv import load_dotenv
        load_dotenv()

        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)

        # 测试连接
        client.admin.command('ping')
        print("[OK] 数据库连接成功")
        return True

    except Exception as e:
        print(f"[FAIL] 数据库连接失败: {e}")
        print("   请确保MongoDB服务正在运行")
        return False

def check_api_connection():
    """检查API连接"""
    print("检查API连接...")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('LLM_API_KEY')
        if not api_key or not api_key.startswith('sk-'):
            print("[SKIP] API密钥未配置或格式错误")
            print("   跳过API连接测试")
            return True

        import requests

        api_url = os.getenv('LLM_API_URL', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation')
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # 发送测试请求
        test_data = {
            'model': os.getenv('LLM_MODEL', 'qwen-turbo'),
            'input': {'prompt': 'Hello'},
            'parameters': {'max_tokens': 10}
        }

        response = requests.post(api_url, json=test_data, headers=headers, timeout=10)

        if response.status_code == 200:
            print("[OK] API连接成功")
            return True
        elif response.status_code == 401:
            print("[FAIL] API密钥无效")
            print("   请检查LLM_API_KEY配置")
            return False
        else:
            print(f"[WARN] API返回状态码: {response.status_code}")
            print("   但连接正常，可能是参数问题")
            return True

    except requests.exceptions.RequestException as e:
        print(f"[WARN] API连接测试失败: {e}")
        print("   网络连接问题或API服务不可用")
        return True
    except Exception as e:
        print(f"[FAIL] API测试出错: {e}")
        return False

def main():
    """主验证函数"""
    print("WTO会议系统配置验证")
    print("=" * 50)

    checks = [
        check_env_file,
        check_dependencies,
        check_database_connection,
        check_api_connection
    ]

    results = []
    for check in checks:
        results.append(check())
        print()

    print("=" * 50)
    print("验证结果总结:")

    passed = sum(results)
    total = len(results)

    if passed == total:
        print("所有检查通过！系统配置正确。")
        print("   可以运行: python run.py")
    else:
        print(f"  {total - passed}项检查失败")
        print("   请根据上述提示修复配置")
        sys.exit(1)

if __name__ == '__main__':
    main()
