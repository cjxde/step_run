from sqlite3 import Timestamp
import time
import random
import string
import hashlib
import json
from unittest.mock import NonCallableMagicMock
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import os

# ====================== 配置区 ======================
# 本地调试兜底，Github从Secret环境变量读取
tel = os.getenv("ACCOUNT_TEL", "cjxde@hotmail.com")
psw = os.getenv("ACCOUNT_PSW", "Cj@1234567zepp")
url = "https://step.wvuvw.top"
# ====================================================

def get_secret_key():
    arr = ['fanTui2024', 'SecretKey', '1234567890', '1234567890', '1234567890', '1234567890']
    return "".join(arr) + "123456789012345678901234567890"

def generate_nonce():
    def rand_str():
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=13))
    return rand_str() + rand_str()

def aes_encrypt(data_obj, key_raw, iv_raw):
    key = key_raw.encode("utf-8")[:32]
    iv = iv_raw.encode("utf-8")[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # 和JS JSON.stringify对齐，移除多余空格，解决加密不一致
    raw_text = json.dumps(data_obj, ensure_ascii=False, separators=(',', ':')).encode("utf-8")
    encrypted = cipher.encrypt(pad(raw_text, AES.block_size, style="pkcs7"))
    return base64.b64encode(encrypted).decode("utf-8")

def make_signature(form_data, timestamp, nonce):
    key_str = get_secret_key()
    sign_str = (
        f"tel={form_data['tel']}&psw={form_data['psw']}&step={form_data['step']}"
        f"&timestamp={timestamp}&nonce={nonce}&key={key_str}"
    )
    print("=========待MD5完整字符串开始==========")
    print(repr(sign_str))
    print("=========待MD5完整字符串结束==========")

    md5_val = hashlib.md5(sign_str.encode("utf-8")).hexdigest()
    return md5_val

def main():
    # 随机步数 10005 ~ 17000
    step = random.randint(10005, 17000)
    print(f"本次随机步数：{step}")

    timestamp = str(int(time.time()))
    nonce = generate_nonce()

    form = {
        "tel": tel,
        "psw": psw,
        "step": str(step)
    }

    signature = make_signature(form, timestamp, nonce)

    payload_data = {
        "tel": tel,
        "psw": psw,
        "step": str(step),
        "timestamp": timestamp,
        "nonce": nonce,
        "signature": signature
    }

    secret_key_full = get_secret_key()
    iv_str = "1234567890123456"
    encrypted_data = aes_encrypt(payload_data, secret_key_full, iv_str)

    print(f"nonce: {nonce}")
    print(f"signature: {signature}")
    print(f"encrypted_data: {encrypted_data}\n")

    post_body = {"encrypted_data": encrypted_data}

    headers = {
        "authority": "step.wvuvw.top",
        "method": "POST",
        "path": "/",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "origin": "https://wvuvw.top",
        "referer": "https://wvuvw.top/",
        "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }

    try:
        resp = requests.post(url, json=post_body, headers=headers, timeout=15)
        print("状态码：", resp.status_code)
        print("服务器返回：", resp.text)
    except Exception as e:
        print("请求异常：", str(e))

if __name__ == "__main__":
    main()
