@echo off
echo Initializing database...
cd ..\database
python init_db.py
cd ..\scripts
pause
