# 模板1：带异常处理的接口函数（Day 1）
import requests
import time
import json

def safe_request(url,data,max_retry=3):
    """
    带重试机制的接口请求
    TODO: 完成此函数的以下步骤
    [ ] Step 1: 设置请求headers (Content-Type: application/json)
    [ ] Step 2: 实现for循环进行重试
    [ ] Step 3: try块中发送POST请求，设置5秒超时
    [ ] Step 4: 使用raise_for_status()检查HTTP错误
    [ ] Step 5: 返回 (True, res.json())
    [ ] Step 6: except Timeout时进行指数退避 (2^i秒)
    [ ] Step 7: 其他异常返回 (False, 错误信息)
    """
    headers = {"Content-Type":"application/json"}
    for i in range(max_retry):
        try:
            res=requests.post(url=url,json=data,headers=headers,timeout=5)
            res.raise_for_status()
            return True,res.json()
        except requests.exceptions.Timeout:
            time.sleep(2**i)
            print(f"第{i+1}次请求超时，准备重试")   # 打印重试信息，i+1表示当前是第几次尝试（从1开始计数）
        except json.JSONDecodeError as e:
            return False,"JSON解析错误: " + str(e)
        except requests.exceptions.RequestException as e:
            return False,str(e)
    return False,"请求失败（多次重试后仍超时）"
def run_test():
    total = 0
    success = 0
    fail = 0
    urls = [
        "https://httpbin.org/post",        # 正常请求
        "https://httpbin.org/status/404",  # 404 错误
        "https://httpbin.org/delay/10"     # 超时
        ]
    for u in urls:
        ok, res = safe_request(u,{"value":"5"})
        print(ok)
        print(res)
        total +=1
        if ok:
            success +=1
        else:
            fail +=1
        print(f"调用:{u},接口结果:{ok},相应内容:{res}")
    print(f"总用例: {total}, 通过: {success}, 失败: {fail}")
    return total,success
def write_report(total,success):
    fail = total - success
    with open("report.txt","w",encoding="utf-8") as f:
     f.write(f"总用例: {total},通过: {success},失败: {fail}")
if __name__ == "__main__":   #   确保只有在直接运行此脚本时才执行测试
    total,success = run_test()   # 运行测试并获取总数和成功数
    write_report(total,success) # 写入报告文件
    print("报告已生成: report.txt")
