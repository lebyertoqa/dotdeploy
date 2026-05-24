"""Tests for dotdeploy.encrypt and dotdeploy.cli_encrypt."""

import os
from pathlib import Path

import pytest

from dotdeploy.encrypt import (
    EncryptError,
    _cycle,
    decrypt_data,
    decrypt_file,
    encrypt_data,
    encrypt_file,
)

PASSWORD = "s3cr3t"
PLAINTEXT = b"Hello, dotdeploy encryption!"


# ---------------------------------------------------------------------------
# Unit tests for encrypt_data / decrypt_data
# ---------------------------------------------------------------------------

def test_encrypt_returns_bytes():
    token = encrypt_data(PLAINTEXT, PASSWORD)
    assert isinstance(token, bytes)


def test_encrypt_decrypt_roundtrip():
    token = encrypt_data(PLAINTEXT, PASSWORD)
    assert decrypt_data(token, PASSWORD) == PLAINTEXT


def test_different_salts_each_call():
    t1 = encrypt_data(PLAINTEXT, PASSWORD)
    t2 = encrypt_data(PLAINTEXT, PASSWORD)
    assert t1 != t2  # different random salts


def test_wrong_password_gives_garbage():
    token = encrypt_data(PLAINTEXT, PASSWORD)
    result = decrypt_data(token, "wrongpassword")
    assert result != PLAINTEXT


def test_missing_env_key_raises(monkeypatch):
    monkeypatch.delenv("DOTDEPLOY_SECRET", raising=False)
    with pytest.raises(EncryptError, match="DOTDEPLOY_SECRET"):
        encrypt_data(PLAINTEXT)  # no explicit password


def test_env_key_used_when_no_password(monkeypatch):
    monkeypatch.setenv("DOTDEPLOY_SECRET", PASSWORD)
    token = encrypt_data(PLAINTEXT)
    assert decrypt_data(token) == PLAINTEXT


# ---------------------------------------------------------------------------
# File-level helpers
# ---------------------------------------------------------------------------

def test_encrypt_file_creates_output(tmp_path):
    src = tmp_path / "plain.txt"
    src.write_bytes(PLAINTEXT)
    dst = tmp_path / "plain.txt.enc"
    encrypt_file(src, dst, PASSWORD)
    assert dst.exists()
    assert dst.read_bytes() != PLAINTEXT


def test_decrypt_file_roundtrip(tmp_path):
    src = tmp_path / "plain.txt"
    src.write_bytes(PLAINTEXT)
    enc = tmp_path / "plain.txt.enc"
    dec = tmp_path / "plain.txt.dec"
    encrypt_file(src, enc, PASSWORD)
    decrypt_file(enc, dec, PASSWORD)
    assert dec.read_bytes() == PLAINTEXT


def test_encrypt_file_missing_source_raises(tmp_path):
    with pytest.raises(EncryptError, match="Source file not found"):
        encrypt_file(tmp_path / "ghost.txt", tmp_path / "out.enc", PASSWORD)


def test_decrypt_file_missing_source_raises(tmp_path):
    with pytest.raises(EncryptError, match="Encrypted file not found"):
        decrypt_file(tmp_path / "ghost.enc", tmp_path / "out.txt", PASSWORD)


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def test_cycle_exact_multiple():
    assert _cycle(b"AB", 4) == b"ABAB"


def test_cycle_with_remainder():
    assert _cycle(b"ABC", 5) == b"ABCAB"
