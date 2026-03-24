@echo off
cd /d %~dp0

echo ============================
echo 支援記録システム 起動
echo ============================

REM 1. Python が使えるか確認
python --version >nul 2>&1
if errorlevel 1 (
    echo [エラー] Python が見つかりません。
    echo Python をインストールしてから再実行してください。
    pause
    exit /b
)

REM 2. .env がなければ env.example から作成
if not exist .env (
    if exist env.example (
        copy env.example .env >nul
        echo .env を作成しました
    ) else (
        echo [注意] env.example が見つかりません
    )
)

REM 3. 仮想環境がなければ作成
if not exist .\.venv\Scripts\python.exe (
    echo 仮想環境を作成しています...
    python -m venv .venv
)

REM 4. 仮想環境を有効化
call .\.venv\Scripts\activate.bat

REM 5. ライブラリをインストール
echo ライブラリを確認しています...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 6. アプリ起動
echo アプリを起動します...
python app.py

pause