"""Optional encryption support for dotfile snapshots using symmetric key."""

import base64
import hashlib
import os
from pathlib import Path

ENV_KEY = "DOTDEPLOY_SECRET"


class EncryptError(Exception):
    pass


def _derive_key(password: str) -> bytes:
    """Derive a 32-byte key from a password string using SHA-256."""
    return hashlib.sha256(password.encode()).digest()


def _get_password() -> str:
    password = os.environ.get(ENV_KEY, "")
    if not password:
        raise EncryptError(
            f"Encryption key not set. Export {ENV_KEY} environment variable."
        )
    return password


def encrypt_data(data: bytes, password: str | None = None) -> bytes:
    """XOR-encrypt data with a key derived from password.

    Returns base64-encoded ciphertext prefixed with a random 16-byte salt.
    """
    if password is None:
        password = _get_password()
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    cipher = bytes(b ^ k for b, k in zip(data, _cycle(key, len(data))))
    return base64.b64encode(salt + cipher)


def decrypt_data(token: bytes, password: str | None = None) -> bytes:
    """Decrypt base64-encoded ciphertext produced by encrypt_data."""
    if password is None:
        password = _get_password()
    raw = base64.b64decode(token)
    salt, cipher = raw[:16], raw[16:]
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return bytes(b ^ k for b, k in zip(cipher, _cycle(key, len(cipher))))


def encrypt_file(src: Path, dst: Path, password: str | None = None) -> None:
    """Encrypt *src* and write ciphertext to *dst*."""
    if not src.exists():
        raise EncryptError(f"Source file not found: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(encrypt_data(src.read_bytes(), password))


def decrypt_file(src: Path, dst: Path, password: str | None = None) -> None:
    """Decrypt *src* and write plaintext to *dst*."""
    if not src.exists():
        raise EncryptError(f"Encrypted file not found: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(decrypt_data(src.read_bytes(), password))


def _cycle(key: bytes, length: int) -> bytes:
    """Repeat *key* until it covers *length* bytes."""
    repeats, remainder = divmod(length, len(key))
    return key * repeats + key[:remainder]
