#!/usr/bin/env python3
"""
Главный файл запуска приложения Recipe Randomizer
Поместите этот файл в корневую папку проекта и запускайте: python launch.py
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем текущую директорию в Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QIcon
except ImportError as e:
    print("❌ Ошибка: Не установлены необходимые библиотеки")
    print("📦 Установите зависимости: pip install PySide6 matplotlib pandas")
    print(f"🔧 Детали ошибки: {e}")
    input("Нажмите Enter для выхода...")
    sys.exit(1)

def setup_database():
    """Настройка и инициализация базы данных"""
    try:
        from app.models import RecipeDB
        
        db_path = "recipes.db"
        db = RecipeDB(db_path)
        
        # Проверяем, есть ли рецепты в базе
        recipes = db.list_all()
        if not recipes:
            print("📝 База данных пустая. Добавляем тестовые рецепты...")
            try:
                # Пробуем заполнить тестовыми данными
                from seed_db import main as seed_main
                seed_main()
                print("✅ Тестовые рецепты добавлены")
            except Exception as e:
                print(f"⚠️ Не удалось добавить тестовые рецепты: {e}")
        else:
            print(f"✅ Загружено {len(recipes)} рецептов из базы данных")
        
        return db
        
    except Exception as e:
        print(f"❌ Ошибка настройки базы данных: {e}")
        raise

def setup_logging():
    """Настройка системы логирования"""
    try:
        # Создаем папку для логов если её нет
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Настраиваем логгер
        logger = logging.getLogger("recipe_app")
        logger.setLevel(logging.INFO)
        
        # Форматтер для логов
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Файловый handler
        file_handler = logging.FileHandler(log_dir / "app.log", encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Консольный handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Очищаем существующие handlers и добавляем новые
        logger.handlers.clear()
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    except Exception as e:
        print(f"❌ Ошибка настройки логирования: {e}")
        # Возвращаем базовый логгер
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger("recipe_app")

def main():
    """Главная функция запуска приложения"""
    print("=" * 60)
    print("🍳 Recipe Randomizer - Генератор случайных рецептов")
    print("=" * 60)
    
    try:
        # Создаем Qt приложение
        app = QApplication(sys.argv)
        app.setApplicationName("Recipe Randomizer")
        app.setApplicationVersion("1.0.0")
        
        print("🔄 Инициализация приложения...")
        
        # Настраиваем компоненты
        db = setup_database()
        logger = setup_logging()
        
        # Импортируем и создаем контроллер
        from app.controllers import RecipeController
        controller = RecipeController(db=db, logger=logger)
        
        # Пробуем импортировать современный GUI, если не получится - старый
        try:
            from app.modern_gui import ModernMainWindow
            print("🎨 Загрузка современного интерфейса...")
            window = ModernMainWindow(controller=controller, logger=logger)
        except ImportError as e:
            print("🎨 Современный интерфейс не найден, загружаем базовый...")
            from app.gui import MainWindow
            window = MainWindow(controller=controller, logger=logger)
        
        print("✅ Приложение успешно запущено!")
        print("\n💡 Подсказки по использованию:")
        print("   - Используйте вкладки для навигации")
        print("   - Двойной клик по рецепту для быстрого просмотра") 
        print("   - Фильтруйте рецепты по тегам в генераторе")
        print("   - Все действия логируются в файл logs/app.log")
        print("-" * 60)
        
        # Показываем окно и запускаем приложение
        window.show()
        
        # Запускаем главный цикл приложения
        return app.exec()
        
    except Exception as e:
        print(f"❌ Критическая ошибка при запуске: {e}")
        print("\n🔧 Возможные решения:")
        print("   1. Убедитесь, что установлены все зависимости: pip install PySide6 matplotlib pandas")
        print("   2. Проверьте структуру папок проекта")
        print("   3. Убедитесь, что файл launch.py находится в корневой папке проекта")
        input("\nНажмите Enter для выхода...")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)