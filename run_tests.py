#!/usr/bin/env python3
"""测试运行器"""
import os
import sys
import subprocess
import argparse

def run_tests(test_type=None, verbose=False, coverage=False):
    """运行测试"""
    # 确保测试依赖已安装
    print("检查测试依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "tests/test_requirements.txt"], 
                   check=True)
    
    # 构建pytest命令
    cmd = ["python", "-m", "pytest"]
    
    if test_type:
        if test_type == "unit":
            cmd.append("tests/unit")
        elif test_type == "integration":
            cmd.append("tests/integration")
        elif test_type == "all":
            cmd.append("tests")
    else:
        cmd.append("tests")
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov=services", "--cov-report=html", "--cov-report=term"])
    
    # 运行测试
    print(f"运行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="运行股票分析系统测试")
    parser.add_argument("--type", choices=["unit", "integration", "all"], 
                       help="测试类型")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="详细输出")
    parser.add_argument("--coverage", action="store_true",
                       help="生成覆盖率报告")
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ["TESTING"] = "true"
    
    # 运行测试
    exit_code = run_tests(args.type, args.verbose, args.coverage)
    
    # 清理
    if os.path.exists("test.db"):
        os.remove("test.db")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
