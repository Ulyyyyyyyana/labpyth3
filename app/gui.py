from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QTextEdit,
    QLineEdit, QLabel, QMessageBox, QFormLayout, QTextBrowser,
    QStatusBar, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import logging

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .models import Recipe
from .logger_config import QTextEditHandler


class ModernMainWindow(QMainWindow):
    def __init__(self, controller, logger=None):
        super().__init__()
        self.controller = controller
        self.logger = logger or logging.getLogger(__name__)
        self.setWindowTitle("🍳 Генератор рецептов")
        self.resize(950, 650)

        self.setStyleSheet("""
            QWidget {
                background-color: #f8f8fb;
                font-family: "Segoe UI", sans-serif;
                font-size: 13px;
            }
            QPushButton {
                background-color: #82b1ff;
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: 600;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #64b5f6;
            }
            QLineEdit, QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #cfd8dc;
                border-radius: 6px;
                padding: 4px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                padding: 8px 16px;
                border-radius: 6px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                font-weight: bold;
            }
        """)

        self._build_ui()
        self._connect_handlers()
        self.refresh_table()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        # 📋 Вкладка рецептов
        self.tab_recipes = QWidget()
        self._build_recipes_tab()
        self.tabs.addTab(self.tab_recipes, "📖 Рецепты")

        # ➕ Вкладка добавления
        self.tab_add = QWidget()
        self._build_add_tab()
        self.tabs.addTab(self.tab_add, "➕ Добавить")

        # 🎲 Генератор
        self.tab_tools = QWidget()
        self._build_tools_tab()
        self.tabs.addTab(self.tab_tools, "🎲 Генератор")

        layout.addWidget(self.tabs)
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.setStatusBar(QStatusBar())

    # -----------------------------
    # 📊 Таблица + график активности
    # -----------------------------
    def _build_recipes_tab(self):
        layout = QVBoxLayout()

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Теги", "Создан"])
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.setColumnWidth(1, 280)
        layout.addWidget(self.table)

        # График активности
        self.figure = Figure(figsize=(5, 2))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(QLabel("Активность добавления рецептов"))
        layout.addWidget(self.canvas)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_view = QPushButton("👁 Просмотр")
        self.btn_edit = QPushButton("✏ Редактировать")
        self.btn_delete = QPushButton("🗑 Удалить")
        btn_layout.addWidget(self.btn_view)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

        self.tab_recipes.setLayout(layout)

    # -----------------------------
    # ➕ Добавление рецепта
    # -----------------------------
    def _build_add_tab(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.input_title = QLineEdit()
        self.input_tags = QLineEdit()
        self.input_ingredients = QTextEdit()
        self.input_steps = QTextEdit()
        self.btn_add = QPushButton("💾 Добавить рецепт")
        self.btn_clear = QPushButton("🧹 Очистить")

        form.addRow("Название:", self.input_title)
        form.addRow("Теги:", self.input_tags)
        form.addRow("Ингредиенты:", self.input_ingredients)
        form.addRow("Шаги:", self.input_steps)

        layout.addLayout(form)
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_clear)

        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout.addWidget(QLabel("Журнал:"))
        layout.addWidget(self.log_widget)

        self.tab_add.setLayout(layout)

    # -----------------------------
    # 🎲 Генератор рецептов
    # -----------------------------
    def _build_tools_tab(self):
        layout = QVBoxLayout()

        self.input_filter_tags = QLineEdit()
        self.input_filter_tags.setPlaceholderText("Введите тег (например, 'десерт')")
        self.btn_random = QPushButton("🎲 Случайный рецепт")
        self.random_recipe_display = QTextBrowser()

        layout.addWidget(QLabel("Фильтр по тегу:"))
        layout.addWidget(self.input_filter_tags)
        layout.addWidget(self.btn_random)
        layout.addWidget(QLabel("Результат:"))
        layout.addWidget(self.random_recipe_display)

        self.tab_tools.setLayout(layout)

    # -----------------------------
    # Обработчики
    # -----------------------------
    def _connect_handlers(self):
        self.btn_add.clicked.connect(self.on_add)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_random.clicked.connect(self.on_random)
        self.btn_view.clicked.connect(self.on_view)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)

        qhandler = QTextEditHandler(self.log_widget.append)
        self.logger.handlers.clear()
        self.logger.addHandler(qhandler)
        self.logger.setLevel(logging.INFO)

    # -----------------------------
    # Действия
    # -----------------------------
    def refresh_table(self):
        try:
            recipes = self.controller.list_recipes()
            self.table.setRowCount(len(recipes))
            for i, recipe in enumerate(recipes):
                self.table.setItem(i, 0, QTableWidgetItem(str(recipe.id)))
                self.table.setItem(i, 1, QTableWidgetItem(recipe.title))
                self.table.setItem(i, 2, QTableWidgetItem(recipe.tags))
                self.table.setItem(i, 3, QTableWidgetItem(recipe.created_at))
            self._update_chart()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить рецепты:\n{e}")

    def _update_chart(self):
        import datetime as dt
        import matplotlib.dates as mdates

        try:
            data = self.controller.activity_stats()

            self.figure.clear()
            ax = self.figure.add_subplot(111)

            if data:
                # Преобразуем ISO-строки в объекты даты
                dates = [dt.datetime.fromisoformat(d).date() for d in sorted(data.keys())]
                counts = [data[str(d)] for d in sorted(data.keys())]

                ax.bar(dates, counts, color="#90caf9", edgecolor="#1e88e5", linewidth=1.2)
                ax.set_title("Активность добавления рецептов", fontsize=11, fontweight="bold")
                ax.set_xlabel("Дата", fontsize=9)
                ax.set_ylabel("Количество рецептов", fontsize=9)
                ax.grid(axis="y", linestyle="--", alpha=0.5)

                # Формат дат
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
                self.figure.autofmt_xdate(rotation=45)
            else:
                ax.text(0.5, 0.5, "Нет данных для отображения",
                        ha="center", va="center", fontsize=11, color="gray")

            self.figure.tight_layout()
            self.canvas.draw()

        except Exception as e:
            self.logger.error(f"Ошибка при построении графика: {e}")

    def on_add(self):
        title = self.input_title.text().strip()
        tags = self.input_tags.text().strip()
        ing = self.input_ingredients.toPlainText().strip()
        steps = self.input_steps.toPlainText().strip()

        if not title:
            QMessageBox.warning(self, "Ошибка", "Введите название рецепта")
            return

        try:
            self.controller.add_recipe(title, ing, steps, tags)
            self.logger.info(f"Добавлен рецепт: {title}")
            self.refresh_table()
            QMessageBox.information(self, "Успех", "Рецепт успешно добавлен!")
            self.on_clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def on_clear(self):
        self.input_title.clear()
        self.input_tags.clear()
        self.input_ingredients.clear()
        self.input_steps.clear()

    def on_view(self):
        recipe = self._get_selected_recipe()
        if recipe:
            self._show_recipe_dialog(recipe, editable=False)

    def on_edit(self):
        recipe = self._get_selected_recipe()
        if recipe:
            self._show_recipe_dialog(recipe, editable=True)

    def on_delete(self):
        recipe = self._get_selected_recipe()
        if not recipe:
            return
        reply = QMessageBox.question(self, "Удаление", f"Удалить рецепт '{recipe.title}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.delete_recipe(recipe.id)
            self.refresh_table()

    def on_random(self):
        tag = self.input_filter_tags.text().strip() or None
        try:
            r = self.controller.random_recipe(tag)
            self.random_recipe_display.setHtml(
                f"<h2>{r.title}</h2><p><b>Теги:</b> {r.tags}</p>"
                f"<pre>{r.ingredients}</pre><pre>{r.steps}</pre>"
            )
        except Exception as e:
            QMessageBox.information(self, "Нет данных", str(e))

    def _get_selected_recipe(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Выбор", "Выберите рецепт")
            return None
        row = selected[0].row()
        rid = int(self.table.item(row, 0).text())
        return self.controller.get_recipe(rid)

    def _show_recipe_dialog(self, recipe, editable=False):
        dlg = RecipeDialog(self, recipe, editable)
        if dlg.exec() == QDialog.Accepted and editable:
            data = dlg.get_data()
            self.controller.edit_recipe(recipe.id, **data)
            self.refresh_table()


class RecipeDialog(QDialog):
    """Диалог просмотра/редактирования"""
    def __init__(self, parent, recipe, editable=False):
        super().__init__(parent)
        self.recipe = recipe
        self.editable = editable
        self.setWindowTitle(f"Рецепт: {recipe.title}")
        self.resize(500, 400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.input_title = QLineEdit(self.recipe.title)
        self.input_tags = QLineEdit(self.recipe.tags)
        self.input_ing = QTextEdit(self.recipe.ingredients)
        self.input_steps = QTextEdit(self.recipe.steps)

        for widget in [self.input_title, self.input_tags, self.input_ing, self.input_steps]:
            widget.setReadOnly(not self.editable)

        form.addRow("Название:", self.input_title)
        form.addRow("Теги:", self.input_tags)
        form.addRow("Ингредиенты:", self.input_ing)
        form.addRow("Шаги:", self.input_steps)

        btn_layout = QHBoxLayout()
        if self.editable:
            btn_save = QPushButton("💾 Сохранить")
            btn_save.clicked.connect(self.accept)
            btn_layout.addWidget(btn_save)
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(btn_close)

        layout.addLayout(form)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_data(self):
        return dict(
            title=self.input_title.text(),
            tags=self.input_tags.text(),
            ingredients=self.input_ing.toPlainText(),
            steps=self.input_steps.toPlainText()
        )
