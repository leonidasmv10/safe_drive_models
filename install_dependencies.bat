@echo off

echo Update virtual environment...
py -3.11 -m pip install --upgrade pip

echo Installing virtualenv...
py -3.11 -m pip install virtualenv

echo Creating virtual environment...
py -3.11 -m venv env

echo Activating virtual environment...
call .\env\Scripts\activate

echo Installing API requirements...
pip install -r requirements.txt

echo Installation completed.
pause