def test(a):   #定义函数，a是参数
    print(a)   #打印参数a
test(10)   #调用函数
for i in range(3):   #循环三次（0，1，2，）   为什么写个3就是循环三次？因为range(3)生成的序列是0,1,2，循环会依次取出这些值赋给i，所以循环三次。
    print(i)   #打印当前循环变量i

def repeat_print(a):   #定义函数，a是参数 为什么叫repeat_print？因为这个函数的功能是重复打印参数a。
    for i in range(3):   #循环三次（0，1，2，）   如果去掉这个循环，函数就只能打印一次参数a了，无法实现重复打印的效果。
        print(a)   #打印参数a   为什么不输出i？因为这个函数的目的是重复打印参数a，而不是打印循环变量i，所以我们只需要打印a即可。
repeat_print("hello")   #调用函数，传入字符串"hello"作为参数a，这样就会重复打印"hello"三次。    
try:
    print(1 /0)   #尝试执行除以零的操作，这会引发ZeroDivisionError异常
except:
    print("出错了")

def test():   #定义函数test
    for i in range(3):   #循环三次（0，1，2，）   这个循环的目的是为了模拟在函数内部可能会发生异常的情况，每次循环都会尝试执行可能出错的代码。
        try:   #尝试执行以下代码块，如果发生异常会跳转到except块
            print("第",i,"次")   #打印当前是第几次循环，这里i的值会依次是0,1,2
        except Exception as e:   #如果在try块中发生任何异常，都会执行这个except块
            print("出错了",e)   #打印错误信息，这里的e会包含具体的异常信息，帮助我们了解发生了什么错误

import time   #导入time模块，这个模块提供了各种时间相关的函数
def test_retry():   #定义函数test_retry，为什么叫test_retry？因为这个函数的目的是测试重试机制，模拟在执行过程中可能会发生错误的情况，并且在发生错误时进行重试。
    for i in range(3):   
        try:
            print("尝试第",i,"次")
            raise Exception("失败") #模拟一个异常，这里我们直接抛出一个Exception异常，表示操作失败了，这样我们就可以测试重试机制了。
        except Exception as e:
            print("失败，请重试",e)   #打印失败信息，这里的e会包含具体的异常信息，帮助我们了解发生了什么错误。
            time.sleep(2**i)   



def my_request():   #定义函数my_request，q是参数，为什么叫my_request？因为这个函数的目的是模拟一个请求操作，可能会失败，需要进行重试。
    for i in range(3):   #循环三次（0，1，2，）   这个循环的目的是为了模拟在函数内部可能会发生异常的情况，每次循环都会尝试执行可能出错的代码。
        if i==0 or i==1:   #如果i是0或者1，表示第一次和第二次尝试
            try:
                print("尝试第",i,"次")   #打印当前是第几次循环，这里i的值会依次是0,1,2
                raise Exception("失败，准备重试")   #模拟一个异常，这里我们直接抛出一个Exception异常，表示操作失败了，这样我们就可以测试重试机制了。
            except Exception as e:
                print("失败，请重试",e)   #打印失败信息，这里的e会包含具体的异常信息，帮助我们了解发生了什么错误。
        else:
            print("成功")   #如果i是2，表示第三次尝试，这次我们不抛出异常，直接打印成功，这样就模拟了在前两次失败后，第三次成功的情况。
            time.sleep(2**i)   #在每次尝试后进行指数退避，等待2的i次幂秒，这样可以模拟在重试时逐渐增加等待时间的效果。




import requests  # 导入requests库（用来发HTTP请求）
import time  # 导入time库（用来实现等待功能）

def safe_request(url,data,max_retry=3):
    headers = {"Content-Type":"application/json"}
    for i in range(max_retry):
        try:
            print("第",i+1,"次请求")
            res = requests.post(url,headers=headers,json=data,timeout=5)   # 发送POST请求，参数url是请求地址，json=data表示将data字典转换为JSON格式并作为请求体发送
            print("状态码：",res.status_code)   # 打印状态码（200代表成功）
            res.raise_for_status()   # 使用raise_for_status()检查HTTP错误，如果状态码不是200，会抛出异常
            return True,res.json()   # 返回 (True, res.json())
        except requests.exceptions.Timeout:
            print(f"第{i+1}次超时，准备重试")
            time.sleep(2**i)   # 等待2的max_retry次幂秒
        except requests.exceptions.RequestException as e:
            print("请求失败")
            return False,str(e)   # 返回 (False, 错误信息)
    return False, "请求失败（多次重试后仍超时）"
