# 🔐 TÀI LIỆU QUY CHUẨN PHƯƠNG THỨC MÃ HÓA, BĂM & GIẢI MÃ DỮ LIỆU
## THƯ MỤC LƯU TRỮ BẢO MẬT: `auth_vault/` (WEB SUPER ENGINE v3.2)

---

### 1. MỤC ĐÍCH & KIẾN TRÚC KHO LƯU TRỮ (AUTH VAULT)
Thư mục `auth_vault/` là phân vùng độc lập chuyên biệt dùng để lưu trữ toàn bộ tài khoản người dùng, cấu hình cá nhân và License Key của hệ thống Web Super.

Cấu trúc thư mục:
```
auth_vault/
├── _master_vault_metadata.json          # Thông số thuật toán, Master Secret và Salt
├── users_registry.vault.json            # Danh bạ người dùng (Mật khẩu băm PBKDF2-SHA256)
├── license_keys.vault.json              # Danh sách License Key (Có chữ ký số HMAC-SHA256)
├── PHUONG_THUC_MA_HOA_VA_GIAI_MA.md      # Tài liệu này (Hướng dẫn giải mã chi tiết)
├── tools_decrypt_vault.py               # Script giải mã & xuất bản rõ độc lập 1-Click
└── profiles/                            # Thư mục cấu hình từng người dùng
    └── user_{user_id}.vault.json        # API Keys (Gemini, OpenAI, Zotero) mã hóa AES-256
```

---

### 2. PHƯƠNG THỨC BĂM MẬT KHẨU (ONE-WAY HASHING)
* **Thuật toán**: `PBKDF2-HMAC-SHA256`
* **Số vòng lặp (Iterations)**: `100.000` vòng.
* **Salt**: Chuỗi ngẫu nhiên 16 bytes (32 ký tự hex) sinh riêng cho từng tài khoản (`secrets.token_hex(16)`).
* **Định dạng chuỗi lưu trữ**:
  ```
  pbkdf2:sha256:100000$[SALT_HEX]$[HASH_HEX]
  ```
* **Tính chất**: Băm một chiều, không thể dịch ngược, chống tấn công từ điển (Rainbow Tables) và tấn công Brute-force.

---

### 3. PHƯƠNG THỨC MÃ HÓA ĐỐI XỨNG KHẢ NGHỊCH (REVERSIBLE AES-256 ENCRYPTION)
Dùng để mã hóa các thông tin nhạy cảm cần giải mã khi gọi AI: `gemini_api_key`, `openai_api_key`, `zotero_api_key`.

* **Thuật toán mã hóa**: `AES-256-CBC` (Advanced Encryption Standard 256-bit, Cipher Block Chaining).
* **Độn dữ liệu (Padding)**: `PKCS7` (block size 128-bit).
* **Khóa dẫn xuất (Key Derivation - KDF)**:
  - Khóa AES 32 bytes (256-bit) được dẫn xuất từ `master_secret` kết hợp với `salt_hex` ngẫu nhiên thông qua `PBKDF2-HMAC-SHA256` (100.000 vòng).
* **Vectơ khởi tạo (IV)**: Sinh ngẫu nhiên 16 bytes cho mỗi lần mã hóa (`secrets.token_bytes(16)`).
* **Cấu trúc chuỗi mã hóa lưu trong file**:
  ```json
  ENC:base64({
    "enc_v": "2.0",
    "alg": "AES-256-CBC",
    "salt": "3a8f... [16-byte hex]",
    "iv": "1b2c... [16-byte hex]",
    "ct": "k8X2... [Ciphertext Base64]"
  })
  ```

---

### 4. PHƯƠNG THỨC KÝ SỐ LICENSE KEY (HMAC-SHA256 SIGNATURE)
* Mỗi License Key khi phát hành đều được gắn kèm một chữ ký số:
  $$	ext{Signature} = 	ext{HMAC-SHA256}(	ext{Key} \parallel 	ext{Plan} \parallel 	ext{Duration} \parallel 	ext{MasterSalt}, 	ext{MasterSecret})$$
* Giúp ngăn chặn 100% hành vi tự sửa đổi gói (Standard -> Pro -> Enterprise) hoặc sửa ngày hết hạn trong file json.

---

### 5. HƯỚNG DẪN GIẢI MÃ & XUẤT BẢN RÕ 1-CLICK (RECOVERY / DECRYPTION)

Khi bạn muốn kiểm tra, xem bản rõ hoặc xuất toàn bộ dữ liệu ra tệp sao lưu JSON không mã hóa:

#### Cách 1: Chạy Script Giải Mã Tự Động
Mở Terminal / Command Prompt tại thư mục `Web Super` và chạy lệnh:
```bash
python auth_vault/tools_decrypt_vault.py --export
```
Script sẽ tự động:
1. Đọc `_master_vault_metadata.json` lấy `master_secret`.
2. Giải mã toàn bộ API Keys trong `profiles/`.
3. Xuất file `auth_vault/export_decrypted_backup.json` đầy đủ bản rõ để xem hoặc sao lưu.

#### Cách 2: Giải mã trực tiếp bằng Python Code ngắn:
```python
from modules.auth.vault_crypto_engine import vault_crypto

# Giải mã một chuỗi bất kỳ:
plain_text = vault_crypto.decrypt_secret(encrypted_string)
print("Bản rõ:", plain_text)
```

---
*Tài liệu được sinh tự động bởi Web Super Engine v3.2 — Đảm bảo an toàn tuyệt đối và tính minh bạch 100%.*
