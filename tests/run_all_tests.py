#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polytool测试套件
===============

运行所有测试脚本
"""

import asyncio
import sys
import os
import subprocess
from pathlib import Path


def run_test_script(script_path):
    """运行单个测试脚本"""
    try:
        print(f"🧪 运行测试: {script_path}")
        
        # 设置环境变量以支持UTF-8编码
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"✅ {script_path.name} - 测试通过")
            return True
        else:
            print(f"❌ {script_path.name} - 测试失败")
            # 只显示关键错误信息，避免编码问题
            if result.stderr:
                error_lines = result.stderr.strip().split('\n')
                print(f"错误信息: {error_lines[-1] if error_lines else '未知错误'}")
            return False
            
    except Exception as e:
        print(f"❌ {script_path.name} - 运行出错: {e}")
        return False


def main():
    """运行所有测试"""
    print("🚀 Polytool测试套件")
    print("=" * 50)
    
    # 获取测试目录
    test_dir = Path(__file__).parent
    
    # 查找所有py文件，排除特定文件
    all_py_files = list(test_dir.glob("*.py"))
    test_files = [
        f for f in all_py_files 
        if f.name not in ["__init__.py", "run_all_tests.py"]
    ]
    
    if not test_files:
        print("⚠️  未找到测试文件")
        return
    
    print(f"📋 找到 {len(test_files)} 个测试文件:")
    for test_file in test_files:
        print(f"   • {test_file.name}")
    
    print("\n🧪 开始执行测试...")
    print("-" * 30)
    
    # 运行所有测试
    passed = 0
    failed = 0
    
    for test_file in test_files:
        if run_test_script(test_file):
            passed += 1
        else:
            failed += 1
        print()  # 空行分隔
    
    # 总结
    print("=" * 50)
    print(f"📊 测试结果总结:")
    print(f"   ✅ 通过: {passed}")
    print(f"   ❌ 失败: {failed}")
    print(f"   📈 总计: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有测试都通过了！")
        sys.exit(0)
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()