@echo off
start cmd /k "python app.py"
timeout /t 2
start cmd /k "python main.py"