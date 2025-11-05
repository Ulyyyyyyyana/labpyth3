@echo off
REM Активируем виртуальное окружение
call .venv\Scripts\activate

REM Запускаем приложение
python -m app.main

REM Чтобы окно не закрылось сразу
pause
