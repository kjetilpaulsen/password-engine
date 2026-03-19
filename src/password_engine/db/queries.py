from __future__ import annotations

INSERT_APP_USER = """
INSERT INTO app_user (
    username,
    username_normalized,
    master_password_hash,
    master_password_hash_algorithm
)
VALUES (%s, %s, %s, %s)
RETURNING id;
"""

FETCH_APP_USER_BY_USERNAME_NORMALIZED = """
SELECT
    id,
    username,
    username_normalized,
    master_password_hash,
    master_password_hash_algorithm,
    master_key_salt,
    created_at,
    updated_at
FROM app_user
WHERE username_normalized = %s;
"""

INSERT_VAULT_ENTRY = """
INSERT INTO vault_entry (
    owner_user_id,
    tag,
    site_username,
    site_email,
    site_url,
    encrypted_password,
    encryption_nonce,
    encryption_key_version
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id;
"""

LIST_VAULT_ENTRIES_FOR_OWNER = """
SELECT
    id,
    tag,
    site_username,
    site_email,
    site_url,
    encrypted_password,
    encryption_nonce,
    encryption_key_version,
    created_at,
    updated_at
FROM vault_entry
WHERE owner_user_id = %s
ORDER BY tag, created_at, id;
"""

FETCH_VAULT_ENTRY_BY_ID_FOR_OWNER = """
SELECT
    id,
    tag,
    site_username,
    site_email,
    site_url,
    encrypted_password,
    encryption_nonce,
    encryption_key_version,
    created_at,
    updated_at
FROM vault_entry
WHERE owner_user_id = %s
  AND id = %s;
"""

FETCH_VAULT_ENTRY_BY_TAG_FOR_OWNER = """
SELECT
    id,
    tag,
    site_username,
    site_email,
    site_url,
    encrypted_password,
    encryption_nonce,
    encryption_key_version,
    created_at,
    updated_at
FROM vault_entry
WHERE owner_user_id = %s
  AND tag = %s
ORDER BY created_at, id;
"""

DELETE_VAULT_ENTRY_BY_ID_FOR_OWNER = """
DELETE FROM vault_entry
WHERE owner_user_id = %s
  AND id = %s;
"""
