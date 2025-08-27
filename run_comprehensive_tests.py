#!/usr/bin/env python3
"""
综合测试运行器
运行所有单元测试、集成测试、性能测试和边界情况测试
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(command, description=""):
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {command}")
    print('='*60)
    
    start_time = time.time()
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        elapsed_time = time.time() - start_time
        
        print(f"耗时: {elapsed_time:.2f}秒")
        
        if result.returncode == 0:
            print("✅ 成功")
            if result.stdout:
                print("输出:")
                print(result.stdout)
        else:
            print("❌ 失败")
            if result.stderr:
                print("错误:")
                print(result.stderr)
            if result.stdout:
                print("输出:")
                print(result.stdout)
        
        return result.returncode == 0, result.stdout, result.stderr
    
    except Exception as e:
        print(f"❌ 运行命令时出错: {e}")
        return False, "", str(e)

def run_test_suite():
    """运行完整的测试套件"""
    
    print("🚀 开始运行综合测试套件...")
    print(f"项目根目录: {project_root}")
    
    # 检查测试文件是否存在
    test_files = {
        "单元测试 - Alpha Vantage API": "tests/unit/test_alpha_vantage_api.py",
        "单元测试 - AI分析器": "tests/unit/test_ai_analyzer.py",
        "单元测试 - 边界情况": "tests/unit/test_edge_cases.py",
        "单元测试 - 性能测试": "tests/unit/test_performance.py",
        "集成测试 - 认证流程": "tests/integration/test_auth_flow.py",
        "集成测试 - 股票分析流程": "tests/integration/test_stock_analysis_flow.py"
    }
    
    # 检查所有测试文件
    missing_files = []
    for name, path in test_files.items():
        if not os.path.exists(path):
            missing_files.append(path)
    
    if missing_files:
        print("❌ 以下测试文件缺失:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("✅ 所有测试文件已找到")
    
    # 运行测试
    results = {}
    
    # 1. 运行单元测试
    print("\n📊 运行单元测试...")
    unit_tests = [
        ("tests/unit/test_alpha_vantage_api.py", "Alpha Vantage API单元测试"),
        ("tests/unit/test_ai_analyzer.py", "AI分析器单元测试"),
        ("tests/unit/test_edge_cases.py", "边界情况测试"),
        ("tests/unit/test_performance.py", "性能测试")
    ]
    
    for test_file, description in unit_tests:
        success, stdout, stderr = run_command(
            f"python -m pytest {test_file} -v",
            description
        )
        results[description] = success
        
        # 如果失败，显示详细信息
        if not success:
            print(f"\n📋 {description} 失败详情:")
            if stderr:
                print(stderr)
    
    # 2. 运行集成测试
    print("\n🔗 运行集成测试...")
    integration_tests = [
        ("tests/integration/test_auth_flow.py", "认证流程集成测试"),
        ("tests/integration/test_stock_analysis_flow.py", "股票分析流程集成测试")
    ]
    
    for test_file, description in integration_tests:
        success, stdout, stderr = run_command(
            f"python -m pytest {test_file} -v",
            description
        )
        results[description] = success
        
        if not success:
            print(f"\n📋 {description} 失败详情:")
            if stderr:
                print(stderr)
    
    # 3. 运行所有测试并生成报告
    print("\n📈 生成测试报告...")
    success, stdout, stderr = run_command(
        "python -m pytest tests/ -v --tb=short --durations=10",
        "完整测试套件"
    )
    
    # 4. 运行覆盖率测试
    print("\n📊 运行代码覆盖率测试...")
    coverage_success, coverage_stdout, coverage_stderr = run_command(
        "python -m pytest tests/ --cov=services --cov=app --cov-report=html --cov-report=term",
        "代码覆盖率测试"
    )
    
    # 5. 显示测试结果摘要
    print("\n" + "="*80)
    print("📋 测试结果摘要")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for test_name, success in results.items():
        if success:
            print(f"✅ {test_name}")
            passed += 1
        else:
            print(f"❌ {test_name}")
            failed += 1
    
    print(f"\n📊 总计: {passed + failed} 个测试套件")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    
    if failed > 0:
        print("\n❗ 有测试失败，请查看上面的详细信息")
        return False
    
    print("\n🎉 所有测试通过!")
    
    # 6. 显示覆盖率报告
    if coverage_success and coverage_stdout:
        print("\n📊 代码覆盖率报告:")
        lines = coverage_stdout.split('\n')
        for line in lines:
            if 'TOTAL' in line or any(service in line for service in ['services/', 'app/']):
                print(line)
    
    return True

def main():
    """主函数"""
    try:
        success = run_test_suite()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 运行测试时发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
