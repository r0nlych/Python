# -*- coding: utf-8 -*-  # 指定源码文件使用 UTF-8 编码，避免中文乱码
import argparse  # 导入命令行参数解析模块，方便用 --day 或 --all 运行不同内容
import csv  # 导入 CSV 模块，用来读写测试数据文件
import hashlib  # 导入哈希模块，用来做 MD5 文件校验
import json  # 导入 JSON 模块，用来打印和保存结构化数据
import os  # 导入操作系统模块，用来处理文件路径和目录
import random  # 导入随机模块，用来生成模拟测试数据
import statistics  # 导入统计模块，用来算平均值、最大值、最小值
import time  # 导入时间模块，用来统计接口耗时、模拟等待
from dataclasses import dataclass, asdict  # 导入 dataclass，方便定义结果对象并转成字典
from pathlib import Path  # 导入 Path，方便跨平台处理文件路径
from typing import Any, Dict, List, Optional  # 导入类型提示，让代码更容易看懂

BASE_DIR = Path.cwd() / "day14_demo_workspace"  # 定义一个工作目录，所有演示文件都放这里，避免弄乱你的项目目录
BASE_DIR.mkdir(exist_ok=True)  # 如果工作目录不存在就自动创建，存在则不报错

@dataclass  # 用 dataclass 装饰器定义一个“接口结果”数据对象
class ApiResult:  # 定义接口返回结果的数据结构
    ok: bool  # 表示请求是否成功
    url: str  # 表示请求的地址
    method: str  # 表示请求方法，比如 GET、POST
    status_code: int  # 表示 HTTP 状态码或模拟状态码
    elapsed_ms: float  # 表示请求耗时，单位毫秒
    response_json: Dict[str, Any]  # 表示返回的 JSON 数据
    response_text: str  # 表示返回的原始文本
    error: str = ""  # 表示错误信息，默认空字符串

    def to_dict(self) -> Dict[str, Any]:  # 定义一个方法，把对象转成字典，便于打印和保存
        return asdict(self)  # 使用 asdict 把 dataclass 对象转成普通字典

def print_title(title: str) -> None:  # 定义一个打印标题的小函数，方便输出更清晰
    print("\n" + "=" * 70)  # 打印一条分隔线
    print(title)  # 打印标题内容
    print("=" * 70)  # 再打印一条分隔线

def save_json(file_path: Path, data: Any) -> None:  # 定义一个保存 JSON 的函数
    with open(file_path, "w", encoding="utf-8") as f:  # 以写入模式打开目标文件，并指定 UTF-8 编码
        json.dump(data, f, ensure_ascii=False, indent=2)  # 把数据保存成格式化的 JSON，保留中文

def load_json(file_path: Path) -> Any:  # 定义一个读取 JSON 的函数
    with open(file_path, "r", encoding="utf-8") as f:  # 以只读模式打开 JSON 文件
        return json.load(f)  # 读取并返回 JSON 数据

def write_csv(file_path: Path, rows: List[Dict[str, Any]]) -> None:  # 定义一个写入 CSV 文件的函数
    if not rows:  # 如果传进来的数据为空
        return  # 直接结束函数，因为没有数据可写
    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:  # 打开 CSV 文件，使用 utf-8-sig 方便 Excel 打开
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))  # 创建一个 DictWriter，并自动使用第一行的键作为表头
        writer.writeheader()  # 先写入表头
        writer.writerows(rows)  # 再写入所有数据行

def read_csv(file_path: Path) -> List[Dict[str, Any]]:  # 定义一个读取 CSV 文件的函数
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:  # 以只读方式打开 CSV 文件
        reader = csv.DictReader(f)  # 创建一个字典形式的 CSV 读取器
        return [dict(row) for row in reader]  # 把每一行转成字典并组成列表返回

def mock_http_post(url: str, data: Optional[Dict[str, Any]] = None) -> ApiResult:  # 定义一个“模拟 POST 请求”函数，默认离线也能跑
    start = time.time()  # 记录开始时间，用来计算耗时
    time.sleep(0.1)  # 模拟网络请求延迟，让结果更像真实请求
    response_json = {  # 构造一个假的返回 JSON
        "code": 0,  # 业务状态码 0 表示成功
        "message": "mock success",  # 返回成功信息
        "echo_url": url,  # 把传入的 URL 回显出来，便于确认请求地址
        "echo_data": data or {},  # 把传入的数据回显出来，便于确认请求体
    }  # 假响应 JSON 构造结束
    elapsed_ms = round((time.time() - start) * 1000, 2)  # 计算总耗时并保留两位小数
    return ApiResult(ok=True, url=url, method="POST", status_code=200, elapsed_ms=elapsed_ms, response_json=response_json, response_text=json.dumps(response_json, ensure_ascii=False), error="")  # 返回一个成功的模拟结果对象

def mock_http_get(url: str, params: Optional[Dict[str, Any]] = None) -> ApiResult:  # 定义一个“模拟 GET 请求”函数
    start = time.time()  # 记录开始时间
    time.sleep(0.1)  # 模拟请求耗时
    response_json = {  # 构造一个假的 GET 返回数据
        "code": 0,  # 业务状态码 0 表示成功
        "message": "mock success",  # 返回成功描述
        "echo_url": url,  # 回显请求地址
        "echo_params": params or {},  # 回显 GET 参数
    }  # 构造结束
    elapsed_ms = round((time.time() - start) * 1000, 2)  # 计算模拟耗时
    return ApiResult(ok=True, url=url, method="GET", status_code=200, elapsed_ms=elapsed_ms, response_json=response_json, response_text=json.dumps(response_json, ensure_ascii=False), error="")  # 返回模拟结果

def test_api(url: str, data: Optional[Dict[str, Any]] = None) -> ApiResult:  # Day1：把原始 requests 代码封装成 test_api(url, data) 函数
    return mock_http_post(url, data)  # 这里默认走离线 mock，保证没网络也能直接跑通

def safe_request(method: str, url: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, retries: int = 3) -> ApiResult:  # Day2：封装一个带重试机制的安全请求函数
    method = method.upper()  # 把请求方法转成大写，防止传入 get/post 时出错
    last_error = ""  # 初始化最后一次错误信息
    for attempt in range(1, retries + 1):  # 按重试次数循环尝试请求
        try:  # 进入异常捕获块，避免一次错误导致程序直接崩掉
            if method == "GET":  # 如果是 GET 请求
                result = mock_http_get(url, params=params)  # 调用模拟 GET 请求函数
            elif method == "POST":  # 如果是 POST 请求
                result = mock_http_post(url, data=json_data)  # 调用模拟 POST 请求函数
            else:  # 如果既不是 GET 也不是 POST
                raise ValueError("不支持的请求方法，只支持 GET 或 POST")  # 手动抛出异常，提醒方法不合法
            return result  # 如果请求成功，直接返回结果，不再继续重试
        except Exception as e:  # 如果本次请求发生异常
            last_error = f"第 {attempt} 次请求失败：{e}"  # 记录本次失败原因
            time.sleep(0.2)  # 稍微等待一下，再进行下一次重试
    return ApiResult(ok=False, url=url, method=method, status_code=500, elapsed_ms=0.0, response_json={}, response_text="", error=last_error)  # 如果所有重试都失败，返回一个失败结果对象

def assert_status_code(result: ApiResult, expected_code: int) -> bool:  # Day3：校验状态码是否等于预期值
    return result.status_code == expected_code  # 返回 True 或 False

def assert_json_key(result: ApiResult, key: str) -> bool:  # Day3：校验返回 JSON 里是否包含某个字段
    return key in result.response_json  # 如果 key 在 response_json 中就返回 True

def batch_run_cases(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:  # Day4：批量执行接口测试用例
    all_results = []  # 创建一个空列表，用来收集每一条用例的执行结果
    for case in cases:  # 遍历每一条测试用例
        method = case.get("method", "GET")  # 取出 method 字段，默认使用 GET
        url = case.get("url", "")  # 取出 url 字段
        expected_status = int(case.get("expected_status", 200))  # 取出预期状态码，默认 200
        if method.upper() == "GET":  # 如果当前用例是 GET 请求
            result = safe_request("GET", url, params={"keyword": case.get("keyword", "")})  # 执行 GET 请求
        else:  # 否则按 POST 请求处理
            result = safe_request("POST", url, json_data={"username": case.get("username", ""), "role": case.get("role", "")})  # 执行 POST 请求
        check_status = assert_status_code(result, expected_status)  # 检查状态码是否符合预期
        check_json = assert_json_key(result, "code")  # 检查返回 JSON 中是否包含 code 字段
        all_results.append({  # 把当前用例的执行结果追加到结果列表里
            "case_id": case.get("case_id", ""),  # 保存用例编号
            "method": method,  # 保存请求方法
            "url": url,  # 保存请求地址
            "expected_status": expected_status,  # 保存预期状态码
            "actual_status": result.status_code,  # 保存实际状态码
            "status_check_pass": check_status,  # 保存状态码检查是否通过
            "json_check_pass": check_json,  # 保存 JSON 字段检查是否通过
            "elapsed_ms": result.elapsed_ms,  # 保存请求耗时
            "error": result.error,  # 保存错误信息
        })  # 当前用例结果追加结束
    return all_results  # 返回所有批量执行结果

def summarize_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:  # Day5：汇总批量测试结果
    total = len(results)  # 统计总用例数
    passed = sum(1 for item in results if item["status_check_pass"] and item["json_check_pass"])  # 统计同时通过状态码和 JSON 检查的用例数量
    failed = total - passed  # 用总数减去通过数得到失败数
    times = [float(item["elapsed_ms"]) for item in results if item["elapsed_ms"] is not None]  # 提取所有耗时数据，用于做统计
    summary = {  # 组装一个汇总字典
        "total": total,  # 总用例数
        "passed": passed,  # 通过数
        "failed": failed,  # 失败数
        "pass_rate": round((passed / total) * 100, 2) if total else 0.0,  # 通过率，保留两位小数
        "avg_elapsed_ms": round(statistics.mean(times), 2) if times else 0.0,  # 平均耗时
        "max_elapsed_ms": round(max(times), 2) if times else 0.0,  # 最大耗时
        "min_elapsed_ms": round(min(times), 2) if times else 0.0,  # 最小耗时
    }  # 汇总字典构造结束
    return summary  # 返回汇总结果

def build_report(summary: Dict[str, Any]) -> str:  # Day6：把统计结果拼成一份可读性更强的测试报告文本
    lines = [  # 创建一个字符串列表，每一行都是报告中的一行
        "接口批量测试报告",  # 报告标题
        f"总用例数：{summary['total']}",  # 写入总用例数
        f"通过数：{summary['passed']}",  # 写入通过数
        f"失败数：{summary['failed']}",  # 写入失败数
        f"通过率：{summary['pass_rate']}%",  # 写入通过率
        f"平均耗时：{summary['avg_elapsed_ms']} ms",  # 写入平均耗时
        f"最大耗时：{summary['max_elapsed_ms']} ms",  # 写入最大耗时
        f"最小耗时：{summary['min_elapsed_ms']} ms",  # 写入最小耗时
    ]  # 报告文本列表构造结束
    return "\n".join(lines)  # 用换行符把每一行拼成完整字符串并返回

def validate_config_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:  # Day7：校验配置表数据，找出问题项
    problems = []  # 创建一个空列表，用来存配置问题
    ids_seen = set()  # 创建一个集合，用来检查 id 是否重复
    probability_sum = 0.0  # 初始化概率总和
    for index, row in enumerate(rows, start=1):  # 带行号遍历每一条配置数据
        if not row.get("id", "").strip():  # 如果 id 为空
            problems.append({"row": str(index), "problem": "id 不能为空"})  # 记录问题
        if not row.get("name", "").strip():  # 如果 name 为空
            problems.append({"row": str(index), "problem": "name 不能为空"})  # 记录问题
        current_id = row.get("id", "").strip()  # 取出当前行的 id 并去掉空格
        if current_id in ids_seen:  # 如果当前 id 已经在集合中出现过
            problems.append({"row": str(index), "problem": f"id 重复：{current_id}"})  # 记录重复问题
        ids_seen.add(current_id)  # 把当前 id 放进已见集合
        try:  # 尝试把 probability 转成浮点数
            probability_sum += float(row.get("probability", "0"))  # 累加概率
        except ValueError:  # 如果转浮点数失败
            problems.append({"row": str(index), "problem": "probability 不是数字"})  # 记录概率格式错误
    if round(probability_sum, 2) != 1.00:  # 如果所有概率之和不等于 1.00
        problems.append({"row": "ALL", "problem": f"概率总和不等于 1，当前为 {probability_sum}"})  # 记录全局概率问题
    return problems  # 返回所有配置问题

def load_config_csv(file_path: Path) -> List[Dict[str, Any]]:  # Day8：读取配置 CSV 文件
    return read_csv(file_path)  # 直接调用通用 CSV 读取函数并返回结果

def calculate_md5(file_path: Path) -> str:  # Day9：计算文件的 MD5 值
    md5 = hashlib.md5()  # 创建一个 md5 对象
    with open(file_path, "rb") as f:  # 以二进制方式打开文件，方便读取任意文件内容
        for chunk in iter(lambda: f.read(4096), b""):  # 按 4096 字节一块一块读取文件，直到读完
            md5.update(chunk)  # 把每一块内容喂给 md5 对象
    return md5.hexdigest()  # 返回最终的 MD5 十六进制字符串

def compare_version(v1: str, v2: str) -> int:  # Day10：比较两个版本号的大小
    p1 = [int(x) for x in v1.split(".")]  # 把第一个版本号按点拆开，并把每一段转成整数
    p2 = [int(x) for x in v2.split(".")]  # 把第二个版本号按点拆开，并把每一段转成整数
    max_len = max(len(p1), len(p2))  # 找出两个版本数组中更长的长度
    p1 += [0] * (max_len - len(p1))  # 如果 p1 较短，就用 0 补齐
    p2 += [0] * (max_len - len(p2))  # 如果 p2 较短，就用 0 补齐
    if p1 > p2:  # 如果 p1 对应的版本更大
        return 1  # 返回 1，表示 v1 > v2
    if p1 < p2:  # 如果 p1 对应的版本更小
        return -1  # 返回 -1，表示 v1 < v2
    return 0  # 如果完全相等，返回 0

def simulate_retry_download(max_retry: int = 3) -> Dict[str, Any]:  # Day11：模拟下载失败后重试成功的过程
    history = []  # 创建一个列表，用来记录每次尝试的结果
    for attempt in range(1, max_retry + 1):  # 从第 1 次尝试循环到最大重试次数
        if attempt < max_retry:  # 如果还没到最后一次
            history.append({"attempt": attempt, "result": "失败"})  # 记录这次下载失败
            time.sleep(0.1)  # 模拟等待一小会儿再重试
        else:  # 如果到了最后一次
            history.append({"attempt": attempt, "result": "成功"})  # 记录最后一次成功
    return {"max_retry": max_retry, "history": history}  # 返回整个重试过程

def analyze_log(file_path: Path, keywords: List[str]) -> Dict[str, List[str]]:  # Day12：分析日志文件，查找关键字
    result = {keyword: [] for keyword in keywords}  # 创建一个结果字典，每个关键字对应一个匹配行列表
    with open(file_path, "r", encoding="utf-8") as f:  # 以 UTF-8 编码打开日志文件
        for line_no, line in enumerate(f, start=1):  # 按行遍历日志文件，并记录行号
            for keyword in keywords:  # 遍历每一个需要查找的关键字
                if keyword in line:  # 如果当前关键字出现在当前行中
                    result[keyword].append(f"第 {line_no} 行：{line.strip()}")  # 把匹配到的行号和内容记录下来
    return result  # 返回关键字分析结果

def generate_case_templates(module_name: str, function_points: List[str]) -> List[Dict[str, str]]:  # Day13：根据模块名和功能点生成测试用例模板
    cases = []  # 创建一个空列表，用来存所有测试用例
    for index, point in enumerate(function_points, start=1):  # 遍历每一个功能点，并自动生成编号
        cases.append({  # 追加一条测试用例模板
            "case_id": f"{module_name.upper()}-{index:03d}",  # 生成形如 SHOP-001 的用例编号
            "module": module_name,  # 记录模块名
            "function_point": point,  # 记录功能点
            "precondition": "系统正常启动，测试账号可用",  # 写一条通用前置条件
            "steps": f"进入 {module_name} 模块，执行 {point}",  # 写测试步骤
            "expected_result": f"{point} 执行成功，返回结果符合预期",  # 写期望结果
        })  # 一条测试用例模板追加结束
    return cases  # 返回所有生成的模板用例

def prepare_demo_files() -> Dict[str, Path]:  # Day14：准备整个 14 天流程需要的演示文件
    api_csv = BASE_DIR / "api_cases.csv"  # 定义批量接口测试用例文件路径
    config_csv = BASE_DIR / "config_data.csv"  # 定义配置表文件路径
    log_file = BASE_DIR / "app.log"  # 定义日志文件路径
    demo_txt = BASE_DIR / "demo_file.txt"  # 定义一个普通文本文件路径，用来做 MD5 校验

    api_rows = [  # 构造批量接口测试的模拟数据
        {"case_id": "API-001", "method": "GET", "url": "https://mock.api/search", "keyword": "sword", "expected_status": "200"},  # 第一条 GET 用例
        {"case_id": "API-002", "method": "POST", "url": "https://mock.api/login", "username": "zhao", "role": "tester", "expected_status": "200"},  # 第二条 POST 用例
    ]  # 批量接口用例构造结束
    write_csv(api_csv, api_rows)  # 把模拟接口测试用例写入 CSV 文件

    config_rows = [  # 构造配置表模拟数据
        {"id": "1", "name": "木剑", "probability": "0.5"},  # 配置表第一行
        {"id": "2", "name": "铁剑", "probability": "0.3"},  # 配置表第二行
        {"id": "3", "name": "金剑", "probability": "0.2"},  # 配置表第三行
    ]  # 配置表模拟数据构造结束
    write_csv(config_csv, config_rows)  # 把配置表写到 CSV 文件中

    with open(log_file, "w", encoding="utf-8") as f:  # 创建并写入日志文件
        f.write("INFO 应用启动成功\n")  # 写入一行普通信息日志
        f.write("WARNING 网络波动，已触发重试\n")  # 写入一行警告日志
        f.write("ERROR 登录接口返回超时\n")  # 写入一行错误日志
        f.write("INFO 用户点击商城购买按钮\n")  # 再写入一行普通信息
        f.write("ERROR 配置表奖励字段缺失\n")  # 再写入一行错误信息

    with open(demo_txt, "w", encoding="utf-8") as f:  # 创建一个普通文本文件
        f.write("这是一个用于 MD5 校验的演示文件。")  # 写入测试内容

    return {"api_csv": api_csv, "config_csv": config_csv, "log_file": log_file, "demo_txt": demo_txt}  # 返回所有准备好的文件路径

def day1_demo() -> Dict[str, Any]:  # Day1：演示把 requests 代码改成 test_api(url, data)
    print_title("Day1：封装 test_api(url, data)")  # 打印标题
    result = test_api("https://mock.api/login", {"username": "zhao", "role": "tester"})  # 执行模拟 POST 请求
    data = result.to_dict()  # 把结果对象转成字典
    print(json.dumps(data, ensure_ascii=False, indent=2))  # 漂亮打印结果
    return data  # 返回结果，便于后续全流程统一收集

def day2_demo() -> Dict[str, Any]:  # Day2：演示 safe_request 重试请求
    print_title("Day2：封装 safe_request()，加入异常处理和重试")  # 打印标题
    result = safe_request("GET", "https://mock.api/search", params={"keyword": "weapon"})  # 执行模拟 GET 请求
    data = result.to_dict()  # 转成字典
    print(json.dumps(data, ensure_ascii=False, indent=2))  # 打印结果
    return data  # 返回结果

def day3_demo() -> Dict[str, Any]:  # Day3：演示接口断言
    print_title("Day3：接口断言")  # 打印标题
    result = safe_request("GET", "https://mock.api/search", params={"keyword": "weapon"})  # 先执行一个请求，拿到结果用于断言
    checks = {  # 构造断言结果字典
        "状态码等于200": assert_status_code(result, 200),  # 检查状态码
        "返回JSON里包含code字段": assert_json_key(result, "code"),  # 检查 JSON key
    }  # 断言结果构造结束
    print(json.dumps(checks, ensure_ascii=False, indent=2))  # 打印断言结果
    return checks  # 返回断言结果

def day4_demo(files: Dict[str, Path]) -> List[Dict[str, Any]]:  # Day4：演示读取 CSV 批量执行接口测试
    print_title("Day4：CSV 批量接口测试")  # 打印标题
    cases = read_csv(files["api_csv"])  # 读取之前准备好的 api_cases.csv 文件
    results = batch_run_cases(cases)  # 批量执行用例
    print(json.dumps(results, ensure_ascii=False, indent=2))  # 打印批量结果
    return results  # 返回批量执行结果

def day5_demo(day4_results: List[Dict[str, Any]]) -> Dict[str, Any]:  # Day5：演示结果汇总统计
    print_title("Day5：结果统计")  # 打印标题
    summary = summarize_results(day4_results)  # 对 Day4 的结果做统计汇总
    print(json.dumps(summary, ensure_ascii=False, indent=2))  # 打印统计结果
    return summary  # 返回汇总结果

def day6_demo(summary: Dict[str, Any]) -> str:  # Day6：演示生成测试报告
    print_title("Day6：生成测试报告")  # 打印标题
    report = build_report(summary)  # 根据统计结果生成报告文本
    print(report)  # 打印报告内容
    return report  # 返回报告文本

def day7_demo(files: Dict[str, Path]) -> List[Dict[str, str]]:  # Day7：演示配置表校验
    print_title("Day7：配置表规则校验")  # 打印标题
    rows = read_csv(files["config_csv"])  # 读取配置表 CSV
    problems = validate_config_rows(rows)  # 对配置表做规则校验
    print(json.dumps(problems, ensure_ascii=False, indent=2))  # 打印问题列表
    return problems  # 返回问题列表

def day8_demo(files: Dict[str, Path]) -> List[Dict[str, Any]]:  # Day8：演示从配置文件读取数据
    print_title("Day8：读取配置文件")  # 打印标题
    rows = load_config_csv(files["config_csv"])  # 读取配置表数据
    print(json.dumps(rows, ensure_ascii=False, indent=2))  # 打印读取结果
    return rows  # 返回读取结果

def day9_demo(files: Dict[str, Path]) -> Dict[str, str]:  # Day9：演示文件 MD5 校验
    print_title("Day9：文件 MD5 校验")  # 打印标题
    md5_value = calculate_md5(files["demo_txt"])  # 计算 demo 文件的 MD5 值
    result = {"file": str(files["demo_txt"]), "md5": md5_value}  # 构造输出字典
    print(json.dumps(result, ensure_ascii=False, indent=2))  # 打印 MD5 结果
    return result  # 返回结果

def day10_demo() -> Dict[str, Any]:  # Day10：演示版本号比较
    print_title("Day10：版本号比较")  # 打印标题
    result = {  # 构造几个版本比较示例
        "1.0.0_vs_1.0.1": compare_version("1.0.0", "1.0.1"),  # 第一组比较
        "1.2.0_vs_1.1.9": compare_version("1.2.0", "1.1.9"),  # 第二组比较
        "1.0_vs_1.0.0": compare_version("1.0", "1.0.0"),  # 第三组比较
    }  # 版本比较结果构造结束
    print(json.dumps(result, ensure_ascii=False, indent=2))  # 打印比较结果
    return result  # 返回比较结果

def day11_demo() -> Dict[str, Any]:  # Day11：演示失败重试逻辑
    print_title("Day11：失败重试模拟")  # 打印标题
    result = simulate_retry_download(max_retry=3)  # 执行重试模拟
    print(json.dumps(result, ensure_ascii=False, indent=2))  # 打印结果
    return result  # 返回结果

def day12_demo(files: Dict[str, Path]) -> Dict[str, List[str]]:  # Day12：演示日志分析
    print_title("Day12：日志分析")  # 打印标题
    result = analyze_log(files["log_file"], ["ERROR", "WARNING"])  # 从日志里查找 ERROR 和 WARNING
    print(json.dumps(result, ensure_ascii=False, indent=2))  # 打印日志分析结果
    return result  # 返回分析结果

def day13_demo() -> List[Dict[str, str]]:  # Day13：演示自动生成测试用例模板
    print_title("Day13：自动生成测试用例模板")  # 打印标题
    cases = generate_case_templates("商城", ["购买商品", "取消订单", "使用优惠券"])  # 生成商城模块的三个测试用例模板
    print(json.dumps(cases, ensure_ascii=False, indent=2))  # 打印生成结果
    return cases  # 返回用例模板

def day14_demo() -> Dict[str, Any]:  # Day14：演示把前面所有内容串成完整流程
    print_title("Day14：全流程串联演示")  # 打印标题
    files = prepare_demo_files()  # 先准备好全流程所需的演示文件
    result_day1 = day1_demo()  # 执行 Day1 演示
    result_day2 = day2_demo()  # 执行 Day2 演示
    result_day3 = day3_demo()  # 执行 Day3 演示
    result_day4 = day4_demo(files)  # 执行 Day4 演示
    result_day5 = day5_demo(result_day4)  # 执行 Day5 演示
    result_day6 = day6_demo(result_day5)  # 执行 Day6 演示
    result_day7 = day7_demo(files)  # 执行 Day7 演示
    result_day8 = day8_demo(files)  # 执行 Day8 演示
    result_day9 = day9_demo(files)  # 执行 Day9 演示
    result_day10 = day10_demo()  # 执行 Day10 演示
    result_day11 = day11_demo()  # 执行 Day11 演示
    result_day12 = day12_demo(files)  # 执行 Day12 演示
    result_day13 = day13_demo()  # 执行 Day13 演示

    final_data = {  # 把所有天的结果汇总成一个总字典
        "day1": result_day1,  # 保存 Day1 结果
        "day2": result_day2,  # 保存 Day2 结果
        "day3": result_day3,  # 保存 Day3 结果
        "day4": result_day4,  # 保存 Day4 结果
        "day5": result_day5,  # 保存 Day5 结果
        "day6": result_day6,  # 保存 Day6 结果
        "day7": result_day7,  # 保存 Day7 结果
        "day8": result_day8,  # 保存 Day8 结果
        "day9": result_day9,  # 保存 Day9 结果
        "day10": result_day10,  # 保存 Day10 结果
        "day11": result_day11,  # 保存 Day11 结果
        "day12": result_day12,  # 保存 Day12 结果
        "day13": result_day13,  # 保存 Day13 结果
    }  # 汇总字典构造结束

    output_file = BASE_DIR / "full_pipeline_result.json"  # 定义全流程结果输出文件路径
    save_json(output_file, final_data)  # 把全流程结果保存成 JSON 文件
    print(f"\n全流程结果已保存到：{output_file}")  # 打印输出文件路径
    return final_data  # 返回全流程结果

def run_day(day: int) -> Any:  # 定义一个总调度函数，根据 day 参数运行指定天数
    files = prepare_demo_files()  # 每次运行前先准备演示文件，保证单独跑某一天也不会缺文件
    if day == 1:  # 如果选择 Day1
        return day1_demo()  # 运行 Day1
    if day == 2:  # 如果选择 Day2
        return day2_demo()  # 运行 Day2
    if day == 3:  # 如果选择 Day3
        return day3_demo()  # 运行 Day3
    if day == 4:  # 如果选择 Day4
        return day4_demo(files)  # 运行 Day4
    if day == 5:  # 如果选择 Day5
        return day5_demo(day4_demo(files))  # 先跑 Day4，再拿结果做 Day5
    if day == 6:  # 如果选择 Day6
        return day6_demo(day5_demo(day4_demo(files)))  # 先跑 Day4、Day5，再生成报告
    if day == 7:  # 如果选择 Day7
        return day7_demo(files)  # 运行 Day7
    if day == 8:  # 如果选择 Day8
        return day8_demo(files)  # 运行 Day8
    if day == 9:  # 如果选择 Day9
        return day9_demo(files)  # 运行 Day9
    if day == 10:  # 如果选择 Day10
        return day10_demo()  # 运行 Day10
    if day == 11:  # 如果选择 Day11
        return day11_demo()  # 运行 Day11
    if day == 12:  # 如果选择 Day12
        return day12_demo(files)  # 运行 Day12
    if day == 13:  # 如果选择 Day13
        return day13_demo()  # 运行 Day13
    if day == 14:  # 如果选择 Day14
        return day14_demo()  # 运行 Day14 全流程
    raise ValueError("day 参数必须是 1 到 14 之间的整数")  # 如果 day 不在范围内，就抛出异常

def main() -> None:  # 定义主函数，作为程序入口
    parser = argparse.ArgumentParser(description="14天测试工程师学习代码整合版：默认离线可运行")  # 创建命令行参数解析器，并写一段说明文字
    parser.add_argument("--day", type=int, help="运行指定天数，例如 --day 1")  # 添加 --day 参数，允许运行指定某一天
    parser.add_argument("--all", action="store_true", help="运行完整 14 天全流程")  # 添加 --all 参数，允许一次跑完整流程
    args = parser.parse_args()  # 解析命令行传入的参数

    if args.all:  # 如果命令行里传入了 --all
        day14_demo()  # 直接运行全流程
        return  # 运行后直接结束

    if args.day:  # 如果命令行里传入了 --day
        run_day(args.day)  # 运行指定天数
        return  # 运行后直接结束

    print("未传入参数，默认运行 Day14 全流程。")  # 如果什么参数都没传，就提示用户默认跑全流程
    day14_demo()  # 默认直接跑完整 14 天流程

if __name__ == "__main__":  # 只有当这个文件被直接运行时，下面的 main 才会执行
    main()  # 调用主函数，正式启动程序
