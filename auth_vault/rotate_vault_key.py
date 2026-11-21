"""
Xoay khóa Master Vault của WEB SUPER.

Khóa cũ (master_secret / master_salt) từng bị commit công khai lên GitHub, nên mọi
API key người dùng được mã hóa bằng nó coi như đã lộ. Công cụ này:
  1. Giải mã mọi giá trị "ENC:..." trong auth_vault/**/*.json bằng khóa cũ
  2. Mã hóa lại bằng khóa mới (ngẫu nhiên hoặc lấy từ VAULT_MASTER_SECRET / VAULT_MASTER_SALT)
  3. Ký lại chữ ký HMAC của License Key
  4. Ghi khóa mới vào auth_vault/_master_vault_metadata.json (tệp này nằm trong .gitignore)

Cách dùng (chạy từ thư mục gốc dự án):
    python auth_vault/rotate_vault_key.py            # chạy thử, không ghi gì
    python auth_vault/rotate_vault_key.py --apply    # thực hiện (tự sao lưu trước)

Sau khi xoay khóa, nên khuyên người dùng đổi luôn các API key (Gemini, OpenAI, Zotero...) đã lưu.
"""

import argparse
import json
import os
import secrets
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

VAULT_DIR = ROOT / "auth_vault"
META_FILE = VAULT_DIR / "_master_vault_metadata.json"

# Khóa cũ ĐÃ BỊ LỘ (từng nằm trong git). Chỉ dùng để giải mã dữ liệu cũ khi chuyển sang khóa mới.
LEGACY_LEAKED_SECRET = "d84bb513634462b6fab08220d1139239c973f26ede509a68be4b11d4f8fad64a"
LEGACY_LEAKED_SALT = "ef7237cf481123882b3bd2c7a3ad1cff"


def make_engine(secret: str, salt: str):
    from modules.auth.vault_crypto_engine import VaultCryptoEngine
    eng = VaultCryptoEngine.__new__(VaultCryptoEngine)
    eng.master_secret, eng.master_salt = secret, salt
    return eng


def walk(obj, fn):
    if isinstance(obj, dict):
        return {k: walk(v, fn) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk(v, fn) for v in obj]
    return fn(obj)


def main():
    ap = argparse.ArgumentParser(description="Xoay khóa Master Vault WEB SUPER")
    ap.add_argument("--apply", action="store_true", help="Ghi thay đổi (mặc định chỉ chạy thử)")
    ap.add_argument("--old-secret", help="master_secret cũ (mặc định: đọc từ metadata hoặc khóa đã lộ)")
    ap.add_argument("--old-salt", help="master_salt cũ")
    args = ap.parse_args()

    old_secret, old_salt = args.old_secret, args.old_salt
    if not (old_secret and old_salt) and META_FILE.exists():
        meta = json.loads(META_FILE.read_text(encoding="utf-8"))
        old_secret, old_salt = meta.get("master_secret"), meta.get("master_salt")
    if not (old_secret and old_salt):
        old_secret, old_salt = LEGACY_LEAKED_SECRET, LEGACY_LEAKED_SALT

    new_secret = os.getenv("VAULT_MASTER_SECRET", "").strip() or secrets.token_hex(32)
    new_salt = os.getenv("VAULT_MASTER_SALT", "").strip() or secrets.token_hex(16)
    if new_secret == old_secret:
        print("Khóa mới trùng khóa cũ – hãy đặt VAULT_MASTER_SECRET khác hoặc bỏ trống để tạo ngẫu nhiên.")
        return 1

    old_eng, new_eng = make_engine(old_secret, old_salt), make_engine(new_secret, new_salt)
    stats = {"files": 0, "values": 0, "failed": 0, "licenses": 0}
    results = {}

    def reencrypt(v):
        if isinstance(v, str) and v.startswith("ENC:"):
            plain = old_eng.decrypt_secret(v)
            if not plain:
                stats["failed"] += 1
                return v
            stats["values"] += 1
            return new_eng.encrypt_secret(plain)
        return v

    for path in sorted(VAULT_DIR.rglob("*.json")):
        if path.name == META_FILE.name or "backup" in path.parts[-2].lower():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        new_data = walk(data, reencrypt)
        records = new_data if isinstance(new_data, list) else (list(new_data.values()) if isinstance(new_data, dict) else [])
        for rec in records:
            if isinstance(rec, dict) and rec.get("hmac_signature") and rec.get("key") and rec.get("plan"):
                if old_eng.verify_license_key_signature(rec["key"], rec["plan"], rec["duration_days"], rec["hmac_signature"]):
                    rec["hmac_signature"] = new_eng.sign_license_key(rec["key"], rec["plan"], rec["duration_days"])
                    stats["licenses"] += 1
        if new_data != data:
            stats["files"] += 1
            results[path] = new_data

    print(f"Tệp cần cập nhật: {stats['files']} | Giá trị mã hóa lại: {stats['values']} | "
          f"Không giải mã được: {stats['failed']} | License ký lại: {stats['licenses']}")
    if not args.apply:
        print("Chạy thử xong. Thêm --apply để thực hiện.")
        return 0

    backup = VAULT_DIR / f"backup_before_rotate_{datetime.now():%Y%m%d_%H%M%S}"
    backup.mkdir()
    for path in results:
        dest = backup / path.relative_to(VAULT_DIR)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    if META_FILE.exists():
        shutil.copy2(META_FILE, backup / META_FILE.name)

    for path, data in results.items():
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    meta = {
        "vault_version": "2.0-VAULT-PRO",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cipher": "AES-256-CBC",
        "kdf": "PBKDF2-HMAC-SHA256",
        "kdf_iterations": 100000,
        "master_salt": new_salt,
        "master_secret": new_secret,
        "description": "Khóa Master Vault (KHÔNG commit tệp này). Trên Vercel đặt VAULT_MASTER_SECRET / VAULT_MASTER_SALT.",
    }
    META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(META_FILE, 0o600)
    except OSError:
        pass
    print(f"Đã xoay khóa. Bản sao lưu: {backup}")
    print("LƯU Ý: thư mục sao lưu vẫn chứa dữ liệu mã hóa bằng khóa cũ – xóa nó sau khi kiểm tra xong.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
