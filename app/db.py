from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite


DB_PATH = Path("data/tasks.db")


@dataclass(slots=True)
class Task:
    id: int
    title: str
    created_at: str
    completed_at: str | None


class TaskRepository:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path

    async def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_user_status "
                "ON tasks(user_id, completed_at)"
            )
            await db.commit()

    async def add(self, user_id: int, title: str) -> int:
        created_at = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO tasks(user_id, title, created_at) VALUES (?, ?, ?)",
                (user_id, title, created_at),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def _list(self, user_id: int, completed: bool) -> list[Task]:
        condition = "completed_at IS NOT NULL" if completed else "completed_at IS NULL"
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                f"SELECT id, title, created_at, completed_at "
                f"FROM tasks WHERE user_id = ? AND {condition} ORDER BY id DESC",
                (user_id,),
            )
            rows = await cursor.fetchall()
            return [
                Task(
                    id=int(r["id"]),
                    title=str(r["title"]),
                    created_at=str(r["created_at"]),
                    completed_at=r["completed_at"],
                )
                for r in rows
            ]

    async def list_active(self, user_id: int) -> list[Task]:
        return await self._list(user_id, completed=False)

    async def list_completed(self, user_id: int) -> list[Task]:
        return await self._list(user_id, completed=True)

    async def complete(self, user_id: int, task_id: int) -> bool:
        completed_at = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "UPDATE tasks SET completed_at = ? "
                "WHERE id = ? AND user_id = ? AND completed_at IS NULL",
                (completed_at, task_id, user_id),
            )
            await db.commit()
            return cursor.rowcount == 1

    async def delete(self, user_id: int, task_id: int, completed_only: bool = False) -> bool:
        condition = " AND completed_at IS NOT NULL" if completed_only else ""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"DELETE FROM tasks WHERE id = ? AND user_id = ?{condition}",
                (task_id, user_id),
            )
            await db.commit()
            return cursor.rowcount == 1
