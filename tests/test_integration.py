import pytest
from app.models import RecipeDB, Recipe
from app.controllers import RecipeController


@pytest.fixture
def setup_env(tmp_path):
    db_path = tmp_path / "integration.db"
    db = RecipeDB(str(db_path))
    ctrl = RecipeController(db)
    return db, ctrl


def test_add_edit_delete_flow(setup_env):
    db, ctrl = setup_env
    rid = ctrl.add_recipe("Паста", "макароны", "варить", "ужин")
    assert len(db.list_all()) == 1

    ctrl.edit_recipe(rid, "Паста болоньезе", "макароны+мясо", "варить", "ужин")
    updated = ctrl.get_recipe(rid)
    assert "болоньезе" in updated.title

    ctrl.delete_recipe(rid)
    assert db.list_all() == []
