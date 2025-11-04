# app/models.py
import sqlite3
from dataclasses import dataclass
from typing import List, Optional
# app/models.py
"""
Модели данных и работа с SQLite.
Содержит:
- исключения приложения
- dataclass Recipe
- класс RecipeDB для работы с БД (создание таблицы, CRUD, агрегация)
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
import sqlite3
import datetime
import json
import os


# -----------------------
# Исключения
# -----------------------
class RecipeError(Exception):
    """Базовое исключение приложения."""
    pass


class RecipeNotFoundError(RecipeError):
    """Выбрасывается, если рецепт с указанным id не найден."""
    pass


# -----------------------
# Dataclass Recipe
# -----------------------
@dataclass
class Recipe:
    id: Optional[int]
    title: str
    ingredients: str  # свободный текст или JSON-строка
    steps: str
    tags: str         # CSV строка: "dessert,vegetarian"
    created_at: str   # ISO 8601, например "2025-11-04T12:34:56"

    @staticmethod
    def now_iso() -> str:
        return datetime.datetime.utcnow().replace(microsecond=0).isoformat()

    @classmethod
    def from_row(cls, row: Tuple) -> "Recipe":
        # row: (id, title, ingredients, steps, tags, created_at)
        return cls(
            id=row[0],
            title=row[1],
            ingredients=row[2] or "",
            steps=row[3] or "",
            tags=row[4] or "",
            created_at=row[5] or ""
        )

    def to_tuple_for_insert(self) -> Tuple:
        return (self.title, self.ingredients, self.steps, self.tags, self.created_at)


# -----------------------
# Класс работы с БД
# -----------------------
class RecipeDB:
    """
    Управление SQLite базой.
    По умолчанию создаёт файл recipes.db в текущей папке.
    """

    def __init__(self, db_path: str = "recipes.db"):
        self.db_path = db_path
        # ensure directory exists when a path has directories
        base_dir = os.path.dirname(os.path.abspath(db_path))
        os.makedirs(base_dir, exist_ok=True)
        # разрешаем многопоточность для GUI (check_same_thread=False)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()

    def _ensure_table(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT,
            steps TEXT,
            tags TEXT,
            created_at TEXT
        )
        """)
        self.conn.commit()

    # Create
    def add(self, recipe: Recipe) -> int:
        if not recipe.title or not recipe.title.strip():
            raise RecipeError("Название рецепта не может быть пустым")
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO recipes(title, ingredients, steps, tags, created_at) VALUES (?, ?, ?, ?, ?)",
            recipe.to_tuple_for_insert()
        )
        self.conn.commit()
        return cur.lastrowid

    # Read all
    def list_all(self, limit: Optional[int] = None) -> List[Recipe]:
        cur = self.conn.cursor()
        q = "SELECT id, title, ingredients, steps, tags, created_at FROM recipes ORDER BY created_at DESC"
        if limit:
            q += f" LIMIT {int(limit)}"
        cur.execute(q)
        rows = cur.fetchall()
        return [Recipe.from_row(tuple(r)) for r in rows]

    # Read one
    def get(self, recipe_id: int) -> Recipe:
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, ingredients, steps, tags, created_at FROM recipes WHERE id = ?", (recipe_id,))
        row = cur.fetchone()
        if not row:
            raise RecipeNotFoundError(f"Рецепт с id={recipe_id} не найден")
        return Recipe.from_row(tuple(row))

    # Update
    def update(self, recipe_id: int, title: str, ingredients: str, steps: str, tags: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE recipes SET title = ?, ingredients = ?, steps = ?, tags = ? WHERE id = ?",
            (title, ingredients, steps, tags, recipe_id)
        )
        if cur.rowcount == 0:
            raise RecipeNotFoundError(f"Рецепт с id={recipe_id} не найден для обновления")
        self.conn.commit()

    # Delete
    def delete(self, recipe_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        if cur.rowcount == 0:
            raise RecipeNotFoundError(f"Рецепт с id={recipe_id} не найден для удаления")
        self.conn.commit()

    # Поиск по тегу (в простом виде — ищем в строке tags)
    def find_by_tag(self, tag: str) -> List[Recipe]:
        cur = self.conn.cursor()
        like = f"%{tag}%"
        cur.execute("SELECT id, title, ingredients, steps, tags, created_at FROM recipes WHERE tags LIKE ? ORDER BY created_at DESC", (like,))
        rows = cur.fetchall()
        return [Recipe.from_row(tuple(r)) for r in rows]

    # Количество добавлений по дате -> возвращает dict {date_str: count}
    def count_by_date(self) -> Dict[str, int]:
        cur = self.conn.cursor()
        # Берём только дату из ISO строки (до 'T') — SQLite SUBSTR or DATE functions are limited, но у нас ISO
        cur.execute("""
        SELECT substr(created_at,1,10) as day, COUNT(*) as cnt
        FROM recipes
        GROUP BY day
        ORDER BY day ASC
        """)
        rows = cur.fetchall()
        return {r["day"]: r["cnt"] for r in rows if r["day"]}

    # Удобный метод для заполнения тестовыми данными
    def seed(self, recipes: List[Recipe]) -> None:
        cur = self.conn.cursor()
        cur.executemany(
            "INSERT INTO recipes(title, ingredients, steps, tags, created_at) VALUES (?, ?, ?, ?, ?)",
            [r.to_tuple_for_insert() for r in recipes]
        )
        self.conn.commit()

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
