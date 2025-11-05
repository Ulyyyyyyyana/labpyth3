"""
Улучшенный интерфейс MainWindow
Более чистая структура с вкладками и понятным расположением элементов
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QTextEdit,
    QLineEdit, QLabel, QMessageBox, QSplitter, QDialog, 
    QFormLayout, QTextBrowser, QStatusBar, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import logging
from datetime import datetime

from .models import Recipe
from .logger_config import QTextEditHandler


class ModernMainWindow(QMainWindow):
    def __init__(self, controller, logger=None):
        super().__init__()
        self.controller = controller
        self.logger = logger or logging.getLogger(__name__)
        self.setWindowTitle("🍳 Генератор случайных рецептов")
        self.resize(1200, 800)
        
        # Центральный стиль
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                font-weight: bold;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        self._create_menu()
        self._build_ui()
        self._connect_handlers()
        self.refresh_all()

    def _create_menu(self):
        """Создание меню приложения"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Вид
        view_menu = menubar.addMenu("Вид")
        refresh_action = QAction("Обновить", self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self.refresh_all)
        view_menu.addAction(refresh_action)

    def _build_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()
        
        # Создаем вкладки для лучшей организации
        self.tabs = QTabWidget()
        
        # Вкладка 1: Просмотр и управление рецептами
        self.tab_recipes = QWidget()
        self._build_recipes_tab()
        self.tabs.addTab(self.tab_recipes, "📖 Все рецепты")
        
        # Вкладка 2: Добавление рецепта
        self.tab_add = QWidget()
        self._build_add_tab()
        self.tabs.addTab(self.tab_add, "➕ Добавить рецепт")
        
        # Вкладка 3: Генератор и статистика
        self.tab_tools = QWidget()
        self._build_tools_tab()
        self.tabs.addTab(self.tab_tools, "🎲 Генератор")
        
        main_layout.addWidget(self.tabs)
        central.setLayout(main_layout)
        self.setCentralWidget(central)
        
        # Статус бар
        self.setStatusBar(QStatusBar())

    def _build_recipes_tab(self):
        layout = QVBoxLayout()
        
        # Группа таблицы
        table_group = QGroupBox("База рецептов")
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Теги", "Создан"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setColumnWidth(0, 50)   # ID
        self.table.setColumnWidth(1, 250)  # Название
        self.table.setColumnWidth(2, 150)  # Теги
        self.table.setColumnWidth(3, 120)  # Дата
        
        table_layout.addWidget(self.table)
        
        # Кнопки управления под таблицей
        btn_layout = QHBoxLayout()
        self.btn_view = QPushButton("👁 Просмотр")
        self.btn_edit = QPushButton("✏ Редактировать")
        self.btn_delete = QPushButton("🗑 Удалить")
        
        btn_layout.addWidget(self.btn_view)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        
        table_layout.addLayout(btn_layout)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # График активности
        chart_group = QGroupBox("Статистика добавления рецептов")
        chart_layout = QVBoxLayout()
        self.figure = Figure(figsize=(8, 3))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        chart_group.setLayout(chart_layout)
        layout.addWidget(chart_group)
        
        self.tab_recipes.setLayout(layout)

    def _build_add_tab(self):
        layout = QVBoxLayout()
        
        form_group = QGroupBox("Новый рецепт")
        form_layout = QFormLayout()
        
        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("Введите название рецепта...")
        
        self.input_tags = QLineEdit()
        self.input_tags.setPlaceholderText("завтрак, десерт, вегетарианский...")
        
        self.input_ingredients = QTextEdit()
        self.input_ingredients.setPlaceholderText("Перечислите ингредиенты...")
        self.input_ingredients.setMaximumHeight(120)
        
        self.input_steps = QTextEdit()
        self.input_steps.setPlaceholderText("Опишите шаги приготовления...")
        self.input_steps.setMaximumHeight(150)
        
        form_layout.addRow("🎯 Название:", self.input_title)
        form_layout.addRow("🏷 Теги:", self.input_tags)
        form_layout.addRow("🥕 Ингредиенты:", self.input_ingredients)
        form_layout.addRow("👨‍🍳 Шаги приготовления:", self.input_steps)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("💾 Сохранить рецепт")
        self.btn_clear = QPushButton("🗑 Очистить форму")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        
        form_layout.addRow("", btn_layout)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Лог действий
        log_group = QGroupBox("Журнал действий")
        log_layout = QVBoxLayout()
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setMaximumHeight(200)
        log_layout.addWidget(self.log_widget)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        self.tab_add.setLayout(layout)

    def _build_tools_tab(self):
        layout = QVBoxLayout()
        
        # Генератор случайных рецептов
        generator_group = QGroupBox("Генератор случайных рецептов")
        generator_layout = QVBoxLayout()
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр по тегам:"))
        self.input_filter_tags = QLineEdit()
        self.input_filter_tags.setPlaceholderText("оставьте пустым для всех рецептов")
        filter_layout.addWidget(self.input_filter_tags)
        
        self.btn_random = QPushButton("🎲 Сгенерировать случайный рецепт!")
        self.btn_random.setStyleSheet("QPushButton { font-size: 14px; padding: 10px; }")
        
        generator_layout.addLayout(filter_layout)
        generator_layout.addWidget(self.btn_random)
        generator_group.setLayout(generator_layout)
        layout.addWidget(generator_group)
        
        # Область для отображения сгенерированного рецепта
        self.random_recipe_display = QTextBrowser()
        self.random_recipe_display.setMaximumHeight(300)
        layout.addWidget(QLabel("Сгенерированный рецепт:"))
        layout.addWidget(self.random_recipe_display)
        
        layout.addStretch()
        self.tab_tools.setLayout(layout)

    def _connect_handlers(self):
        # Кнопки управления рецептами
        self.btn_view.clicked.connect(self.on_view)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        
        # Кнопки добавления
        self.btn_add.clicked.connect(self.on_add_recipe)
        self.btn_clear.clicked.connect(self.on_clear_form)
        
        # Генератор
        self.btn_random.clicked.connect(self.on_random)
        
        # Двойной клик по таблице
        self.table.cellDoubleClicked.connect(self.on_table_double_click)
        
        # Настройка логгера
        qhandler = QTextEditHandler(self.log_widget.append)
        self.logger.handlers.clear()
        self.logger.addHandler(qhandler)
        self.logger.setLevel(logging.INFO)

    def refresh_all(self):
        self.refresh_table()
        self.refresh_plot()
        self.statusBar().showMessage(f"Данные обновлены {datetime.now().strftime('%H:%M:%S')}")

    def refresh_table(self):
        try:
            recipes = self.controller.list_recipes()
            self.table.setRowCount(len(recipes))
            
            for i, recipe in enumerate(recipes):
                self.table.setItem(i, 0, QTableWidgetItem(str(recipe.id)))
                self.table.setItem(i, 1, QTableWidgetItem(recipe.title))
                self.table.setItem(i, 2, QTableWidgetItem(recipe.tags))
                
                # Форматируем дату для лучшего отображения
                try:
                    date_obj = datetime.fromisoformat(recipe.created_at.replace('Z', '+00:00'))
                    display_date = date_obj.strftime("%d.%m.%Y %H:%M")
                except:
                    display_date = recipe.created_at
                
                self.table.setItem(i, 3, QTableWidgetItem(display_date))
            
            self.logger.info(f"Загружено {len(recipes)} рецептов")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки рецептов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить рецепты:\n{e}")

    def refresh_plot(self):
        try:
            stats = self.controller.activity_stats()
            self.figure.clear()
            ax = self.figure.subplots()
            
            if not stats:
                ax.text(0.5, 0.5, "Нет данных для построения графика", 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title("Статистика добавления рецептов")
            else:
                # Сортируем по дате
                dates = sorted(stats.keys())
                counts = [stats[date] for date in dates]
                
                # Создаем красивый график
                bars = ax.bar(dates, counts, color='skyblue', edgecolor='navy', alpha=0.7)
                ax.set_ylabel("Количество рецептов")
                ax.set_title("Статистика добавления рецептов по датам")
                
                # Добавляем значения на столбцы
                for bar, count in zip(bars, counts):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                           str(count), ha='center', va='bottom', fontsize=9)
                
                # Наклоняем подписи дат для лучшей читаемости
                ax.set_xticks(range(len(dates)))
                ax.set_xticklabels(dates, rotation=45, ha='right')
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Ошибка построения графика: {e}")

    def on_add_recipe(self):
        """Добавление нового рецепта"""
        title = self.input_title.text().strip()
        tags = self.input_tags.text().strip()
        ingredients = self.input_ingredients.toPlainText().strip()
        steps = self.input_steps.toPlainText().strip()
        
        if not title:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, введите название рецепта")
            self.input_title.setFocus()
            return
        
        try:
            recipe_id = self.controller.add_recipe(title, ingredients, steps, tags)
            self.logger.info(f"Добавлен новый рецепт: '{title}' (ID: {recipe_id})")
            
            # Очищаем форму и переходим к вкладке с рецептами
            self.on_clear_form()
            self.tabs.setCurrentIndex(0)  # Переход к вкладке рецептов
            self.refresh_all()
            
            QMessageBox.information(self, "Успех", f"Рецепт '{title}' успешно добавлен!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить рецепт:\n{e}")
            self.logger.error(f"Ошибка добавления рецепта: {e}")

    def on_clear_form(self):
        """Очистка формы ввода"""
        self.input_title.clear()
        self.input_tags.clear()
        self.input_ingredients.clear()
        self.input_steps.clear()
        self.input_title.setFocus()

    def on_view(self):
        """Просмотр выбранного рецепта"""
        recipe = self._get_selected_recipe()
        if recipe:
            self._show_recipe_dialog(recipe, editable=False)

    def on_edit(self):
        """Редактирование выбранного рецепта"""
        recipe = self._get_selected_recipe()
        if recipe:
            self._show_recipe_dialog(recipe, editable=True)

    def on_delete(self):
        """Удаление выбранного рецепта"""
        recipe = self._get_selected_recipe()
        if not recipe:
            return
            
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить рецепт:\n\"{recipe.title}\"?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.controller.delete_recipe(recipe.id)
                self.logger.info(f"Удален рецепт: '{recipe.title}' (ID: {recipe.id})")
                self.refresh_all()
                QMessageBox.information(self, "Успех", "Рецепт успешно удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить рецепт:\n{e}")
                self.logger.error(f"Ошибка удаления рецепта: {e}")

    def on_random(self):
        """Генерация случайного рецепта"""
        tag_filter = self.input_filter_tags.text().strip() or None
        
        try:
            recipe = self.controller.random_recipe(tag_filter)
            self._display_random_recipe(recipe)
            self.logger.info(f"Сгенерирован случайный рецепт: '{recipe.title}'")
        except Exception as e:
            QMessageBox.information(self, "Информация", 
                                  f"Не удалось сгенерировать рецепт:\n{e}")
            self.random_recipe_display.clear()
            self.random_recipe_display.append("❌ Рецепты не найдены по заданным критериям")

    def on_table_double_click(self, row, column):
        """Обработка двойного клика по таблице - быстрый просмотр"""
        recipe = self._get_selected_recipe()
        if recipe:
            self._show_recipe_dialog(recipe, editable=False)

    def _get_selected_recipe(self):
        """Получение выбранного рецепта из таблицы"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Выбор", "Пожалуйста, выберите рецепт из таблицы")
            return None
        
        try:
            row = selected_items[0].row()
            recipe_id = int(self.table.item(row, 0).text())
            return self.controller.get_recipe(recipe_id)
        except Exception as e:
            self.logger.error(f"Ошибка получения рецепта: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить рецепт:\n{e}")
            return None

    def _show_recipe_dialog(self, recipe: Recipe, editable: bool = False):
        """Показ диалога с рецептом"""
        dlg = RecipeDialog(self, recipe, editable)
        if dlg.exec() == QDialog.Accepted and editable:
            # Если редактировали и сохранили изменения
            try:
                data = dlg.get_data()
                self.controller.edit_recipe(recipe.id, **data)
                self.logger.info(f"Обновлен рецепт: '{recipe.title}' (ID: {recipe.id})")
                self.refresh_all()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить рецепт:\n{e}")
                self.logger.error(f"Ошибка обновления рецепта: {e}")

    def _display_random_recipe(self, recipe: Recipe):
        """Отображение сгенерированного рецепта в красивом формате"""
        display_text = f"""
        <h2 style='color: #2E8B57;'>{recipe.title}</h2>
        <p><strong>🏷 Теги:</strong> {recipe.tags or 'нет'}</p>
        <p><strong>📅 Добавлен:</strong> {recipe.created_at}</p>
        
        <h3 style='color: #4169E1;'>🥕 Ингредиенты:</h3>
        <pre style='background-color: #f8f8f8; padding: 10px; border-radius: 5px;'>{recipe.ingredients or 'Не указаны'}</pre>
        
        <h3 style='color: #4169E1;'>👨‍🍳 Способ приготовления:</h3>
        <pre style='background-color: #f8f8f8; padding: 10px; border-radius: 5px;'>{recipe.steps or 'Не указан'}</pre>
        """
        
        self.random_recipe_display.setHtml(display_text)


class RecipeDialog(QDialog):
    """Диалог для просмотра/редактирования рецепта"""
    
    def __init__(self, parent=None, recipe: Recipe = None, editable: bool = False):
        super().__init__(parent)
        self.recipe = recipe
        self.editable = editable
        
        mode = "Редактирование" if editable else "Просмотр"
        self.setWindowTitle(f"{mode} рецепта: {recipe.title}")
        self.resize(600, 500)
        
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.input_title = QLineEdit(self.recipe.title)
        self.input_title.setReadOnly(not self.editable)
        
        self.input_tags = QLineEdit(self.recipe.tags)
        self.input_tags.setReadOnly(not self.editable)
        
        self.input_ingredients = QTextEdit()
        self.input_ingredients.setPlainText(self.recipe.ingredients)
        self.input_ingredients.setReadOnly(not self.editable)
        
        self.input_steps = QTextEdit()
        self.input_steps.setPlainText(self.recipe.steps)
        self.input_steps.setReadOnly(not self.editable)
        
        form.addRow("Название:", self.input_title)
        form.addRow("Теги:", self.input_tags)
        form.addRow("Ингредиенты:", self.input_ingredients)
        form.addRow("Шаги:", self.input_steps)
        
        layout.addLayout(form)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        if self.editable:
            self.btn_save = QPushButton("💾 Сохранить")
            self.btn_save.clicked.connect(self.accept)
            btn_layout.addWidget(self.btn_save)
        
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_close)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_data(self):
        return {
            'title': self.input_title.text(),
            'tags': self.input_tags.text(),
            'ingredients': self.input_ingredients.toPlainText(),
            'steps': self.input_steps.toPlainText()
        }