#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Monitoring Game Backend サーバー起動スクリプト
"""

import uvicorn
import sys
import os

# srcディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# EXE実行かどうかを判断
is_exe = getattr(sys, 'frozen', False)

if __name__ == "__main__":
    print("🚀 AI Monitoring Game Backend を起動中...")
    print("📖 API ドキュメント: http://localhost:8000/docs")
    print("🔍 ReDoc: http://localhost:8000/redoc")
    print("⏹️  停止するには Ctrl+C を押してください")
    
    if is_exe:
        print("🔧 EXE実行モード: ホットリロードは無効です")
    else:
        print("🔧 開発モード: ホットリロードが有効です")
    
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=not is_exe,  # EXE実行時はreloadを無効
        log_level="info"
    ) 