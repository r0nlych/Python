import requests   # 导入requests库（用来发HTTP请求）
url = "http://httpbin.org/post"   # 请求地址（测试用接口）
data = {
    "userID":"55",   #用户ID
    "content":"666"   #弹幕内容
    }   #请求体数据（对应postman里的Body）
res = requests.post(url,json=data)   #发送POST请求，参数url是请求地址，json=data表示将data字典转换为JSON格式并作为请求体发送
print("状态码:",res.status_code)   #打印状态码（200代表成功）
print("返回数据:",res.text)   #打印返回的原始数据（对应postman里的Response）
result=res.json()   #将返回的JSON字符串转换为Python字典
print("解析后:",result)   #打印解析后的数据结构
print("解析结果:",result["json"])   #打印解析结果中的json字段（对应postman里的Response Body）
if res.status_code==200:   #如果状态码是200
    print("请求成功！")   #打印成功信息
    if result["json"]["userID"]=="55" and result["json"]["content"]=="666":
        print("数据解析成功！")   #如果解析结果中的userID是55且content是666，打印数据解析成功
    else:
        print("数据解析失败！")   #否则打印数据解析失败

else:
    print("请求失败！")   #否则打印失败信息
    


    if result["json"]["userID"]=="55":
        print("用户正确")
    else:
        print("用户错误")

if "userID" not in result["json"] or ["content"] not in result["json"]:
    print("数据结构错误")
else:
    if result["json"]["userID"]=="55":
        print("用户正确")
    else:
        print("用户错误")

