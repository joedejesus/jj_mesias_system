@echo off
setlocal
cd /d %~dp0..
set "VENV_DIR=%CD%\venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
	python -m venv "%VENV_DIR%"
)

"%PYTHON_EXE%" -m pip install --upgrade pip
"%PYTHON_EXE%" -m pip install -r requirements.txt
"%PYTHON_EXE%" -m unittest discover -s tests -p "test_*.py"
endlocal