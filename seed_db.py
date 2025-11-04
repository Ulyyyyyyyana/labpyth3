# seed_db.py
"""
Заполнит БД несколькими тестовыми рецептами.
Запуск:
python seed_db.py
"""

from app.models import Recipe, RecipeDB
import datetime

def make_recipe(title, tags, ingredients, steps, created_at=None):
    if created_at is None:
        created_at = Recipe.now_iso()
    return Recipe(id=None, title=title, ingredients=ingredients, steps=steps, tags=tags, created_at=created_at)

def main():
    db = RecipeDB("recipes.db")
    recipes = [
        make_recipe("Овсяная каша с ягодами", "breakfast,vegetarian", "Овсяные хлопья\nМолоко\nЯгоды\nСахар", "1. Вскипятить молоко\n2. Добавить хлопья\n3. Подавать с ягодами"),
        make_recipe("Салат Цезарь", "salad,meat", "Листья салата\nКрутоны\nКурица\nСоус Цезарь", "1. Обжарить курицу\n2. Смешать ингредиенты\n3. Заправить"),
        make_recipe("Суп-пюре из тыквы", "soup,vegetarian", "Тыква\nЛук\nБульон\nСливки", "1. Обжарить лук\n2. Добавить тыкву и бульон\n3. Варить до мягкости\n4. Взбить"),
        make_recipe("Шоколадные маффины", "dessert,vegetarian", "Мука\nКакао\nСахар\nЯйца\nМолоко", "1. Смешать сухие\n2. Добавить яйца и молоко\n3. Выпекать 20 минут"),
        make_recipe("Паста Карбонара", "dinner,meat", "Паста\nГуанчиале или бекон\nСливки\nПармезан\nЯйца", "1. Отварить пасту\n2. Обжарить бекон\n3. Смешать с соусом")
    ]
    db.seed(recipes)
    print("Заполнено", len(recipes), "рецептов в recipes.db")

if __name__ == "__main__":
    main()
