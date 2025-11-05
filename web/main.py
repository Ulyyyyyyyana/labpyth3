from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.models import RecipeDB
from app.controllers import RecipeController
import json
import os

app = FastAPI()
templates = Jinja2Templates(directory="web/templates")

# Создаём глобальные объекты (БД и контроллер)
db_path = os.path.join(os.path.dirname(__file__), "..", "recipes.db")
db = RecipeDB(db_path)
controller = RecipeController(db=db)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница с таблицей и графиком"""
    recipes = controller.list_recipes()
    stats = controller.activity_stats() or {}
    return templates.TemplateResponse("index.html", {
        "request": request,
        "recipes": recipes,
        "random_recipe": None,
        "stats_json": json.dumps(stats)
    })

@app.post("/add", response_class=HTMLResponse)
async def add_recipe(
    request: Request,
    title: str = Form(...),
    ingredients: str = Form(""),
    steps: str = Form(""),
    tags: str = Form("")
):
    """Добавление нового рецепта"""
    try:
        controller.add_recipe(title, ingredients, steps, tags)
    except Exception as e:
        print(f"Ошибка добавления рецепта: {e}")

    recipes = controller.list_recipes()
    stats = controller.activity_stats() or {}
    return templates.TemplateResponse("index.html", {
        "request": request,
        "recipes": recipes,
        "random_recipe": None,
        "stats_json": json.dumps(stats)
    })

@app.get("/random", response_class=HTMLResponse)
async def random_recipe(request: Request, tag: str = None):
    """Генерация случайного рецепта"""
    recipe = None
    try:
        recipe = controller.random_recipe(tag)
    except Exception as e:
        print(f"Ошибка генерации: {e}")

    recipes = controller.list_recipes()
    stats = controller.activity_stats() or {}
    return templates.TemplateResponse("index.html", {
        "request": request,
        "recipes": recipes,
        "random_recipe": recipe,
        "stats_json": json.dumps(stats)
    })
