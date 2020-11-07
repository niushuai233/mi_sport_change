# -*- coding: utf8 -*-
import requests,time,re,json
  
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
 
#获取登录code
def get_code(location):
    code_pattern = re.compile("(?<=access=).*?(?=&)")
    code = code_pattern.findall(location)[0]
    print("get_code = " + code)
    return code
 
#登录
def login(user,password):
    print("user="+user+", pwd="+password)
    url1 = "https://api-user.huami.com/registrations/+86" + user + "/tokens"
    headers = {
        "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",
    "User-Agent":"MiFit/4.6.0 (iPhone; iOS 14.0.1; Scale/2.00)"
        }
    data1 = {
        "client_id":"HuaMi",
        "password":f"{password}",
        "redirect_uri":"https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html",
        "token":"access"
        }
    r1 = requests.post(url1,data=data1,headers=headers,allow_redirects=False)
    print("r1.text = " + r1.text)
    location = r1.headers["Location"]
    print("r1.location = " + location)
    try:
        code = get_code(location)
    except:
        return 0,0
    print("access_code获取成功！")
    print(code)
     
    url2 = "https://account.huami.com/v2/client/login"
    data2 = {
        "app_name":"com.xiaomi.hm.health",
        "app_version":"4.6.0",
        "code":f"{code}",
        "country_code":"CN",
        "device_id":"2C8B4939-0CCD-4E94-8CBA-CB8EA6E613A1",
        "device_model":"phone",
        "grant_type":"access_token",
        "third_name":"huami_phone",
        } 
    r2 = requests.post(url2,data=data2,headers=headers).json()
    login_token = r2["token_info"]["login_token"]
    print("login_token获取成功！")
    print(login_token)
    userid = r2["token_info"]["user_id"]
    print("userid获取成功！")
    print(userid)
 
    return login_token,userid
 
#主函数
def main_handler(event, context):
    print(event["queryString"])
    try:
        user = str(event["queryString"]["user"])
        password = str(event["queryString"]["password"])
        step = str(event["queryString"]["step"])
    except:
        return "please input user,password,step"
     
    login_token = 0
    login_token,userid = login(user,password)
    if login_token == 0:
        print("登陆失败！")
        return "login fail!"
 
    t = get_time()
     
    app_token = get_app_token(login_token)
 
    date = time.strftime("%Y-%m-%d",time.localtime())
 
    with open('data_json.txt','rt') as f:
        data_json = f.read()
    data_json += date + "\"}]"
    step_pattern = re.compile("12345")
    de_id_pattern = re.compile("321123")
    data_json = de_id_pattern.sub("DA932FFFFE8816E7",data_json)
    data_json = step_pattern.sub(f"{step}",data_json)
     
    url = f'https://api-mifit-cn.huami.com/v1/data/band_data.json?&t={t}'
    head = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.12(0x17000c2d) NetType/WIFI Language/zh_CN',
        'apptoken': f'{app_token}'
        }
     
    data = {
        'data_json': f'{data_json}',
        'userid': f'{userid}',
        'device_type': '0',
        'last_sync_data_time': '1589917081',
        'last_deviceid': 'DA932FFFFE8816E7',
        }
 
    response = requests.post(url, data=data, headers=head).json()
    print(response)
    result = f"change step {step}:"+ response['message']
    print(result)
    return result
  
#获取时间戳
def get_time():
    url = 'http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp'
    response = requests.get(url,headers=headers).json()
    t = response['data']['t']
    return t
  
#获取app_token
def get_app_token(login_token):
    url = f"https://account-cn.huami.com/v1/client/app_tokens?app_name=com.xiaomi.hm.health&dn=api-user.huami.com%2Capi-mifit.huami.com%2Capp-analytics.huami.com&login_token={login_token}&os_version=4.1.0"
    response = requests.get(url,headers=headers).json()
    app_token = response['token_info']['app_token']
    print("app_token获取成功！")
    print(app_token)
    return app_token
 
#main_handler(0,0)
