# app/controllers.py
"""
Контроллер, реализующий бизнес-логику:
- добавление / удаление / редактирование рецепта
- генерация случайного рецепта
- статистика активностид
"""

import random
import datetime
from typing import List, Dict, Optional

from .models import Recipe, RecipeDB, RecipeError, RecipeNotFoundError


class RecipeController:
    def __init__(self, db: RecipeDB, logger=None):
        self.db = db
        self.logger = logger

    def add_recipe(self, title: str, ingredients: str, steps: str, tags: str) -> int:
        title = (title or "").strip()
        if not title:
            raise RecipeError("Название не может быть пустым")
        created_at = Recipe.now_iso()
        recipe = Recipe(id=None, title=title, ingredients=ingredients or "", steps=steps or "", tags=tags or "", created_at=created_at)
        rid = self.db.add(recipe)
        if self.logger:
            self.logger.info(f"Добавлен рецепт id={rid} title='{title}'")
        return rid

    def edit_recipe(self, recipe_id: int, title: str, ingredients: str, steps: str, tags: str) -> None:
        try:
            self.db.update(recipe_id, title, ingredients, steps, tags)
            if self.logger:
                self.logger.info(f"Обновлён рецепт id={recipe_id}")
        except RecipeNotFoundError:
            if self.logger:
                self.logger.warning(f"Попытка редактировать несуществующий рецепт id={recipe_id}")
            raise

    def delete_recipe(self, recipe_id: int) -> None:
        try:
            self.db.delete(recipe_id)
            if self.logger:
                self.logger.info(f"Удалён рецепт id={recipe_id}")
        except RecipeNotFoundError:
            if self.logger:
                self.logger.warning(f"Попытка удалить несуществующий рецепт id={recipe_id}")
            raise

    def list_recipes(self, limit: Optional[int] = None) -> List[Recipe]:
        return self.db.list_all(limit=limit)

    def get_recipe(self, recipe_id: int) -> Recipe:
        return self.db.get(recipe_id)

    def random_recipe(self, tag_filter: Optional[str] = None) -> Recipe:
        if tag_filter:
            candidates = self.db.find_by_tag(tag_filter)
        else:
            candidates = self.db.list_all()
        if not candidates:
            raise RecipeError("Нет подходящих рецептов для генерации")
        choice = random.choice(candidates)
        if self.logger:
            self.logger.info(f"Сгенерирован случайный рецепт id={choice.id} title='{choice.title}'")
        return choice

    def activity_stats(self) -> Dict[str, int]:
        # возвращает {date_str: count}
        return self.db.count_by_date()
