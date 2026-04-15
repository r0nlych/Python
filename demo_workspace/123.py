
import requests, json, time, hashlib, csv, statistics, argparse
from pathlib import Path

class ApiResult:
    def __init__(self, ok, url, method, status_code=None, elapsed_ms=None, response_json=None, response_text="", error=""):
        self.ok = ok
        self.url = url
        self.method = method
        self.status_code = status_code
        self.elapsed_ms = elapsed_ms
        self.response_json = response_json
        self.response_text = response_text
        self.error = error
    def to_dict(self):
        return self.__dict__

def test_api(url, data=None):
    start = time.time()
    try:
        response = requests.post(url, json=data, timeout=5)
        elapsed_ms = round((time.time() - start) * 1000,2)
        try:
            response_json = response.json()
        except:
            response_json = None
        return ApiResult(response.ok,url,"POST",response.status_code,elapsed_ms,response_json,response.text[:1000])
    except Exception as e:
        elapsed_ms = round((time.time() - start) * 1000,2)
        return ApiResult(False,url,"POST",None,elapsed_ms,None,"",str(e))

def safe_request(method,url,params=None,json_data=None,headers=None,timeout=5,retries=2,retry_interval=0.5):
    method = method.upper()
    last_error=""
    for attempt in range(1,retries+1):
        start = time.time()
        try:
            if method=="GET":
                response=requests.get(url,params=params,headers=headers,timeout=timeout)
            elif method=="POST":
                response=requests.post(url,json=json_data,headers=headers,timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            elapsed_ms = round((time.time()-start)*1000,2)
            try:
                response_json = response.json()
            except:
                response_json=None
            return ApiResult(response.ok,url,method,response.status_code,elapsed_ms,response_json,response.text[:1000])
        except Exception as e:
            last_error=f"Attempt {attempt} failed: {e}"
            if attempt<retries: time.sleep(retry_interval)
    return ApiResult(False,url,method,None,None,None,"",last_error)

def compare_version(v1,v2):
    p1=[int(x) for x in v1.split(".")]
    p2=[int(x) for x in v2.split(".")]
    max_len=max(len(p1),len(p2))
    p1+=[0]*(max_len-len(p1))
    p2+=[0]*(max_len-len(p2))
    return 1 if p1>p2 else -1 if p1<p2 else 0

def run_validation(day):
    print(f"=== Run Day {day} Demo ===")
    if day==1:
        url="https://httpbin.org/post"
        data={"username":"zhao","role":"tester"}
        result=test_api(url,data)
        print(json.dumps(result.to_dict(),ensure_ascii=False,indent=2))
    elif day==2:
        result=safe_request("GET","https://httpbin.org/get",params={"q":"test"})
        print(json.dumps(result.to_dict(),ensure_ascii=False,indent=2))
    elif day==3:
        print("Day3 demo: JSON assertions")
    elif day==4:
        print("Day4 demo: Batch CSV API")
    elif day==5:
        print("Day5 demo: Result summary")
    elif day==6:
        print("Day6 demo: Test report")
    elif day==7:
        print("Day7 demo: Config validation")
    elif day==8:
        print("Day8 demo: Excel config validation")
    elif day==9:
        print("Day9 demo: MD5 file check")
    elif day==10:
        print("Version compare 1.0.0 vs 1.0.1:",compare_version("1.0.0","1.0.1"))
    elif day==11:
        print("Day11 demo: Retry simulation")
    elif day==12:
        print("Day12 demo: Log analysis")
    elif day==13:
        print("Day13 demo: Test case template")
    elif day==14:
        print("Day14 demo: Full pipeline")
    else:
        print(f"Day {day} demo not implemented")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--day",type=int)
    args=parser.parse_args()
    if args.day: run_validation(args.day)
