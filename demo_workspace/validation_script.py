#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
14天测试工程师急救计划 - 验收检查脚本
自动验证Day 1/4/6/9的关键产出

使用方法:
    python validation_script.py --day 1  # 验证Day 1
    python validation_script.py --day 4  # 验证Day 4
    python validation_script.py --day 6  # 验证Day 6
    python validation_script.py --day 9  # 验证Day 9
    python validation_script.py --all    # 验证所有天数
"""

import os
import sys
import argparse
import subprocess
import importlib.util
from pathlib import Path


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(title):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_success(msg):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")


def print_error(msg):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")


def print_warning(msg):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")


def print_info(msg):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")


def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description}不存在: {filepath}")
        return False


def check_module_installed(module_name, description):
    """检查Python模块是否安装"""
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        print_success(f"{description}已安装: {module_name}")
        return True
    else:
        print_error(f"{description}未安装: {module_name}")
        print_info(f"安装命令: pip install {module_name}")
        return False


def validate_day1():
    """验证Day 1产出"""
    print_header("Day 1 验收: 基础保命 - 函数封装与异常处理")

    passed = 0
    total = 5

    # 检查1: requests模块安装
    if check_module_installed('requests', 'requests库'):
        passed += 1

    # 检查2: 查找包含safe_request函数的文件
    py_files = list(Path('.').glob('*.py'))
    found_safe_request = False
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'def safe_request' in content:
                    print_success(f"找到safe_request函数: {py_file}")
                    found_safe_request = True
                    passed += 1

                    # 检查异常处理
                    if 'try:' in content and 'except' in content:
                        print_success("代码包含try-except异常处理")
                        passed += 1
                    else:
                        print_error("代码缺少try-except异常处理")

                    # 检查重试逻辑
                    if 'for' in content and 'range' in content:
                        print_success("代码包含重试循环")
                        passed += 1
                    else:
                        print_error("代码缺少重试循环")
                    break
        except:
            pass

    if not found_safe_request:
        print_error("未找到safe_request函数，请创建包含该函数的Python文件")

    # 检查3: 日志报告文件
    report_files = list(Path('.').glob('*report*.txt')) + list(Path('.').glob('*log*.txt'))
    if report_files:
        print_success(f"找到报告文件: {report_files[0]}")
        passed += 1
    else:
        print_error("未找到报告文件(.txt)，请确保生成包含统计信息的txt报告")

    print(f"\n{Colors.BOLD}Day 1 验收结果: {passed}/{total} 项通过{Colors.RESET}")
    return passed == total


def validate_day4():
    """验证Day 4产出"""
    print_header("Day 4 验收: 配置表校验 - pandas核心技能")

    passed = 0
    total = 5

    # 检查1: pandas安装
    if check_module_installed('pandas', 'pandas库'):
        passed += 1

    # 检查2: openpyxl安装
    if check_module_installed('openpyxl', 'openpyxl库'):
        passed += 1

    # 检查3: 查找配置表检查函数
    py_files = list(Path('.').glob('*.py'))
    found_check_func = False
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'check_level_continuity' in content or 'check_config' in content:
                    print_success(f"找到配置表检查函数: {py_file}")
                    found_check_func = True
                    passed += 1

                    # 检查pandas使用
                    if 'pd.read_excel' in content or 'pandas' in content:
                        print_success("代码使用pandas读取Excel")
                        passed += 1
                    else:
                        print_error("代码未使用pandas读取Excel")

                    # 检查shift或groupby使用
                    if 'shift(' in content or 'groupby' in content:
                        print_success("代码使用shift或groupby进行数据分析")
                        passed += 1
                    else:
                        print_error("代码未使用shift/groupby")
                    break
        except:
            pass

    if not found_check_func:
        print_error("未找到配置表检查函数")
        print_info("请创建包含check_level_continuity或check_config函数的文件")

    # 检查4: 测试Excel文件
    excel_files = list(Path('.').glob('*.xlsx')) + list(Path('.').glob('*.xls'))
    if excel_files:
        print_success(f"找到Excel文件: {excel_files[0]}")
    else:
        print_warning("未找到Excel测试文件，建议创建用于测试的配置表")

    print(f"\n{Colors.BOLD}Day 4 验收结果: {passed}/{total} 项通过{Colors.RESET}")
    return passed >= 4  # 允许一项不通过


def validate_day6():
    """验证Day 6产出"""
    print_header("Day 6 验收: 数据库 - MySQL与一致性校验")

    passed = 0
    total = 5

    # 检查1: pymysql安装
    if check_module_installed('pymysql', 'pymysql库'):
        passed += 1

    # 检查2: 查找数据库检查函数
    py_files = list(Path('.').glob('*.py'))
    found_db_func = False
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'check_db_consistency' in content or 'pymysql.connect' in content:
                    print_success(f"找到数据库操作代码: {py_file}")
                    found_db_func = True
                    passed += 1

                    # 检查连接配置
                    if 'host' in content and 'user' in content:
                        print_success("代码包含数据库连接配置")
                        passed += 1
                    else:
                        print_error("代码缺少数据库连接配置")

                    # 检查参数化查询
                    if '%s' in content or 'params' in content:
                        print_success("代码使用参数化查询(防SQL注入)")
                        passed += 1
                    else:
                        print_warning("建议添加参数化查询防止SQL注入")

                    # 检查with语句
                    if 'with' in content and 'cursor' in content:
                        print_success("代码使用with语句管理cursor")
                        passed += 1
                    else:
                        print_warning("建议使用with语句管理cursor")
                    break
        except:
            pass

    if not found_db_func:
        print_error("未找到数据库操作代码")
        print_info("请创建包含pymysql连接和查询的Python文件")

    # 检查3: MySQL/Docker
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=5)
        if 'mysql' in result.stdout.lower():
            print_success("Docker中有MySQL容器在运行")
        else:
            print_warning("Docker中未找到MySQL容器，可使用以下命令启动:")
            print_info("docker run -e MYSQL_ROOT_PASSWORD=123456 -p 3306:3306 mysql:5.7")
    except:
        print_warning("无法检查Docker状态，请确保MySQL可用")

    print(f"\n{Colors.BOLD}Day 6 验收结果: {passed}/{total} 项通过{Colors.RESET}")
    return passed >= 3


def validate_day9():
    """验证Day 9产出"""
    print_header("Day 9 验收: 压测实战 - JMeter性能测试")

    passed = 0
    total = 4

    # 检查1: JMeter安装
    jmeter_paths = [
        'C:/apache-jmeter/bin/jmeter.bat',
        '/usr/local/bin/jmeter',
        '/opt/apache-jmeter/bin/jmeter',
    ]
    jmeter_found = False
    for path in jmeter_paths:
        if os.path.exists(path):
            print_success(f"找到JMeter: {path}")
            jmeter_found = True
            passed += 1
            break

    if not jmeter_found:
        # 尝试命令行
        try:
            result = subprocess.run(['jmeter', '--version'], capture_output=True, text=True, timeout=5)
            if 'Apache JMeter' in result.stdout:
                print_success("JMeter已安装并可用")
                jmeter_found = True
                passed += 1
        except:
            pass

    if not jmeter_found:
        print_error("未找到JMeter，请下载安装")
        print_info("下载地址: https://jmeter.apache.org/download_jmeter.cgi")

    # 检查2: JMeter测试计划文件
    jmx_files = list(Path('.').glob('*.jmx'))
    if jmx_files:
        print_success(f"找到JMeter测试计划: {jmx_files[0]}")
        passed += 1
    else:
        print_error("未找到JMeter测试计划文件(.jmx)")
        print_info("请创建包含HTTP请求、线程组、CSV数据源的测试计划")

    # 检查3: CSV数据文件
    csv_files = list(Path('.').glob('*.csv'))
    if csv_files:
        print_success(f"找到CSV数据文件: {csv_files[0]}")
        passed += 1
    else:
        print_warning("未找到CSV数据文件，JMeter测试通常需要CSV数据源")

    # 检查4: 压测结果报告
    result_files = list(Path('.').glob('*result*.jtl')) + list(Path('.').glob('*report*'))
    if result_files:
        print_success(f"找到压测结果文件")
        passed += 1
    else:
        print_warning("未找到压测结果文件，运行压测后会生成.jtl或HTML报告")

    print(f"\n{Colors.BOLD}Day 9 验收结果: {passed}/{total} 项通过{Colors.RESET}")
    print_info("压测关键指标: Throughput(吞吐量), Error%(错误率), P90/P95(延迟百分位)")
    return passed >= 2


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='14天测试工程师急救计划验收脚本')
    parser.add_argument('--day', type=int, choices=[1, 4, 6, 9], help='验证指定天数')
    parser.add_argument('--all', action='store_true', help='验证所有天数')
    args = parser.parse_args()

    print(f"{Colors.BOLD}{Colors.GREEN}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     14天测试工程师急救计划 - 验收检查脚本                    ║")
    print("║     西安市场适配版                                          ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

    results = {}

    if args.all:
        results['Day 1'] = validate_day1()
        results['Day 4'] = validate_day4()
        results['Day 6'] = validate_day6()
        results['Day 9'] = validate_day9()
    elif args.day == 1:
        results['Day 1'] = validate_day1()
    elif args.day == 4:
        results['Day 4'] = validate_day4()
    elif args.day == 6:
        results['Day 6'] = validate_day6()
    elif args.day == 9:
        results['Day 9'] = validate_day9()
    else:
        parser.print_help()
        return

    # 总结
    print_header("验收总结")
    for day, passed in results.items():
        status = f"{Colors.GREEN}通过" if passed else f"{Colors.RED}未通过"
        print(f"{day}: {status}{Colors.RESET}")

    all_passed = all(results.values())
    if all_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 恭喜！所有验收项已通过！{Colors.RESET}")
        print(f"{Colors.GREEN}你已经具备了西安测试岗位的核心竞争力！{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ 部分验收项未通过，请根据提示完善{Colors.RESET}")
        print(f"{Colors.YELLOW}继续加油，你离目标已经很近了！{Colors.RESET}")


if __name__ == '__main__':
    main()
