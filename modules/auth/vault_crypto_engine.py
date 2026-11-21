"""
vault_crypto_engine.py
──────────────────────
Hệ thống mã hóa, băm mật khẩu và quản trị kho dữ liệu bảo mật (Auth Vault v2.0).
Tích hợp:
1. PBKDF2-HMAC-SHA256 (100.000 vòng) cho Mật khẩu và Chữ ký License Key.
2. AES-256-CBC / Fernet Key Derivation cho dữ liệu nhạy cảm (API Keys, Zotero Tokens).
3. Đầy đủ cơ chế Giải mã (Decryption) và Khôi phục (Recovery) minh bạch.
"""

import os
import json
import base64
import hashlib
import hmac
import secrets
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

import tempfile
IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
if IS_VERCEL:
    VAULT_DIR = Path(tempfile.gettempdir()) / "auth_vault"
else:
    VAULT_DIR = Path(__file__).resolve().parent.parent.parent / "auth_vault"
VAULT_METADATA_FILE = VAULT_DIR / "_master_vault_metadata.json"
VAULT_PROFILES_DIR = VAULT_DIR / "profiles"

DEFAULT_ITERATIONS = 100000
DEFAULT_ALGORITHM = "AES-256-CBC"

class VaultCryptoEngine:
    def __init__(self):
        try:
            VAULT_DIR.mkdir(parents=True, exist_ok=True)
        except (OSError, FileNotFoundError):
            pass
        try:
            VAULT_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        except (OSError, FileNotFoundError):
            pass
        self.master_secret, self.master_salt = self._init_or_load_master_metadata()

    def _init_or_load_master_metadata(self) -> Tuple[str, str]:
        # Ưu tiên khóa từ biến môi trường (bắt buộc trên Vercel / máy chủ thật)
        env_secret = os.getenv("VAULT_MASTER_SECRET", "").strip()
        env_salt = os.getenv("VAULT_MASTER_SALT", "").strip()
        if env_secret and env_salt:
            return env_secret, env_salt
        if IS_VERCEL:
            # Dự phòng: khóa ổn định theo lần deploy để mọi máy chủ giải mã được như nhau
            from modules.auth.auth_service import derive_deployment_secret
            derived = derive_deployment_secret("vault")
            if derived:
                return derived, derive_deployment_secret("vault-salt")[:32]

        if VAULT_METADATA_FILE.exists():
            try:
                with open(VAULT_METADATA_FILE, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    return meta.get("master_secret"), meta.get("master_salt")
            except Exception:
                pass

        # Khởi tạo khóa bảo mật Master Vault
        master_secret = secrets.token_hex(32)  # 256-bit entropy
        master_salt = secrets.token_hex(16)    # 128-bit salt
        metadata = {
            "vault_version": "2.0-VAULT-PRO",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cipher": DEFAULT_ALGORITHM,
            "kdf": "PBKDF2-HMAC-SHA256",
            "kdf_iterations": DEFAULT_ITERATIONS,
            "master_salt": master_salt,
            "master_secret": master_secret,
            "description": "Kho lưu trữ mã hóa người dùng và License Keys của Web Super.",
            "recovery_guide": "Xem tệp PHUONG_THUC_MA_HOA_VA_GIAI_MA.md và chạy tools_decrypt_vault.py để giải mã."
        }
        try:
            with open(VAULT_METADATA_FILE, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            os.chmod(VAULT_METADATA_FILE, 0o600)
        except OSError:
            pass

        return master_secret, master_salt

    def _derive_key(self, salt_hex: str) -> bytes:
        """Dẫn xuất khóa AES 256-bit từ Master Secret và Salt bằng PBKDF2-HMAC-SHA256"""
        salt = bytes.fromhex(salt_hex)
        return hashlib.pbkdf2_hmac(
            'sha256',
            self.master_secret.encode('utf-8'),
            salt,
            DEFAULT_ITERATIONS,
            dklen=32  # 32 bytes = 256 bits
        )

    def hash_password(self, password: str) -> str:
        """Băm mật khẩu người dùng chuẩn PBKDF2-HMAC-SHA256 (100.000 vòng) kèm Salt"""
        if not password:
            return ""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            DEFAULT_ITERATIONS,
            dklen=32
        ).hex()
        return f"pbkdf2:sha256:{DEFAULT_ITERATIONS}${salt}${pwd_hash}"

    def verify_password(self, password: str, hashed_str: str) -> bool:
        """Xác thực mật khẩu đối chiếu với chuỗi băm"""
        if not password or not hashed_str or not hashed_str.startswith("pbkdf2:sha256:"):
            return False
        try:
            parts = hashed_str.split("$")
            if len(parts) != 3:
                return False
            iterations = int(parts[0].split(":")[-1])
            salt = parts[1]
            target_hash = parts[2]
            computed = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations,
                dklen=32
            ).hex()
            return hmac.compare_digest(computed, target_hash)
        except Exception:
            return False

    def encrypt_secret(self, plaintext: str) -> str:
        """Mã hóa chuỗi nhạy cảm (API Keys, Zotero Tokens) bằng AES-256-CBC PKCS7 hoặc stream fallback"""
        if not plaintext:
            return ""
        salt_hex = secrets.token_hex(16)
        key = self._derive_key(salt_hex)
        
        if HAS_CRYPTOGRAPHY:
            iv = secrets.token_bytes(16)
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()

            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()

            payload = {
                "enc_v": "2.0",
                "alg": DEFAULT_ALGORITHM,
                "salt": salt_hex,
                "iv": iv.hex(),
                "ct": base64.b64encode(ciphertext).decode('utf-8')
            }
        else:
            plain_bytes = plaintext.encode('utf-8')
            stream = hashlib.sha256(key + salt_hex.encode()).digest()
            while len(stream) < len(plain_bytes):
                stream += hashlib.sha256(stream).digest()
            ct = bytes([b ^ s for b, s in zip(plain_bytes, stream[:len(plain_bytes)])])
            payload = {
                "enc_v": "2.0-fallback",
                "alg": "XOR-SHA256",
                "salt": salt_hex,
                "iv": "",
                "ct": base64.b64encode(ct).decode('utf-8')
            }
        return "ENC:" + base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')

    def decrypt_secret(self, encrypted_str: str) -> str:
        """Giải mã chuỗi AES-256-CBC về bản rõ"""
        if not encrypted_str:
            return ""
        if not encrypted_str.startswith("ENC:"):
            return encrypted_str  # Chưa mã hóa, trả về nguyên bản (tương thích ngược)
        try:
            raw_b64 = encrypted_str[4:]
            payload_bytes = base64.b64decode(raw_b64)
            payload = json.loads(payload_bytes.decode('utf-8'))

            salt_hex = payload.get("salt")
            iv = bytes.fromhex(payload.get("iv"))
            ciphertext = base64.b64decode(payload.get("ct"))

            key = self._derive_key(salt_hex)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()

            unpadder = padding.PKCS7(128).unpadder()
            plaintext_bytes = unpadder.update(padded_data) + unpadder.finalize()
            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            return ""

    def sign_license_key(self, key_string: str, plan: str, days: int) -> str:
        """Tạo chữ ký số HMAC-SHA256 cho License Key nhằm chống giả mạo"""
        msg = f"{key_string}|{plan}|{days}|{self.master_salt}"
        return hmac.new(self.master_secret.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).hexdigest()

    def verify_license_key_signature(self, key_string: str, plan: str, days: int, signature: str) -> bool:
        """Kiểm tra chữ ký số HMAC của License Key"""
        expected = self.sign_license_key(key_string, plan, days)
        return hmac.compare_digest(expected, signature)

vault_crypto = VaultCryptoEngine()
