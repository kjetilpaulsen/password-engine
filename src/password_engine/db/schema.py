from __future__ import annotations

import psycopg

DDL= """
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS app_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    username TEXT NOT NULL,
    username_normalized TEXT NOT NULL UNIQUE,

    master_password_hash TEXT NOT NULL,
    master_password_hash_algorithm TEXT NOT NULL DEFAULT 'argon2id',
    master_key_salt BYTEA NOT NULL DEFAULT gen_random_bytes(16),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT app_user_username_not_blank
        CHECK (length(trim(username)) > 0),

    CONSTRAINT app_user_username_normalized_not_blank
        CHECK (length(trim(username_normalized)) > 0)
);

CREATE TABLE IF NOT EXISTS vault_entry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    owner_user_id UUID NOT NULL
        REFERENCES app_user(id)
        ON DELETE CASCADE,

    tag TEXT NOT NULL,
    site_username TEXT,
    site_email TEXT,
    site_url TEXT,

    encrypted_password BYTEA NOT NULL,
    encryption_nonce BYTEA NOT NULL,
    encryption_key_version INTEGER NOT NULL DEFAULT 1,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT vault_entry_tag_not_blank
        CHECK (length(trim(tag)) > 0)
);

CREATE INDEX IF NOT EXISTS idx_vault_entry_owner_user_id
    ON vault_entry(owner_user_id);

CREATE INDEX IF NOT EXISTS idx_vault_entry_owner_user_tag
    ON vault_entry(owner_user_id, tag);

CREATE INDEX IF NOT EXISTS idx_vault_entry_owner_user_site_url
    ON vault_entry(owner_user_id, site_url);
"""

def create_schema(conn: psycopg.Connection) -> None:
    """
    Creates database tables and indexes if they do not already exist.

    Params:
    - conn: open psycopg connection to the target database
    """
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()


