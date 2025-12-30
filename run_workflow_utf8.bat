@echo off
REM Set UTF-8 encoding for Chinese characters
chcp 65001 > nul

REM Set Python encoding
set PYTHONIOENCODING=utf-8

REM Run the workflow test
python test_full_workflow.py

pause
