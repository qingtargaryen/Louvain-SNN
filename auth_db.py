# -*- coding: utf-8 -*-
"""SQLite 用户表：用户名唯一，密码仅存哈希。"""
import os
import sqlite3
from contextlib import contextmanager

from werkzeug.security import check_password_hash, generate_password_hash


def _connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path):
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()


@contextmanager
def get_connection(db_path):
    conn = _connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def user_count(db_path):
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()
        return int(row["n"])


def get_user_by_username(db_path, username):
    if not username:
        return None
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ? COLLATE NOCASE",
            (username.strip(),),
        ).fetchone()
        return dict(row) if row else None


def create_user(db_path, username, password):
    """成功返回用户 id；用户名冲突返回 None。"""
    username = (username or "").strip()
    if len(username) < 3 or len(username) > 64:
        raise ValueError("用户名长度应为 3–64 个字符。")
    if len(password or "") < 6:
        raise ValueError("密码长度至少 6 位。")
    ph = generate_password_hash(password)
    with get_connection(db_path) as conn:
        try:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, ph),
            )
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None


def verify_password(db_path, username, password):
    u = get_user_by_username(db_path, username)
    if not u:
        return None
    if not check_password_hash(u["password_hash"], password):
        return None
    return {"id": u["id"], "username": u["username"]}


def ensure_default_admin(db_path, password):
    """库中无任何用户时创建默认管理员（仅用于首次部署）。"""
    if user_count(db_path) > 0:
        return
    if not password:
        return
    create_user(db_path, "admin", password)
