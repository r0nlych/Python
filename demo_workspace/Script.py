
# -*- coding: utf-8 -*-
"""
14天测试工程师急救计划 - 代码作业整合版
====================================
说明：
1. 本文件按 Day1 ~ Day14 整合为一个 Python 文件，便于你统一保存、查看、导出。
2. 重点覆盖你 Notion 里已经能确认到的内容：
   - safe_request
   - test_api(url, data)
   - validation_script 按天验收思路
   - code_templates 风格的测试练习
3. 文件里尽量都写了中文注释，便于面试前快速复习。
4. 运行环境：Python 3.10+，需要 requests、pandas（可选）
"""

from __future__ import annotations

import csv
import json
import time
import hashlib
import statistics
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError as exc:
    raise SystemExit("请先安装 requests：pip install requests") from exc

try:
    import pandas as pd
except ImportError:
    pd = None


# ============================================================
# 通用数据结构
# ============================================================

@dataclass
class ApiResult:
    """保存一次接口调用结果。"""
    ok: bool
    url: str
    method: str
    status_code: Optional[int]
    elapsed_ms: Optional[float]
    response_json: Optional[Dict[str, Any]]
    response_text: str
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# Day 1：requests 基础 + test_api(url, data)
# ============================================================

def test_api(url: str, data: Optional[Dict[str, Any]] = None) -> ApiResult:
    """
    Day 1 练习：
    将现有 requests 代码改写为函数：def test_api(url, data)

    功能：
    1. 向指定 url 发起 POST 请求
    2. 自动统计耗时
    3. 尝试解析 JSON
    4. 返回统一结构，便于后续批量测试/分析
    """
    start = time.time()

    try:
        response = requests.post(url, json=data, timeout=10)
        elapsed_ms = round((time.time() - start) * 1000, 2)

        # 尝试解析 JSON
        try:
            response_json = response.json()
        except ValueError:
            response_json = None

        return ApiResult(
            ok=response.ok,
            url=url,
            method="POST",
            status_code=response.status_code,
            elapsed_ms=elapsed_ms,
            response_json=response_json,
            response_text=response.text[:1000],  # 避免过长
            error=""
        )

    except requests.RequestException as e:
        elapsed_ms = round((time.time() - start) * 1000, 2)
        return ApiResult(
            ok=False,
            url=url,
            method="POST",
            status_code=None,
            elapsed_ms=elapsed_ms,
            response_json=None,
            response_text="",
            error=str(e)
        )


# ============================================================
# Day 2：异常处理 + safe_request
# ============================================================

def safe_request(
    method: str,
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10,
    retries: int = 3,
    retry_interval: float = 1.0,
) -> ApiResult:
    """
    Day 2 练习：
    将 requests 请求封装成安全请求函数。

    设计思路：
    1. 统一入口
    2. 支持 GET / POST
    3. 失败自动重试
    4. 返回标准结构，便于统计
    """
    method = method.upper()
    last_error = ""

    for attempt in range(1, retries + 1):
        start = time.time()

        try:
            if method == "GET":
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout
                )
            elif method == "POST":
                response = requests.post(
                    url,
                    json=json_data,
                    headers=headers,
                    timeout=timeout
                )
            else:
                raise ValueError(f"不支持的请求方法: {method}")

            elapsed_ms = round((time.time() - start) * 1000, 2)

            try:
                response_json = response.json()
            except ValueError:
                response_json = None

            return ApiResult(
                ok=response.ok,
                url=url,
                method=method,
                status_code=response.status_code,
                elapsed_ms=elapsed_ms,
                response_json=response_json,
                response_text=response.text[:1000],
                error=""
            )

        except Exception as e:
            last_error = f"第{attempt}次请求失败: {e}"
            if attempt < retries:
                time.sleep(retry_interval)

    return ApiResult(
        ok=False,
        url=url,
        method=method,
        status_code=None,
        elapsed_ms=None,
        response_json=None,
        response_text="",
        error=last_error
    )


# ============================================================
# Day 3：接口断言
# ============================================================

def assert_status_code(result: ApiResult, expected_code: int) -> bool:
    """校验 HTTP 状态码。"""
    return result.status_code == expected_code


def assert_json_key_exists(result: ApiResult, key: str) -> bool:
    """校验返回 JSON 中是否存在某个 key。"""
    return bool(result.response_json and key in result.response_json)


def assert_json_value(result: ApiResult, key: str, expected_value: Any) -> bool:
    """校验 JSON 某个字段值是否等于预期。"""
    if not result.response_json:
        return False
    return result.response_json.get(key) == expected_value


def run_basic_assertions(result: ApiResult) -> Dict[str, bool]:
    """
    对接口结果做一组基础断言。
    这里是通用模板，你后续可以按项目接口自行扩展。
    """
    checks = {
        "status_code_is_200": assert_status_code(result, 200),
        "response_time_under_2000ms": (
            result.elapsed_ms is not None and result.elapsed_ms < 2000
        ),
    }

    # 如果是 JSON，就补一个“是否能解析”的检查
    checks["json_parsed"] = result.response_json is not None

    return checks


# ============================================================
# Day 4：批量接口测试（Collection Runner 思路）
# ============================================================

def load_test_cases_from_csv(csv_file: str) -> List[Dict[str, Any]]:
    """
    从 CSV 读取测试数据。
    示例字段：
    url,method,param1,param2,expected_status
    """
    cases: List[Dict[str, Any]] = []

    with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cases.append(dict(row))

    return cases


def batch_run_api_tests_from_csv(csv_file: str) -> List[Dict[str, Any]]:
    """
    批量执行 CSV 中定义的接口测试。
    模拟 Postman Collection Runner + CSV 数据驱动思路。
    """
    cases = load_test_cases_from_csv(csv_file)
    all_results: List[Dict[str, Any]] = []

    for case in cases:
        url = case.get("url", "").strip()
        method = case.get("method", "GET").strip().upper()

        # 除了 url/method/expected_status，其余字段都当成参数
        payload = {
            k: v for k, v in case.items()
            if k not in {"url", "method", "expected_status"} and v != ""
        }

        if method == "GET":
            result = safe_request("GET", url, params=payload)
        else:
            result = safe_request("POST", url, json_data=payload)

        expected_status = case.get("expected_status")
        try:
            expected_status = int(expected_status) if expected_status else 200
        except ValueError:
            expected_status = 200

        assertions = {
            "status_match": result.status_code == expected_status,
            "request_success": result.ok,
        }

        all_results.append({
            "case": case,
            "result": result.to_dict(),
            "assertions": assertions
        })

    return all_results


# ============================================================
# Day 5：结果统计与汇总
# ============================================================

def summarize_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """统计批量测试结果。"""
    total = len(results)
    success = 0
    fail = 0
    elapsed_list: List[float] = []

    for item in results:
        if item["result"]["ok"]:
            success += 1
        else:
            fail += 1

        elapsed = item["result"]["elapsed_ms"]
        if isinstance(elapsed, (int, float)):
            elapsed_list.append(float(elapsed))

    summary = {
        "total": total,
        "success": success,
        "fail": fail,
        "success_rate": round(success / total * 100, 2) if total else 0,
        "avg_elapsed_ms": round(statistics.mean(elapsed_list), 2) if elapsed_list else None,
        "max_elapsed_ms": round(max(elapsed_list), 2) if elapsed_list else None,
        "min_elapsed_ms": round(min(elapsed_list), 2) if elapsed_list else None,
    }

    return summary


def save_results_to_json(results: List[Dict[str, Any]], output_file: str) -> None:
    """将测试结果保存为 JSON 文件。"""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


# ============================================================
# Day 6：测试报告文本输出
# ============================================================

def generate_test_report(summary: Dict[str, Any]) -> str:
    """生成简单的测试报告。"""
    lines = [
        "=== 接口测试报告 ===",
        f"总用例数: {summary['total']}",
        f"成功数: {summary['success']}",
        f"失败数: {summary['fail']}",
        f"成功率: {summary['success_rate']}%",
        f"平均响应时间: {summary['avg_elapsed_ms']} ms",
        f"最大响应时间: {summary['max_elapsed_ms']} ms",
        f"最小响应时间: {summary['min_elapsed_ms']} ms",
    ]
    return "\n".join(lines)


# ============================================================
# Day 7：配置表校验（贴近你的简历场景）
# ============================================================

def validate_probability_sum(records: List[Dict[str, Any]], key: str = "probability") -> Tuple[bool, float]:
    """
    校验概率总和是否约等于 1。
    适用于掉落表/奖池配置表。
    """
    total = 0.0
    for row in records:
        try:
            total += float(row.get(key, 0))
        except (TypeError, ValueError):
            return False, 0.0

    return abs(total - 1.0) < 1e-6, total


def validate_no_empty_fields(records: List[Dict[str, Any]], required_fields: List[str]) -> List[Dict[str, Any]]:
    """检查必填字段是否为空。"""
    problems = []

    for idx, row in enumerate(records, start=1):
        for field in required_fields:
            if str(row.get(field, "")).strip() == "":
                problems.append({
                    "row": idx,
                    "field": field,
                    "problem": "必填字段为空"
                })

    return problems


def validate_unique_field(records: List[Dict[str, Any]], field_name: str) -> List[Dict[str, Any]]:
    """检查某字段是否唯一，例如 id。"""
    seen = {}
    duplicates = []

    for idx, row in enumerate(records, start=1):
        value = row.get(field_name)
        if value in seen:
            duplicates.append({
                "row": idx,
                "field": field_name,
                "value": value,
                "problem": f"与第{seen[value]}行重复"
            })
        else:
            seen[value] = idx

    return duplicates


# ============================================================
# Day 8：Excel / CSV 配置表读取
# ============================================================

def load_records_from_csv(csv_file: str) -> List[Dict[str, Any]]:
    """从 CSV 读取配置记录。"""
    with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def load_records_from_excel(excel_file: str, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    从 Excel 读取配置记录。
    需要 pandas。
    """
    if pd is None:
        raise RuntimeError("未安装 pandas，无法读取 Excel。请执行: pip install pandas openpyxl")

    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    return df.fillna("").to_dict(orient="records")


def validate_config_file(file_path: str) -> Dict[str, Any]:
    """
    综合校验配置文件。
    默认检查：
    1. 必填字段 id/name 是否为空
    2. id 是否重复
    3. 如果存在 probability 字段，就校验总和
    """
    path = Path(file_path)
    if not path.exists():
        return {"ok": False, "error": f"文件不存在: {file_path}"}

    if path.suffix.lower() == ".csv":
        records = load_records_from_csv(file_path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        records = load_records_from_excel(file_path)
    else:
        return {"ok": False, "error": f"不支持的文件格式: {path.suffix}"}

    problems = []
    problems.extend(validate_no_empty_fields(records, ["id", "name"]))
    problems.extend(validate_unique_field(records, "id"))

    probability_check = None
    if records and "probability" in records[0]:
        ok, total = validate_probability_sum(records)
        probability_check = {"ok": ok, "total": total}
        if not ok:
            problems.append({
                "row": "ALL",
                "field": "probability",
                "problem": f"概率总和不为1，当前为 {total}"
            })

    return {
        "ok": len(problems) == 0,
        "total_records": len(records),
        "problems": problems,
        "probability_check": probability_check,
    }


# ============================================================
# Day 9：文件完整性校验（热更新/资源校验思路）
# ============================================================

def calculate_md5(file_path: str) -> str:
    """计算文件 MD5。"""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk)
    return md5.hexdigest()


def verify_file_md5(file_path: str, expected_md5: str) -> bool:
    """校验文件 MD5 是否与预期一致。"""
    if not Path(file_path).exists():
        return False
    return calculate_md5(file_path) == expected_md5.lower()


# ============================================================
# Day 10：版本号比较（热更新/版本检查）
# ============================================================

def compare_version(v1: str, v2: str) -> int:
    """
    比较两个版本号。
    返回：
    1  -> v1 > v2
    0  -> v1 == v2
    -1 -> v1 < v2
    """
    parts1 = [int(x) for x in v1.split(".")]
    parts2 = [int(x) for x in v2.split(".")]

    # 对齐长度
    max_len = max(len(parts1), len(parts2))
    parts1.extend([0] * (max_len - len(parts1)))
    parts2.extend([0] * (max_len - len(parts2)))

    if parts1 > parts2:
        return 1
    if parts1 < parts2:
        return -1
    return 0


def needs_update(local_version: str, remote_version: str) -> bool:
    """判断是否需要更新。"""
    return compare_version(local_version, remote_version) < 0


# ============================================================
# Day 11：弱网/重试模拟思路
# ============================================================

def simulated_download(
    retry_times: int = 3,
    fail_before_success: int = 2
) -> bool:
    """
    用纯 Python 模拟“下载失败后重试成功”的场景。
    主要是练测试思路，而不是真的做网络限速。
    """
    for i in range(1, retry_times + 1):
        # 前几次故意失败
        if i <= fail_before_success:
            print(f"第{i}次下载失败，准备重试...")
            time.sleep(0.5)
            continue

        print(f"第{i}次下载成功。")
        return True

    print("重试后仍然失败。")
    return False


# ============================================================
# Day 12：日志分析
# ============================================================

def find_keywords_in_log(log_file: str, keywords: List[str]) -> Dict[str, List[str]]:
    """
    从日志中查找关键字。
    例如：ERROR、Timeout、Exception
    """
    result = {kw: [] for kw in keywords}
    path = Path(log_file)

    if not path.exists():
        return result

    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line_no, line in enumerate(f, start=1):
            for kw in keywords:
                if kw in line:
                    result[kw].append(f"第{line_no}行: {line.strip()}")

    return result


# ============================================================
# Day 13：简单的测试用例模板生成
# ============================================================

def generate_test_case_template(module_name: str, function_points: List[str]) -> List[Dict[str, str]]:
    """
    根据模块名和功能点，快速生成测试用例骨架。
    """
    cases = []
    case_id = 1

    for point in function_points:
        cases.append({
            "case_id": f"{module_name.upper()}-{case_id:03d}",
            "module": module_name,
            "function_point": point,
            "precondition": "系统正常启动，测试账号可用",
            "steps": f"进入{module_name}模块，执行{point}",
            "expected_result": f"{point}执行成功，页面/接口返回符合预期"
        })
        case_id += 1

    return cases


# ============================================================
# Day 14：总调度 / 验收入口
# ============================================================

def demo_day1():
    """Day1 演示：test_api()"""
    url = "https://httpbin.org/post"
    data = {"username": "zhao", "role": "tester"}
    result = test_api(url, data)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def demo_day2():
    """Day2 演示：safe_request()"""
    result = safe_request("GET", "https://httpbin.org/get", params={"q": "api test"})
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def demo_day7_config_check():
    """Day7/8 演示：配置校验"""
    sample_records = [
        {"id": "1", "name": "木剑", "probability": "0.5"},
        {"id": "2", "name": "铁剑", "probability": "0.3"},
        {"id": "3", "name": "金剑", "probability": "0.2"},
    ]
    print("概率校验:", validate_probability_sum(sample_records))


def demo_day10_version():
    """Day10 演示：版本比较"""
    print("1.0.0 vs 1.0.1 =>", compare_version("1.0.0", "1.0.1"))
    print("1.2.0 vs 1.1.9 =>", compare_version("1.2.0", "1.1.9"))
    print("1.0 vs 1.0.0 =>", compare_version("1.0", "1.0.0"))


def demo_day13_case_template():
    """Day13 演示：生成测试用例模板"""
    cases = generate_test_case_template(
        "商城",
        ["购买商品", "取消订单", "使用优惠券"]
    )
    print(json.dumps(cases, ensure_ascii=False, indent=2))


def run_validation(day: int) -> None:
    """
    简化版 validation_script 思路。
    你 Notion 里已经明确有：
        python validation_script.py --day 1
    所以这里做一个轻量模拟入口，方便你统一演示。
    """
    print(f"=== 验证 Day {day} ===")

    if day == 1:
        demo_day1()
    elif day == 2:
        demo_day2()
    elif day == 7:
        demo_day7_config_check()
    elif day == 10:
        demo_day10_version()
    elif day == 13:
        demo_day13_case_template()
    else:
        print(f"Day {day} 暂无单独演示，代码已整合在本文件中，可直接查看对应函数。")


# ============================================================
# 命令行入口
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="14天测试工程师急救计划 - 代码作业整合版")
    parser.add_argument("--day", type=int, help="运行某一天的演示，例如 --day 1")
    parser.add_argument("--csv", type=str, help="运行 CSV 批量接口测试，例如 --csv cases.csv")
    parser.add_argument("--config", type=str, help="校验配置文件，例如 --config config.csv")

    args = parser.parse_args()

    if args.day is not None:
        run_validation(args.day)

    elif args.csv:
        results = batch_run_api_tests_from_csv(args.csv)
        summary = summarize_results(results)
        print(generate_test_report(summary))
        save_results_to_json(results, "batch_api_results.json")
        print("\n结果已保存到 batch_api_results.json")

    elif args.config:
        result = validate_config_file(args.config)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print("未提供参数，运行默认演示：Day 1")
        run_validation(1)
