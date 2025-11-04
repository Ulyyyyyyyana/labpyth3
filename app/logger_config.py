# app/logger_config.py
"""
Настройка логера и handler для QTextEdit (GUI).
"""

import logging
from PySide6.QtCore import QObject, Signal


class QTextEditHandler(logging.Handler):
    """
    Лог-хендлер, который вызывает переданную функцию для добавления строки в QTextEdit.
    append_func должно принимать одну строку.
    """
    def __init__(self, append_func):
        super().__init__()
        self.append_func = append_func

    def emit(self, record):
        try:
            msg = self.format(record)
            # append_func вызывается в GUI-потоке; в простом приложении это безопасно
            self.append_func(msg)
        except Exception:
            self.handleError(record)


def setup_root_logger(level=logging.INFO, handler=None, fmt=None):
    root = logging.getLogger()
    root.setLevel(level)
    if fmt is None:
        fmt = "%(asctime)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)
    if handler:
        handler.setFormatter(formatter)
        root.addHandler(handler)
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        root.addHandler(ch)
    return root
