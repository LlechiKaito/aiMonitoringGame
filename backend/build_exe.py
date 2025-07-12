#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Monitoring Game Backend をEXE化するスクリプト
"""

import os
import sys
import subprocess
import shutil

def build_exe():
    """EXEファイルを作成"""
    print("🔨 AI Monitoring Game Backend をEXE化しています...")
    
    # PyInstallerコマンドを実行
    cmd = [
        "pyinstaller",
        "--onefile",                 # 1つのEXEファイルにまとめる
        "--name", "AIMonitoringGameBackend",  # EXEファイル名
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
        "--add-data", "src:src",     # srcフォルダをバンドル
        "--distpath", "dist",        # 出力ディレクトリ
        "--workpath", "build",       # 作業ディレクトリ
        "--clean",                   # 古いビルドファイルを削除
        "run.py"                     # エントリーポイント
    ]
    
    # Windows用の追加設定
    if sys.platform == "win32":
        cmd.extend([
            "--console",             # コンソールウィンドウを表示
            "--icon", "icon.ico"     # アイコン（もしあれば）
        ])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ EXE化が完了しました！")
        print(f"📁 出力ディレクトリ: {os.path.abspath('dist')}")
        
        # 作成されたファイルを確認
        dist_files = os.listdir("dist")
        print("📦 作成されたファイル:")
        for file in dist_files:
            print(f"  - {file}")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ EXE化に失敗しました: {e}")
        print(f"エラー出力: {e.stderr}")
        return False

def create_run_script():
    """実行用のバッチファイルを作成"""
    batch_content = """@echo off
echo Starting AI Monitoring Game Backend...
echo API Documentation: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
AIMonitoringGameBackend.exe
pause
"""
    
    with open("dist/run_backend.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print("📝 実行用バッチファイル (run_backend.bat) を作成しました")

def main():
    """メイン処理"""
    print("🚀 AI Monitoring Game Backend EXE化ツール")
    print("=" * 50)
    
    if build_exe():
        create_run_script()
        print("\n🎉 EXE化が完了しました！")
        print("📁 'dist' フォルダ内にEXEファイルが作成されました")
        print("🔧 使用方法:")
        print("  1. 'dist' フォルダを任意の場所にコピー")
        print("  2. 'run_backend.bat' をダブルクリックして実行")
        print("  3. http://localhost:8000/docs でAPI文書にアクセス")
    else:
        print("\n❌ EXE化に失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main() 