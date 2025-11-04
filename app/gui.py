# app/gui.py
"""
MainWindow: интерфейс приложения.
Содержит:
- таблицу рецептов (QTableWidget)
- поля добавления/редактирования
- кнопки Add, Edit, Delete, Random
- график активности (matplotlib)
- лог (QTextEdit)
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QTextEdit,
    QLineEdit, QLabel, QMessageBox, QSplitter, QDialog, QFormLayout, QTextBrowser, QStatusBar
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import logging
import PySide6.QtWidgets as QtW

from .models import Recipe
from .logger_config import QTextEditHandler


class MainWindow(QMainWindow):
    def __init__(self, controller, logger=None):
        super().__init__()
        self.controller = controller
        self.logger = logger or logging.getLogger(__name__)
        self.setWindowTitle("Генератор случайных рецептов")
        self.resize(1000, 700)

        self._build_ui()
        self._connect_handlers()
        self.refresh_all()

    def _build_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()

        # верх: таблица и кнопки
        top_layout = QHBoxLayout()

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Теги", "Создано"])
        self.table.setSelectionBehavior(QtW.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QtW.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setColumnWidth(1, 400)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_random = QPushButton("Случайный рецепт")
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_edit)
        btn_row.addWidget(self.btn_delete)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_random)
        left_layout.addLayout(btn_row)

        # правая панель: форма добавления + лог
        right_layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.input_title = QLineEdit()
        self.input_tags = QLineEdit()
        self.input_ingredients = QTextEdit()
        self.input_steps = QTextEdit()
        self.btn_add_quick = QPushButton("Быстро добавить (из формы)")

        form_layout.addRow(QLabel("Название:"), self.input_title)
        form_layout.addRow(QLabel("Теги (через запятую):"), self.input_tags)
        form_layout.addRow(QLabel("Ингредиенты:"), self.input_ingredients)
        form_layout.addRow(QLabel("Шаги:"), self.input_steps)
        right_layout.addLayout(form_layout)
        right_layout.addWidget(self.btn_add_quick)

        # Лог
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        right_layout.addWidget(QLabel("Лог действий:"))
        right_layout.addWidget(self.log_widget, stretch=1)

        # Splitter: таблица слева, форма+лог справа
        splitter = QSplitter(Qt.Horizontal)
        left_container = QWidget()
        left_container.setLayout(left_layout)
        right_container = QWidget()
        right_container.setLayout(right_layout)
        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        # график активности (внизу)
        self.figure = Figure(figsize=(5, 2))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(QLabel("Активность (добавления по датам):"))
        main_layout.addWidget(self.canvas, stretch=0)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # статус-бар
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Готово")

        # подключаем логгер к виджету
        qhandler = QTextEditHandler(self.log_widget.append)
        self.logger.handlers = []  # убираем внешние хендлеры (чтобы не дублировать)
        self.logger.addHandler(qhandler)
        self.logger.setLevel(logging.INFO)

    def _connect_handlers(self):
        self.btn_add.clicked.connect(self.show_add_dialog)
        self.btn_add_quick.clicked.connect(self.on_quick_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_random.clicked.connect(self.on_random)
        self.table.cellDoubleClicked.connect(self.on_table_double)

    # -----------------------
    # Обновления UI
    # -----------------------
    def refresh_all(self):
        self.refresh_table()
        self.refresh_plot()

    def refresh_table(self):
        try:
            recipes = self.controller.list_recipes()
            self.table.setRowCount(len(recipes))
            for i, r in enumerate(recipes):
                self.table.setItem(i, 0, QTableWidgetItem(str(r.id)))
                self.table.setItem(i, 1, QTableWidgetItem(r.title))
                self.table.setItem(i, 2, QTableWidgetItem(r.tags))
                self.table.setItem(i, 3, QTableWidgetItem(r.created_at))
            self.statusBar().showMessage(f"Загружено {len(recipes)} рецептов")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить рецепты:\n{e}")
            self.logger.exception("Ошибка при refresh_table")

    def refresh_plot(self):
        stats = self.controller.activity_stats()
        self.figure.clear()
        ax = self.figure.subplots()
        if not stats:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center')
            self.canvas.draw()
            return
        s = pd.Series(stats)
        s.index = pd.to_datetime(s.index)
        s = s.sort_index()
        ax.bar(s.index.strftime("%Y-%m-%d"), s.values)
        ax.set_xticks(range(len(s.index)))
        ax.set_xticklabels(
            [d.strftime("%Y-%m-%d") for d in s.index],
            rotation=45, ha='right', fontsize=8
        )
        ax.set_ylabel("Кол-во")
        ax.set_title("Добавления по датам")
        self.figure.tight_layout()
        self.canvas.draw()

    # -----------------------
    # События / действия
    # -----------------------
    def on_quick_add(self):
        title = self.input_title.text()
        tags = self.input_tags.text()
        ingredients = self.input_ingredients.toPlainText()
        steps = self.input_steps.toPlainText()
        try:
            rid = self.controller.add_recipe(title, ingredients, steps, tags)
            self.logger.info(f"Быстро добавлен рецепт id={rid}")
            self.input_title.clear()
            self.input_tags.clear()
            self.input_ingredients.clear()
            self.input_steps.clear()
            self.refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка при добавлении", str(e))
            self.logger.exception("Ошибка on_quick_add")

    def show_add_dialog(self):
        dlg = RecipeDialog(parent=self, title="Добавить рецепт")
        if dlg.exec():
            data = dlg.get_data()
            try:
                rid = self.controller.add_recipe(**data)
                self.logger.info(f"Добавлен рецепт id={rid} через диалог")
                self.refresh_all()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка при добавлении", str(e))
                self.logger.exception("Ошибка show_add_dialog")

    def on_table_double(self, row, col):
        try:
            item = self.table.item(row, 0)
            if not item:
                return
            recipe_id = int(item.text())
            recipe = self.controller.get_recipe(recipe_id)
            dlg = RecipeDialog(parent=self, title="Просмотр/Редактирование", recipe=recipe)
            if dlg.exec():
                data = dlg.get_data()
                try:
                    self.controller.edit_recipe(recipe_id=recipe.id, **data)
                    self.logger.info(f"Редактирование через диалог id={recipe_id}")
                    self.refresh_all()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка при обновлении", str(e))
                    self.logger.exception("Ошибка on_table_double save")
        except Exception:
            self.logger.exception("Ошибка on_table_double")

    def on_edit(self):
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.information(self, "Редактировать", "Сначала выберите рецепт в таблице")
            return
        row = sel[0].row()
        recipe_id = int(self.table.item(row, 0).text())
        try:
            recipe = self.controller.get_recipe(recipe_id)
            dlg = RecipeDialog(parent=self, title="Редактировать рецепт", recipe=recipe)
            if dlg.exec():
                data = dlg.get_data()
                self.controller.edit_recipe(recipe_id=recipe_id, **data)
                self.logger.info(f"Редактирован рецепт id={recipe_id}")
                self.refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.logger.exception("Ошибка on_edit")

    def on_delete(self):
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.information(self, "Удалить", "Сначала выберите строку")
            return
        row = sel[0].row()
        recipe_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Подтвердить удаление", f"Удалить рецепт id={recipe_id}?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            self.controller.delete_recipe(recipe_id)
            self.logger.info(f"Удалён рецепт id={recipe_id}")
            self.refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка удаления", str(e))
            self.logger.exception("Ошибка on_delete")

    def on_random(self):
        try:
            tag = self.input_tags.text().strip() or None
            r = self.controller.random_recipe(tag_filter=tag)
            self.show_recipe_view(r)
        except Exception as e:
            QMessageBox.information(self, "Нет рецепта", str(e))
            self.logger.exception("Ошибка on_random")

    def show_recipe_view(self, recipe: Recipe):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Рецепт: {recipe.title}")
        dlg.resize(600, 400)
        layout = QVBoxLayout()
        title = QLabel(f"<b>{recipe.title}</b>")
        tags = QLabel(f"<i>Теги: {recipe.tags}</i>")
        created = QLabel(f"<small>Добавлен: {recipe.created_at}</small>")
        ing = QTextBrowser()
        ing.setPlainText(recipe.ingredients)
        steps = QTextBrowser()
        steps.setPlainText(recipe.steps)
        layout.addWidget(title)
        layout.addWidget(tags)
        layout.addWidget(created)
        layout.addWidget(QLabel("Ингредиенты:"))
        layout.addWidget(ing)
        layout.addWidget(QLabel("Шаги:"))
        layout.addWidget(steps)
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close)
        dlg.setLayout(layout)
        dlg.exec()


class RecipeDialog(QDialog):
    """Диалог добавления/редактирования рецепта."""
    def __init__(self, parent=None, title="Рецепт", recipe: Recipe = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.recipe = recipe
        self._build()

    def _build(self):
        self.layout = QVBoxLayout()
        form = QFormLayout()
        self.input_title = QLineEdit()
        self.input_tags = QLineEdit()
        self.input_ingredients = QTextEdit()
        self.input_steps = QTextEdit()
        if self.recipe:
            self.input_title.setText(self.recipe.title)
            self.input_tags.setText(self.recipe.tags)
            self.input_ingredients.setPlainText(self.recipe.ingredients)
            self.input_steps.setPlainText(self.recipe.steps)
        form.addRow("Название:", self.input_title)
        form.addRow("Теги:", self.input_tags)
        form.addRow("Ингредиенты:", self.input_ingredients)
        form.addRow("Шаги:", self.input_steps)
        self.layout.addLayout(form)
        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить")
        self.btn_cancel = QPushButton("Отмена")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_cancel)
        self.layout.addLayout(btn_row)
        self.setLayout(self.layout)

    def get_data(self):
        return dict(
            title=self.input_title.text(),
            tags=self.input_tags.text(),
            ingredients=self.input_ingredients.toPlainText(),
            steps=self.input_steps.toPlainText()
        )
