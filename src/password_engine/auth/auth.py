from __future__ import annotations

from dataclasses import dataclass
from getpass import getuser

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from password_engine.encryption.crypto import derive_vault_key
from password_engine.db.repo import AppUserRow, PasswordRepo


@dataclass(frozen=True)
class AuthenticatedSession:
    user_id: str
    username: str
    username_normalized: str
    vault_key: bytes


class AuthService:
    """
    Handles registration, authentication, and vault-key derivation.
    """

    def __init__(self, repo: PasswordRepo) -> None:
        self.repo = repo
        self._password_hasher = PasswordHasher()

    @staticmethod
    def normalize_username(username: str | None) -> str:
        raw = (username or "").strip()
        if not raw:
            raw = getuser().strip()

        if not raw:
            raise ValueError("Username cannot be empty")

        return raw.lower()

    @staticmethod
    def clean_username(username: str | None) -> str:
        raw = (username or "").strip()
        if not raw:
            raw = getuser().strip()

        if not raw:
            raise ValueError("Username cannot be empty")

        return raw

    @staticmethod
    def validate_master_password(master_password: str) -> None:
        if not master_password:
            raise ValueError("Master password cannot be empty")
        if len(master_password) < 12:
            raise ValueError("Master password must be at least 12 characters long")

    def register_user(
        self,
        *,
        username: str | None,
        master_password: str,
    ) -> str:
        """
        Creates a new app user.

        The database generates master_key_salt automatically.
        """
        cleaned_username = self.clean_username(username)
        normalized_username = cleaned_username.lower()

        self.validate_master_password(master_password)

        existing = self.repo.get_app_user_for_auth(normalized_username)
        if existing is not None:
            raise ValueError(f"User already exists: {normalized_username}")

        master_password_hash = self._password_hasher.hash(master_password)

        return self.repo.create_app_user(
            username=cleaned_username,
            master_password_hash=master_password_hash,
            master_password_hash_algorithm="argon2id",
        )

    def authenticate_user(
        self,
        *,
        username: str | None,
        master_password: str,
    ) -> AuthenticatedSession:
        """
        Verifies the supplied master password and derives the vault key.
        """
        normalized_username = self.normalize_username(username)
        user = self.repo.get_app_user_for_auth(normalized_username)

        if user is None:
            raise ValueError("Invalid username or password")

        self._verify_master_password(
            password_hash=user.master_password_hash,
            supplied_password=master_password,
        )

        vault_key = derive_vault_key(
            master_password=master_password,
            salt=user.master_key_salt,
        )

        return AuthenticatedSession(
            user_id=user.id,
            username=user.username,
            username_normalized=user.username_normalized,
            vault_key=vault_key,
        )

    def _verify_master_password(
        self,
        *,
        password_hash: str,
        supplied_password: str,
    ) -> None:
        try:
            ok = self._password_hasher.verify(password_hash, supplied_password)
        except VerifyMismatchError as exc:
            raise ValueError("Invalid username or password") from exc
        except InvalidHashError as exc:
            raise RuntimeError("Stored password hash is invalid") from exc

        if not ok:
            raise ValueError("Invalid username or password")
