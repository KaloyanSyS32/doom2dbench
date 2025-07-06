@echo off
title Doom2DBench
cls
echo ===========================
echo         doom2dbench
echo ===========================
echo.
timeout 3 >nul
cls
echo Checking for pygame package 
pip install pygame >nul
timeout 3 >nul
cls
timeout 3 >nul
cls
python doombench.py >nul
cls
