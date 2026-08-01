import time
import random
import json
from datetime import datetime
import os

# =================【配置区】================
RECORD_FILE = "run_record.json"
MAX_DAILY_RUN = 3        # 每日最多执行3次
MAX_WAIT_SEC = 10 * 60   # 选中执行才会等待：0~10分钟
RANDOM_RATE = 0.25       # 单次触发执行概率25%，12次期望≈3次
# ============================================

# 获取北京时间日期字符串
def get_beijing_date_str():
    return datetime.now().strftime("%Y-%m-%d")

# 读取运行记录
def load_record():
    if not os.path.exists(RECORD_FILE):
        return {"today":"","exec_count":0}
    with open(RECORD_FILE,"r",encoding="utf-8") as f:
        return json.load(f)

# 保存记录并提交git
def save_record(data):
    with open(RECORD_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    os.system("git config --global user.name 'Github Action'")
    os.system("git config --global user.email 'action@github.com'")
    os.system("git add "+RECORD_FILE)
    os.system("git commit -m 'update run record'")
    os.system("git push")

def main():
    today = get_beijing_date_str()
    record = load_record()

    # 跨天重置计数器
    if record["today"] != today:
        record["today"] = today
        record["exec_count"] = 0
        save_record(record)

    print(f"今日日期:{today},已执行次数:{record['exec_count']}")

    # 条件1：今日次数已满，直接退出【不等待】
    if record["exec_count"] >= MAX_DAILY_RUN:
        print("今日已达到最大执行次数，直接退出")
        return

    # 条件2：随机抽签不执行，直接退出【不等待】
    if random.random() > RANDOM_RATE:
        print("本次抽签不执行任务，直接退出")
        return

    # ========== 只有走到这里，才是真正要执行任务 ==========
    wait = random.randint(0, MAX_WAIT_SEC)
    print(f"本次有效任务，随机等待 {wait//60}分{wait%60}秒")
    time.sleep(wait)

    # ============业务脚本（刷步数逻辑）=============
    step = random.randint(10005, 17000)
    print(f"本次随机步数：{step}")

    timestamp = str(int(time.time()))
    nonce = generate_nonce()

    form = {
        "tel": os.getenv("ACCOUNT_TEL"),
        "psw": os.getenv("ACCOUNT_PSW"),
        "step": str(step)
    }

    signature = make_signature(form, timestamp, nonce)

    payload_data = {
        "tel": os.getenv("ACCOUNT_TEL"),
        "psw": os.getenv("ACCOUNT_PSW"),
        "step": str(step),
        "timestamp": timestamp,
        "nonce": nonce,
        "signature": signature
    }

    secret_key_full = get_secret_key()
    iv_str = "1234567890123456"
    encrypted_data = aes_encrypt(payload_data, secret_key_full, iv_str)

    post_body = {"encrypted_data": encrypted_data}

    headers = {
        "authority": "step.wvuvw.top",
        "method": "POST",
        "path": "/",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json",
        "origin": "https://wvuvw.top",
        "referer": "https://wvuvw.top/",
        "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }

    try:
        import requests
        resp = requests.post("https://step.wvuvw.top", json=post_body, headers=headers, timeout=15)
        print("状态码：", resp.status_code)
        print("接口返回：", resp.text)
        # 请求成功，计数增加
        record["exec_count"] += 1
        save_record(record)
    except Exception as e:
        print("请求异常：", str(e))

# 工具函数
def get_secret_key():
    arr = ['fanTui2024', 'SecretKey', '1234567890', '1234567890', '1234567890', '1234567890']
    return "".join(arr)

def generate_nonce():
    def rand_str():
        return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=13))
    return rand_str() + rand_str()

def aes_encrypt(data_obj, key_raw, iv_raw):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    import base64
    import json
    key = key_raw.encode("utf-8")[:32]
    iv = iv_raw.encode("utf-8")[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    raw = json.dumps(data_obj, ensure_ascii=False, separators=(',', ':')).encode("utf-8")
    enc = cipher.encrypt(pad(raw, AES.block_size))
    return base64.b64encode(enc).decode("utf-8")

def make_signature(form_data, ts, nc):
    import hashlib
    key_str = get_secret_key()
    sign_raw = f"tel={form_data['tel']}&psw={form_data['psw']}&step={form_data['step']}&timestamp={ts}&nonce={nc}&key={key_str}"
    return hashlib.md5(sign_raw.encode("utf-8")).hexdigest()

if __name__ == "__main__":
    main()
