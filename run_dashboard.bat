@echo off
title FPL Mini-League Dashboard
echo ========================================================
echo   Menjalankan FPL Mini-League Interactive Dashboard...
echo ========================================================
python -m streamlit run app.py --server.port 8501 --server.address localhost
pause
