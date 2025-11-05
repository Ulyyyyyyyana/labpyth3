import os
import tempfile
import pytest
from app.models import RecipeDB, Recipe, RecipeError, RecipeNotFoundError


@pytest.fixture
def temp_db():
    """Создает временную БД для тестов"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = RecipeDB(db_path=path)
    yield db
    db.close()
    os.remove(path)


def test_add_and_get_recipe(temp_db):
    recipe = Recipe(
        id=None,
        title="Тестовый рецепт",
        ingredients="Мука, Яйца",
        steps="Смешать и испечь",
        tags="десерт",
        created_at=Recipe.now_iso(),
    )
    rid = temp_db.add(recipe)
    fetched = temp_db.get(rid)
    assert fetched.title == "Тестовый рецепт"
    assert "Мука" in fetched.ingredients


def test_add_recipe_without_title_raises(temp_db):
    recipe = Recipe(id=None, title="", ingredients="a", steps="b", tags="", created_at=Recipe.now_iso())
    with pytest.raises(RecipeError):
        temp_db.add(recipe)


def test_update_recipe(temp_db):
    recipe = Recipe(None, "Рецепт", "ингр", "шаги", "тест", Recipe.now_iso())
    rid = temp_db.add(recipe)
    temp_db.update(rid, "Новый", "новые", "новые шаги", "другое")
    updated = temp_db.get(rid)
    assert updated.title == "Новый"


def test_delete_recipe(temp_db):
    recipe = Recipe(None, "Удалить", "x", "y", "z", Recipe.now_iso())
    rid = temp_db.add(recipe)
    temp_db.delete(rid)
    with pytest.raises(RecipeNotFoundError):
        temp_db.get(rid)


def test_find_by_tag(temp_db):
    recipes = [
        Recipe(None, "Овсянка", "овес", "варить", "завтрак", Recipe.now_iso()),
        Recipe(None, "Борщ", "свекла", "варить", "обед", Recipe.now_iso()),
    ]
    temp_db.seed(recipes)
    found = temp_db.find_by_tag("завтрак")
    assert len(found) == 1
    assert found[0].title == "Овсянка"


def test_count_by_date(temp_db):
    recipes = [
        Recipe(None, "A", "1", "2", "x", "2025-11-04T10:00:00"),
        Recipe(None, "B", "1", "2", "x", "2025-11-04T12:00:00"),
        Recipe(None, "C", "1", "2", "x", "2025-11-03T09:00:00"),
    ]
    temp_db.seed(recipes)
    stats = temp_db.count_by_date()
    assert stats["2025-11-04"] == 2
    assert stats["2025-11-03"] == 1
