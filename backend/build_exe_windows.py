#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows用 AI Monitoring Game Backend EXE化スクリプト
"""

import os
import sys
import subprocess
import shutil

def build_exe():
    """Windows用EXEファイルを作成"""
    print("🔨 Windows用 AI Monitoring Game Backend をEXE化しています...")
    
    # PyInstallerコマンドを実行
    cmd = [
        "pyinstaller",
        "--onefile",                 # 1つのEXEファイルにまとめる
        "--name", "AIMonitoringGameBackend",  # EXEファイル名
        "--console",                 # コンソールウィンドウを表示
        "--hidden-import", "fastapi",
        "--hidden-import", "uvicorn",
        "--hidden-import", "sqlalchemy",
        "--hidden-import", "pydantic",
        "--hidden-import", "starlette",
        "--hidden-import", "src.main",
        "--hidden-import", "src.memories",
        "--hidden-import", "src.objects", 
        "--hidden-import", "src.summaries",
        "--hidden-import", "src.utils",
        "--add-data", "src;src",     # srcフォルダをバンドル（Windows用のセパレータ）
        "--distpath", "dist",        # 出力ディレクトリ
        "--workpath", "build",       # 作業ディレクトリ
        "--clean",                   # 古いビルドファイルを削除
        "run.py"                     # エントリーポイント
    ]
    
    # アイコンファイルがあれば追加
    if os.path.exists("icon.ico"):
        cmd.extend(["--icon", "icon.ico"])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ EXE化が完了しました！")
        print(f"📁 出力ディレクトリ: {os.path.abspath('dist')}")
        
        # 作成されたファイルを確認
        dist_files = os.listdir("dist")
        print("📦 作成されたファイル:")
        for file in dist_files:
            file_path = os.path.join("dist", file)
            size = os.path.getsize(file_path)
            print(f"  - {file} ({size:,} bytes)")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ EXE化に失敗しました: {e}")
        print(f"エラー出力: {e.stderr}")
        return False

def create_run_script():
    """実行用のバッチファイルを作成"""
    batch_content = """@echo off
title AI Monitoring Game Backend
echo ============================================
echo   AI Monitoring Game Backend
echo ============================================
echo.
echo Starting server...
echo API Documentation: http://localhost:8000/docs
echo ReDoc: http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.
AIMonitoringGameBackend.exe
echo.
echo Server has stopped.
pause
"""
    
    with open("dist/run_backend.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print("📝 実行用バッチファイル (run_backend.bat) を作成しました")

def create_readme():
    """ReadMeファイルを作成"""
    readme_content = """# AI Monitoring Game Backend

## 使用方法

### 1. 基本的な起動方法
- `run_backend.bat` をダブルクリックして実行
- または、コマンドプロンプトで `AIMonitoringGameBackend.exe` を実行

### 2. アクセス方法
- API文書: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 停止方法
- コンソールウィンドウで `Ctrl+C` を押す
- またはウィンドウを閉じる

### 4. データベース
- SQLiteデータベースファイル `aimonitoringgame.db` が自動作成されます
- データはローカルに保存されます

## システム要件
- Windows 10 以上
- ネットワーク接続（API使用時）

## トラブルシューティング

### ポートエラーが発生する場合
- 別のアプリケーションが8000番ポートを使用している可能性があります
- 該当アプリケーションを終了してから再度実行してください

### ファイアウォールの警告
- Windowsファイアウォールが警告を表示する場合があります
- 「アクセスを許可する」を選択してください

## サポート
問題が発生した場合は、以下を確認してください：
1. ポート8000が使用可能か
2. ファイアウォールの設定
3. ウイルス対策ソフトの除外設定
"""
    
    with open("dist/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("📄 ReadMeファイル (README.txt) を作成しました")

def main():
    """メイン処理"""
    print("🚀 AI Monitoring Game Backend Windows EXE化ツール")
    print("=" * 60)
    
    if build_exe():
        create_run_script()
        create_readme()
        print("\n🎉 EXE化が完了しました！")
        print("📁 'dist' フォルダ内にEXEファイルが作成されました")
        print("\n🔧 使用方法:")
        print("  1. 'dist' フォルダを任意の場所にコピー")
        print("  2. 'run_backend.bat' をダブルクリックして実行")
        print("  3. http://localhost:8000/docs でAPI文書にアクセス")
        print("\n📦 配布用ファイル:")
        print("  - AIMonitoringGameBackend.exe (メインプログラム)")
        print("  - run_backend.bat (実行用バッチファイル)")
        print("  - README.txt (使用方法)")
    else:
        print("\n❌ EXE化に失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main() 