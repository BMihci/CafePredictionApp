@echo off
title Kingfool Inc. | AI & Cafe API Server
echo ========================================================
echo KINGFOOL INC. AI & CAFE REST API BACKEND
echo ========================================================
echo Bulut Veritabani: Supabase Bagli
echo API Adresi: http://localhost:8000
echo Swagger Docs: http://localhost:8000/docs
echo ========================================================
cd /d "%~dp0"
python api/main.py
pause
