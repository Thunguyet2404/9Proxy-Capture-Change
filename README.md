# 9Proxy Capture Tool

Công cụ tự động quét, kiểm tra bandwidth (GB), mã codes và đổi mật khẩu hàng loạt cho tài khoản 9Proxy.

> Author: **[T.ME/hieunguyen2907](https://t.me/hieunguyen2907)**

---

## Mục lục

- [Tính năng](#tính-năng)
- [Yêu cầu](#yêu-cầu)
- [Cài đặt](#cài-đặt)
- [Cấu hình](#cấu-hình)
- [Cách sử dụng](#cách-sử-dụng)
- [Kết quả đầu ra](#kết-quả-đầu-ra)
- [Kiến trúc mã nguồn](#kiến-trúc-mã-nguồn)
- [Lưu ý](#lưu-ý)

---

## Tính năng

| Tính năng | Mô tả |
|---|---|
| **Check GB** | Quét bandwidth còn lại (Basic + Enterprise) qua Selenium |
| **Check Codes** | Quét danh sách share codes đã tạo trên tài khoản |
| **Full Scan** | Quét đồng thời GB + Codes (all-in-one) |
| **Password Reset** | Đổi mật khẩu hàng loạt qua API |
| **Multi-thread** | Hỗ trợ chạy nhiều luồng song song (tối đa 20 threads) |
| **Auto ChromeDriver** | Tự động tải và cấu hình ChromeDriver phù hợp |
| **Email Verification** | Xác minh đúng tài khoản đang đăng nhập trên browser |
| **Smart Retry** | Tự động thử lại khi gặp lỗi đăng nhập hoặc đổi pass |

---

## Yêu cầu

- Python 3.7+
- Google Chrome (đã cài đặt trên máy)
- Hệ điều hành: Windows / Linux / macOS

### Thư viện Python

```
selenium >= 4.15.0
webdriver-manager >= 4.0.0
requests >= 2.31.0
rich >= 13.0.0
```

---

## Cài đặt

```bash
git clone https://github.com/Thunguyet2404/9Proxy-Capture-Change.git
cd 9proxy-capture
pip install -r requirements.txt
```

---

## Cấu hình

Tạo file `account.txt` cùng thư mục với `main.py`, mỗi dòng chứa một tài khoản theo định dạng:

```
email1@example.com:password1
email2@example.com:password2
email3@example.com:password3
```

> **Lưu ý:** Các dòng trống hoặc bắt đầu bằng `#` sẽ bị bỏ qua.

---

## Cách sử dụng

```bash
python main.py
```

Sau khi chạy, tool sẽ hiển thị menu chọn chức năng:

```
[1] check-gb       → Scan bandwidth
[2] check-codes    → Scan generated codes
[3] full-scan      → GB + Codes (all-in-one)
[4] passwd-reset   → Change password
[0] exit
```

Nhập số tương ứng và Enter. Tool sẽ hỏi số threads (mặc định từ 3-15 tùy module).

---

## Kết quả đầu ra

| Module | File kết quả | Nội dung |
|---|---|---|
| Check GB | `results_gb.txt` | `email:pass\|Basic:XGB\|Enterprise:YGB` |
| Check Codes | `results_codes.txt` | `email:pass\|Codes:N\|TotalGB:X\|code1(XGB);code2(YGB)` |
| Full Scan | `results_full.txt` | `email:pass\|GB:X\|Codes:N\|CodeGB:Y\|code1,code2` |
| Password Reset | `results_changed.txt` | `email:newpass` |
| Password Reset | `results_backup.txt` | `email:newpass\|OLD:oldpass` |

---

## Kiến trúc mã nguồn

```
9Proxy Capture/
├── main.py              # Script chính
├── requirements.txt     # Danh sách thư viện cần cài
├── account.txt          # File chứa tài khoản (tự tạo)
├── results_gb.txt       # Kết quả check GB (tự động tạo)
├── results_codes.txt    # Kết quả check codes (tự động tạo)
├── results_full.txt     # Kết quả full scan (tự động tạo)
├── results_changed.txt  # Kết quả đổi pass (tự động tạo)
├── results_backup.txt   # Backup pass cũ (tự động tạo)
└── README.md            # Tài liệu hướng dẫn
```

### Luồng hoạt động

```
account.txt
    │
    ▼
 Login API ──► Lấy Access/Refresh Token
    │
    ├──► [Check GB]     Selenium → 9proxy.com/dashboard → Parse GB
    ├──► [Check Codes]  Selenium → 9proxy.com/share-code → Parse Table
    ├──► [Full Scan]    Kết hợp cả GB + Codes
    └──► [Passwd Reset] API change-password → Ghi kết quả
```

### Các module chính

| Module | Chức năng |
|---|---|
| `login()` | Đăng nhập API, lấy access/refresh token |
| `change_password_api()` | Gọi API đổi mật khẩu |
| `make_driver()` | Khởi tạo Chrome headless với anti-detect |
| `fetch_gb()` | Lấy thông tin GB bằng Selenium + JS injection |
| `fetch_codes()` | Lấy danh sách codes từ bảng Ant Design |
| `worker_*()` | Các hàm worker chạy trong từng thread |
| `run_task()` | Điều phối chạy đa luồng và tổng kết |

---

## Lưu ý

> ⚠️ **Tool chỉ dùng cho mục đích học tập và nghiên cứu.**

- Cần có Google Chrome đã cài sẵn trên máy.
- ChromeDriver sẽ được tự động tải về lần đầu chạy. 
- Với module Check GB / Codes / Full Scan, nên dùng 3-5 threads để tránh bị rate-limit.
- Module Password Reset có thể dùng nhiều threads hơn (10-15) vì chỉ dùng API.
- File `results_backup.txt` lưu lại mật khẩu cũ để có thể rollback nếu cần.

---

## Liên hệ

- **Telegram**: [t.me/hieunguyen2907](https://t.me/hieunguyen2907)

