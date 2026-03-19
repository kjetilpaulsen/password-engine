from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from getpass import getuser
from typing import Any

import psycopg
from psycopg.rows import tuple_row

from password_engine.db import queries as q

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AppUserRow:
    id: str
    username: str
    username_normalized: str
    master_password_hash: str
    master_password_hash_algorithm: str
    master_key_salt: bytes
    created_at: datetime
    updated_at: datetime

@dataclass(frozen=True)
class VaultEntryRow:
    id: str
    tag: str
    site_username: str | None
    site_email: str | None
    site_url: str | None
    encrypted_password: bytes
    encryption_nonce: bytes
    encryption_key_version: int
    created_at: datetime
    updated_at: datetime


@dataclass
class PasswordRepo:
    """
    Repository for password-engine persistence.

    Params:
    - conn: an open psycopg connection
    """

    conn: psycopg.Connection

    # Local methods
    def _execute(self, sql: str, params: tuple | None = None) -> int:
        with self.conn.cursor() as cur:
            cur.execute(sql, params or ())  # type: ignore[]
            rc = cur.rowcount
        self.conn.commit()
        return 0 if rc is None or rc < 0 else int(rc)

    def _fetchone(self, sql: str, params: tuple | None = None) -> tuple[Any, ...] | None:
        with self.conn.cursor(row_factory=tuple_row) as cur:
            cur.execute(sql, params or ())  # type: ignore[]
            return cur.fetchone()

    def _fetchall(self, sql: str, params: tuple | None = None) -> list[tuple[Any, ...]]:
        with self.conn.cursor(row_factory=tuple_row) as cur:
            cur.execute(sql, params or ())  # type: ignore[]
            return cur.fetchall()

    def _scalar(self, sql: str, params: tuple | None = None) -> Any | None:
        row = self._fetchone(sql, params)
        return None if row is None else row[0]

    # Local helpers
    def _clean_username(self, username: str | None) -> str:
        """
        Normalizes the app username.

        If username is empty or only whitespace, the current system user is used.
        """
        raw = (username or "").strip()
        if not raw:
            raw = getuser().strip()

        if not raw:
            raise ValueError("Username cannot be empty")

        return raw

    def _normalize_username(self, username: str | None) -> str:
        return self._clean_username(username).lower()

    def _clean_required_tag(self, tag: str) -> str:
        cleaned = tag.strip()
        if not cleaned:
            raise ValueError("Tag cannot be empty")
        return cleaned

    def _optional_text_or_none(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _row_to_app_user(self, row: tuple[Any, ...]) -> AppUserRow:
        return AppUserRow(
            id=str(row[0]),
            username=str(row[1]),
            username_normalized=str(row[2]),
            master_password_hash=str(row[3]),
            master_password_hash_algorithm=str(row[4]),
            master_key_salt=bytes(row[5]),
            created_at=row[6],
            updated_at=row[7],
    )

    def _row_to_vault_entry(self, row: tuple[Any, ...]) -> VaultEntryRow:
        return VaultEntryRow(
            id=str(row[0]),
            tag=str(row[1]),
            site_username=row[2],
            site_email=row[3],
            site_url=row[4],
            encrypted_password=bytes(row[5]),
            encryption_nonce=bytes(row[6]),
            encryption_key_version=int(row[7]),
            created_at=row[8],
            updated_at=row[9],
        )

    # Methods
    def create_app_user(
        self,
        *,
        username: str | None,
        master_password_hash: str,
        master_password_hash_algorithm: str = "argon2id",
    ) -> str:
        """
        Inserts a new app user and returns its UUID as a string.

        The hash must already have been created in the calling layer.
        """
        cleaned_username = self._clean_username(username)
        username_normalized = cleaned_username.lower()

        user_id = self._scalar(
            q.INSERT_APP_USER,
            (
                cleaned_username,
                username_normalized,
                master_password_hash,
                master_password_hash_algorithm,
            ),
        )
        self.conn.commit()

        if user_id is None:
            raise RuntimeError("Failed to fetch user id after insert")

        return str(user_id)

    def get_app_user_for_auth(self, username: str | None) -> AppUserRow | None:
        """
        Fetches the app user row needed for authentication.

        The calling layer should verify the supplied password against
        master_password_hash.
        """
        username_normalized = self._normalize_username(username)
        row = self._fetchone(q.FETCH_APP_USER_BY_USERNAME_NORMALIZED, (username_normalized,))
        if row is None:
            return None
        return self._row_to_app_user(row)

    def insert_vault_entry(
        self,
        *,
        owner_user_id: str,
        tag: str,
        encrypted_password: bytes,
        encryption_nonce: bytes,
        encryption_key_version: int = 1,
        site_username: str | None = None,
        site_email: str | None = None,
        site_url: str | None = None,
    ) -> str:
        """
        Inserts a vault entry and returns its UUID as a string.

        The password must already have been encrypted in the calling layer.
        """
        cleaned_tag = self._clean_required_tag(tag)

        entry_id = self._scalar(
            q.INSERT_VAULT_ENTRY,
            (
                owner_user_id,
                cleaned_tag,
                self._optional_text_or_none(site_username),
                self._optional_text_or_none(site_email),
                self._optional_text_or_none(site_url),
                encrypted_password,
                encryption_nonce,
                encryption_key_version,
            ),
        )
        self.conn.commit()

        if entry_id is None:
            raise RuntimeError("Failed to fetch vault entry id after insert")

        return str(entry_id)

    def list_vault_entries_for_user(self, owner_user_id: str) -> list[VaultEntryRow]:
        """
        Returns all vault entries for a user.

        Decryption is handled outside the repository.
        """
        rows = self._fetchall(q.LIST_VAULT_ENTRIES_FOR_OWNER, (owner_user_id,))
        return [self._row_to_vault_entry(row) for row in rows]

    def get_vault_entry_by_id_for_user(
        self,
        *,
        owner_user_id: str,
        entry_id: str,
    ) -> VaultEntryRow | None:
        row = self._fetchone(
            q.FETCH_VAULT_ENTRY_BY_ID_FOR_OWNER,
            (owner_user_id, entry_id),
        )
        if row is None:
            return None
        return self._row_to_vault_entry(row)

    def get_vault_entries_by_tag_for_user(
        self,
        *,
        owner_user_id: str,
        tag: str,
    ) -> list[VaultEntryRow]:
        cleaned_tag = self._clean_required_tag(tag)
        rows = self._fetchall(
            q.FETCH_VAULT_ENTRY_BY_TAG_FOR_OWNER,
            (owner_user_id, cleaned_tag),
        )
        return [self._row_to_vault_entry(row) for row in rows]

    def delete_vault_entry_by_id_for_user(
        self,
        *,
        owner_user_id: str,
        entry_id: str,
    ) -> int:
        return self._execute(
            q.DELETE_VAULT_ENTRY_BY_ID_FOR_OWNER,
            (owner_user_id, entry_id),
        )
