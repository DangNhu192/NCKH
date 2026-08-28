#!/usr/bin/env python3
"""
tools_decrypt_vault.py
──────────────────────
Công cụ dòng lệnh độc lập (CLI Tool) giúp quản trị viên:
1. Xem thông tin bảo mật và thống kê Vault.
2. Giải mã trực tiếp một chuỗi bí mật.
3. Xuất toàn bộ danh sách User, License Key và API Keys ra tệp sao lưu bản rõ (Decrypted Backup JSON).
"""

import os
import sys
import json
import base64
import hashlib
import argparse
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

VAULT_DIR = Path(__file__).resolve().parent
METADATA_FILE = VAULT_DIR / "_master_vault_metadata.json"
REGISTRY_FILE = VAULT_DIR / "users_registry.vault.json"
LICENSE_FILE = VAULT_DIR / "license_keys.vault.json"
PROFILES_DIR = VAULT_DIR / "profiles"

def load_master_secret():
    if not METADATA_FILE.exists():
        print(f"[-] Lỗi: Không tìm thấy file metadata tại {METADATA_FILE}")
        sys.exit(1)
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)
        return meta.get("master_secret"), meta.get("kdf_iterations", 100000)

def decrypt_string(encrypted_str: str, master_secret: str, iterations: int = 100000) -> str:
    if not encrypted_str or not encrypted_str.startswith("ENC:"):
        return encrypted_str
    try:
        raw_b64 = encrypted_str[4:]
        payload = json.loads(base64.b64decode(raw_b64).decode('utf-8'))
        salt_hex = payload.get("salt")
        iv = bytes.fromhex(payload.get("iv"))
        ciphertext = base64.b64decode(payload.get("ct"))

        # Derive key
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac('sha256', master_secret.encode('utf-8'), salt, iterations, dklen=32)

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        plaintext_bytes = unpadder.update(padded_data) + unpadder.finalize()
        return plaintext_bytes.decode('utf-8')
    except Exception as e:
        return f"[Lỗi giải mã: {e}]"

def show_status():
    master_secret, iters = load_master_secret()
    print("=" * 65)
    print("🔐 BÁO CÁO TRẠNG THÁI KHO BẢO MẬT (AUTH VAULT)")
    print("=" * 65)
    print(f"📁 Vị trí Vault: {VAULT_DIR}")
    print(f"🛡️ Thuật toán mã hóa: AES-256-CBC (PBKDF2-HMAC-SHA256 with {iters} rounds)")
    print(f"🔑 Master Secret Fingerprint: {hashlib.sha256(master_secret.encode()).hexdigest()[:16]}...")

    # Users count
    user_count = 0
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            user_count = len(json.load(f))
    print(f"👥 Tổng số người dùng đã đăng ký: {user_count}")

    # License count
    key_count = 0
    if LICENSE_FILE.exists():
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            key_count = len(json.load(f))
    print(f"🎫 Tổng số License Keys: {key_count}")

    # Profiles count
    profile_count = len(list(PROFILES_DIR.glob("user_*.vault.json")))
    print(f"📄 Tổng số User Profiles mã hóa: {profile_count}")
    print("=" * 65)

def export_all():
    master_secret, iters = load_master_secret()
    print("[*] Đang xuất toàn bộ dữ liệu Vault ra bản rõ...")

    export_data = {
        "export_timestamp": str(Path(__file__).stat().st_mtime),
        "users": {},
        "license_keys": [],
        "user_profiles_decrypted": {}
    }

    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            export_data["users"] = json.load(f)

    if LICENSE_FILE.exists():
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            export_data["license_keys"] = json.load(f)

    for pfile in PROFILES_DIR.glob("user_*.vault.json"):
        try:
            with open(pfile, "r", encoding="utf-8") as f:
                prof = json.load(f)
                decrypted_prof = {}
                for k, v in prof.items():
                    if isinstance(v, str) and v.startswith("ENC:"):
                        decrypted_prof[k] = decrypt_string(v, master_secret, iters)
                    else:
                        decrypted_prof[k] = v
                export_data["user_profiles_decrypted"][pfile.stem] = decrypted_prof
        except Exception as e:
            print(f"[-] Cảnh báo khi giải mã profile {pfile.name}: {e}")

    out_file = VAULT_DIR / "export_decrypted_backup.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"[+] XUẤT THÀNH CÔNG! Bản sao lưu giải mã lưu tại: {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Công cụ quản trị & giải mã Auth Vault")
    parser.add_argument("--status", action="store_true", help="Hiển thị trạng thái Vault")
    parser.add_argument("--export", action="store_true", help="Xuất bản sao lưu giải mã JSON")
    parser.add_argument("--decrypt", type=str, help="Giải mã một chuỗi ENC:...")

    args = parser.parse_args()

    if args.decrypt:
        master_secret, iters = load_master_secret()
        print("Bản rõ:", decrypt_string(args.decrypt, master_secret, iters))
    elif args.export:
        export_all()
    else:
        show_status()
