@echo off
echo ========================================
echo Historical RAG Backend - Dataset Setup
echo ========================================
echo.

REM Check if dataset exists in root
if exist "..\historical_events_cleaned_full.csv" (
    echo [FOUND] Dataset in root directory
    echo Copying to backend/app/data/documents/...
    copy "..\historical_events_cleaned_full.csv" "app\data\documents\historical_events_cleaned_full.csv"
    if %errorlevel% == 0 (
        echo [SUCCESS] Dataset copied successfully!
    ) else (
        echo [ERROR] Failed to copy dataset
    )
) else if exist "historical_events_cleaned_full.csv" (
    echo [FOUND] Dataset in current directory
    echo Copying to app/data/documents/...
    copy "historical_events_cleaned_full.csv" "app\data\documents\historical_events_cleaned_full.csv"
    if %errorlevel% == 0 (
        echo [SUCCESS] Dataset copied successfully!
    ) else (
        echo [ERROR] Failed to copy dataset
    )
) else (
    echo [NOT FOUND] Dataset file: historical_events_cleaned_full.csv
    echo.
    echo Please place your dataset CSV file in one of these locations:
    echo   1. Root directory: Week2Bootcamp\historical_events_cleaned_full.csv
    echo   2. Backend directory: Week2Bootcamp\backend\historical_events_cleaned_full.csv
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Dataset Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Copy .env.example to .env
echo   2. Run: pip install -r requirements.txt
echo   3. Run: python -m uvicorn app.main:app --reload
echo.
pause

