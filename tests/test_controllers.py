import pytest
from app.controllers import RecipeController
from app.models import RecipeDB, Recipe, RecipeError, RecipeNotFoundError


@pytest.fixture
def controller(tmp_path):
    db_path = tmp_path / "test.db"
    db = RecipeDB(str(db_path))
    ctrl = RecipeController(db=db)
    return ctrl


def test_add_recipe_success(controller):
    rid = controller.add_recipe("Тест", "ингр", "шаги", "тест")
    assert isinstance(rid, int)
    r = controller.get_recipe(rid)
    assert r.title == "Тест"


def test_add_recipe_empty_title(controller):
    with pytest.raises(RecipeError):
        controller.add_recipe("", "ингр", "шаги", "тест")


def test_edit_recipe(controller):
    rid = controller.add_recipe("A", "B", "C", "T")
    controller.edit_recipe(rid, "Новый", "B2", "C2", "T2")
    updated = controller.get_recipe(rid)
    assert updated.title == "Новый"


def test_edit_nonexistent_recipe(controller):
    with pytest.raises(RecipeNotFoundError):
        controller.edit_recipe(9999, "X", "Y", "Z", "K")


def test_delete_recipe(controller):
    rid = controller.add_recipe("Del", "a", "b", "c")
    controller.delete_recipe(rid)
    with pytest.raises(RecipeNotFoundError):
        controller.get_recipe(rid)


def test_random_recipe(controller):
    controller.add_recipe("Суп", "вода", "варить", "обед")
    r = controller.random_recipe()
    assert isinstance(r, Recipe)


def test_random_recipe_with_tag(controller):
    controller.add_recipe("Пирог", "мука", "печь", "десерт")
    r = controller.random_recipe("десерт")
    assert "Пирог" in r.title


def test_random_recipe_no_results(controller):
    with pytest.raises(RecipeError):
        controller.random_recipe("несуществующий")
# tests/test_controllers_extra.py
import pytest
from app.controllers import RecipeController
from app.models import RecipeDB, Recipe, RecipeNotFoundError

class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg): self.messages.append(msg)
    def warning(self, msg): self.messages.append(msg)

@pytest.fixture
def controller_with_logger(tmp_path):
    db = RecipeDB(str(tmp_path / "db.db"))
    logger = DummyLogger()
    return RecipeController(db, logger)

def test_edit_nonexistent_logs_warning(controller_with_logger):
    with pytest.raises(RecipeNotFoundError):
        controller_with_logger.edit_recipe(999, "x", "y", "z", "t")
    assert any("несуществующий" in m for m in controller_with_logger.logger.messages)

def test_delete_nonexistent_logs_warning(controller_with_logger):
    with pytest.raises(RecipeNotFoundError):
        controller_with_logger.delete_recipe(123)
    assert any("несуществующий" in m for m in controller_with_logger.logger.messages)

def test_random_recipe_logs(controller_with_logger):
    controller_with_logger.add_recipe("Тест", "ингр", "шаги", "метка")
    _ = controller_with_logger.random_recipe()
    assert any("Сгенерирован" in m for m in controller_with_logger.logger.messages)
