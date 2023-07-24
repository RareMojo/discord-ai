@echo off

REM Create a virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Update pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

REM Launch src/main.py
python src\main.py

REM Deactivate the virtual environment
call venv\Scripts\deactivate.bat