#!/usr/bin/env python3
"""
AI Monitoring Game Backend サーバー起動スクリプト
"""

import uvicorn
import sys
import os

# srcディレクトリをPythonパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    print("🚀 AI Monitoring Game Backend を起動中...")
    print("📖 API ドキュメント: http://localhost:8000/docs")
    print("🔍 ReDoc: http://localhost:8000/redoc")
    print("⏹️  停止するには Ctrl+C を押してください")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 