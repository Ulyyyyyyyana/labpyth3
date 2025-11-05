
# app/main.py
"""
Точка входа в приложение.
Запускает QApplication, создаёт DB, контроллер и окно.
"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from .models import RecipeDB
from .controllers import RecipeController
from .gui import ModernMainWindow

from .logger_config import setup_root_logger, QTextEditHandler

def run():
    # Создаём приложение Qt
    app = QApplication(sys.argv)

    # Создаём БД (файл recipes.db рядом с проектом)
    db = RecipeDB(db_path="recipes.db")
    # Логгер
    logger = logging.getLogger("recipe_app")
    setup_root_logger(level=logging.INFO)
    # Контроллер
    controller = RecipeController(db=db, logger=logger)
    # Окно
    mw = ModernMainWindow(controller=controller, logger=logger)


    # Перевыставим handler для записи в виджет (MainWindow создает QTextEdit handler внутри)
    # Показываем окно
    mw.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
