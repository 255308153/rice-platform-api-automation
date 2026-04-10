from __future__ import annotations

from typing import Any

import pymysql


class DBClient:
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = None

    def is_enabled(self) -> bool:
        return bool(self.host and self.user and self.database)

    def connect(self) -> None:
        if not self.is_enabled():
            raise RuntimeError("数据库连接参数未配置，无法建立连接。")
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def fetch_one(self, sql: str, params: tuple[Any, ...] | None = None) -> dict[str, Any] | None:
        if self.conn is None:
            self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()

    def __enter__(self) -> "DBClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
