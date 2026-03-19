from __future__ import annotations

import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from hashlib import scrypt


@dataclass(frozen=True)
class EncryptedSecret:
    ciphertext: bytes
    nonce: bytes
    key_version: int = 1


DEFAULT_KEY_VERSION = 1
NONCE_SIZE = 12
KEY_SIZE = 32


def derive_vault_key(
    *,
    master_password: str,
    salt: bytes,
    key_len: int = KEY_SIZE,
) -> bytes:
    """
    Derives a stable vault encryption key from the user's master password.

    Uses scrypt with a per-user salt stored in app_user.master_key_salt.
    """
    if not master_password:
        raise ValueError("Master password cannot be empty")

    if not salt:
        raise ValueError("Salt cannot be empty")

    return scrypt(
        password=master_password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=key_len,
    )


def encrypt_secret(
    *,
    plaintext: str,
    key: bytes,
    key_version: int = DEFAULT_KEY_VERSION,
) -> EncryptedSecret:
    """
    Encrypts a site password for database storage.
    """
    if not plaintext:
        raise ValueError("Plaintext secret cannot be empty")

    if len(key) != KEY_SIZE:
        raise ValueError(f"Encryption key must be {KEY_SIZE} bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), associated_data=None)

    return EncryptedSecret(
        ciphertext=ciphertext,
        nonce=nonce,
        key_version=key_version,
    )


def decrypt_secret(
    *,
    ciphertext: bytes,
    nonce: bytes,
    key: bytes,
) -> str:
    """
    Decrypts a stored site password from the database.
    """
    if not ciphertext:
        raise ValueError("Ciphertext cannot be empty")

    if not nonce:
        raise ValueError("Nonce cannot be empty")

    if len(key) != KEY_SIZE:
        raise ValueError(f"Encryption key must be {KEY_SIZE} bytes")

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)

    return plaintext.decode("utf-8")
