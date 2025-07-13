#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Flash 2.0 + Flash Attention 2.0 統合サンプル
AI Monitoring Game Backend用セマンティック検索機能
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# 依存関係の確認とインストール
try:
    import torch
    from sentence_transformers import SentenceTransformer
    import google.generativeai as genai
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import pytz
except ImportError as e:
    print(f"必要な依存関係がインストールされていません: {e}")
    print("以下のコマンドで依存関係をインストールしてください:")
    print("pip install torch sentence-transformers google-generativeai scikit-learn fastapi uvicorn pydantic pytz")
    sys.exit(1)

# Flash Attentionの確認（オプション）
try:
    from flash_attn import flash_attn_func
    FLASH_ATTENTION_AVAILABLE = True
    print("✅ Flash Attention 2.0 が利用可能です")
except ImportError:
    FLASH_ATTENTION_AVAILABLE = False
    print("⚠️  Flash Attention 2.0 が利用できません。通常のコサイン類似度を使用します。")
    flash_attn_func = None

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
JST = pytz.timezone('Asia/Tokyo')

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 10
    use_flash_attention: bool = True
    use_gemini_enhancement: bool = True

class SemanticSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query_enhanced: Optional[str] = None
    processing_time: float
    model_info: Dict[str, Any]

class GeminiFlash2SemanticSearch:
    """
    Gemini Flash 2.0 と Flash Attention 2.0 を統合したセマンティック検索
    """
    
    def __init__(self):
        self.setup_gemini()
        self.setup_embeddings()
        self.setup_flash_attention()
        self.sample_memories = self.create_sample_data()
        
    def setup_gemini(self):
        """Gemini Flash 2.0の設定"""
        if GEMINI_API_KEY == "your-api-key-here":
            logger.warning("Gemini API Keyが設定されていません。環境変数GEMINI_API_KEYを設定してください。")
            self.gemini_available = False
        else:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.gemini_available = True
                logger.info("✅ Gemini Flash 2.0 初期化成功")
            except Exception as e:
                logger.error(f"❌ Gemini Flash 2.0 初期化失敗: {e}")
                self.gemini_available = False
    
    def setup_embeddings(self):
        """埋め込みモデルの設定"""
        try:
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            self.embedding_model.eval()
            logger.info(f"✅ 埋め込みモデル読み込み成功: {EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"❌ 埋め込みモデル読み込み失敗: {e}")
            raise
    
    def setup_flash_attention(self):
        """Flash Attention 2.0の設定"""
        if not FLASH_ATTENTION_AVAILABLE:
            self.flash_attention_available = False
            logger.warning("⚠️ Flash Attention 2.0 未インストールのため無効化")
            return
            
        try:
            if torch.cuda.is_available():
                # Flash Attention テスト
                test_q = torch.randn(1, 10, 8, 64, dtype=torch.float16, device='cuda')
                test_k = torch.randn(1, 10, 8, 64, dtype=torch.float16, device='cuda')
                test_v = torch.randn(1, 10, 8, 64, dtype=torch.float16, device='cuda')
                
                with torch.no_grad():
                    _ = flash_attn_func(test_q, test_k, test_v)
                
                self.flash_attention_available = True
                logger.info("✅ Flash Attention 2.0 初期化成功")
            else:
                self.flash_attention_available = False
                logger.warning("⚠️ CUDA未対応のため Flash Attention 2.0 を無効化")
        except Exception as e:
            logger.error(f"❌ Flash Attention 2.0 初期化失敗: {e}")
            self.flash_attention_available = False
    
    def create_sample_data(self) -> List[Dict[str, Any]]:
        """サンプルメモリデータの作成"""
        return [
            {
                "id": 1,
                "content": "今日は新しいAI技術について学んだ。特にTransformerアーキテクチャの注意機構が興味深かった。",
                "importance": 8,
                "last_accessed": datetime.now(JST),
                "created_at": datetime.now(JST)
            },
            {
                "id": 2,
                "content": "プロジェクトの締切が近づいている。タスクの優先順位を見直す必要がある。",
                "importance": 9,
                "last_accessed": datetime.now(JST),
                "created_at": datetime.now(JST)
            },
            {
                "id": 3,
                "content": "セマンティック検索の実装でFlash Attentionを使用することで大幅な高速化が期待できる。",
                "importance": 7,
                "last_accessed": datetime.now(JST),
                "created_at": datetime.now(JST)
            },
            {
                "id": 4,
                "content": "チームメンバーとのコミュニケーションを改善するためのアイデアを考えた。",
                "importance": 6,
                "last_accessed": datetime.now(JST),
                "created_at": datetime.now(JST)
            },
            {
                "id": 5,
                "content": "Gemini Flash 2.0の新機能を使って、より自然な対話システムを構築したい。",
                "importance": 8,
                "last_accessed": datetime.now(JST),
                "created_at": datetime.now(JST)
            }
        ]
    
    async def enhance_query_with_gemini(self, query: str) -> str:
        """Gemini Flash 2.0を使用したクエリ拡張"""
        if not self.gemini_available:
            return query
        
        try:
            prompt = f"""
            以下の検索クエリを、より効果的なセマンティック検索のために拡張・改善してください。
            関連するキーワードや同義語を含めて、検索精度を向上させてください。
            
            元のクエリ: {query}
            
            拡張されたクエリを日本語で返してください。
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, prompt
            )
            
            enhanced_query = response.text.strip()
            logger.info(f"クエリ拡張: '{query}' -> '{enhanced_query}'")
            return enhanced_query
            
        except Exception as e:
            logger.error(f"Geminiクエリ拡張エラー: {e}")
            return query
    
    def compute_embeddings(self, texts: List[str]) -> np.ndarray:
        """テキストの埋め込み計算"""
        try:
            with torch.no_grad():
                embeddings = self.embedding_model.encode(texts)
            return embeddings
        except Exception as e:
            logger.error(f"埋め込み計算エラー: {e}")
            raise
    
    def compute_similarity_with_flash_attention(self, 
                                              query_embedding: np.ndarray, 
                                              memory_embeddings: np.ndarray) -> np.ndarray:
        """Flash Attention 2.0を使用した類似度計算"""
        if not self.flash_attention_available or not FLASH_ATTENTION_AVAILABLE:
            return cosine_similarity([query_embedding], memory_embeddings)[0]
        
        try:
            # 埋め込みをFlash Attention形式に変換
            q = torch.tensor(query_embedding, dtype=torch.float16, device='cuda').unsqueeze(0).unsqueeze(0).unsqueeze(0)
            k = torch.tensor(memory_embeddings, dtype=torch.float16, device='cuda').unsqueeze(0).unsqueeze(0)
            v = k.clone()
            
            # Flash Attention実行
            with torch.no_grad():
                attention_output = flash_attn_func(q, k, v, softmax_scale=1.0/np.sqrt(query_embedding.shape[0]))
            
            # 類似度スコアの計算
            similarities = attention_output.squeeze().cpu().numpy()
            
            # 正規化
            similarities = (similarities - similarities.min()) / (similarities.max() - similarities.min())
            
            return similarities
            
        except Exception as e:
            logger.error(f"Flash Attention類似度計算エラー: {e}")
            # フォールバックとして通常のコサイン類似度を使用
            return cosine_similarity([query_embedding], memory_embeddings)[0]
    
    async def search(self, request: SemanticSearchRequest) -> SemanticSearchResponse:
        """セマンティック検索の実行"""
        start_time = datetime.now()
        
        # クエリの拡張
        enhanced_query = request.query
        if request.use_gemini_enhancement:
            enhanced_query = await self.enhance_query_with_gemini(request.query)
        
        # 埋め込みの計算
        query_embedding = self.compute_embeddings([enhanced_query])[0]
        memory_texts = [memory["content"] for memory in self.sample_memories]
        memory_embeddings = self.compute_embeddings(memory_texts)
        
        # 類似度計算
        if request.use_flash_attention:
            similarities = self.compute_similarity_with_flash_attention(query_embedding, memory_embeddings)
        else:
            similarities = cosine_similarity([query_embedding], memory_embeddings)[0]
        
        # 結果の整理
        results = []
        for i, similarity in enumerate(similarities):
            memory = self.sample_memories[i].copy()
            memory["similarity_score"] = float(similarity)
            memory["last_accessed"] = memory["last_accessed"].isoformat()
            memory["created_at"] = memory["created_at"].isoformat()
            results.append(memory)
        
        # 類似度順でソート
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        results = results[:request.limit]
        
        # 処理時間の計算
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # モデル情報
        model_info = {
            "embedding_model": EMBEDDING_MODEL,
            "device": DEVICE,
            "flash_attention_enabled": request.use_flash_attention and self.flash_attention_available,
            "gemini_enhancement_enabled": request.use_gemini_enhancement and self.gemini_available,
            "cuda_available": torch.cuda.is_available()
        }
        
        return SemanticSearchResponse(
            results=results,
            query_enhanced=enhanced_query if enhanced_query != request.query else None,
            processing_time=processing_time,
            model_info=model_info
        )

# FastAPIアプリケーション
app = FastAPI(
    title="Gemini Flash 2.0 + Flash Attention 2.0 セマンティック検索",
    description="AI Monitoring Game Backend用の高速セマンティック検索API",
    version="1.0.0"
)

# セマンティック検索インスタンス
semantic_search = GeminiFlash2SemanticSearch()

@app.post("/search", response_model=SemanticSearchResponse)
async def search_memories(request: SemanticSearchRequest):
    """
    セマンティック検索API
    """
    try:
        return await semantic_search.search(request)
    except Exception as e:
        logger.error(f"検索エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    ヘルスチェックAPI
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(JST).isoformat(),
        "cuda_available": torch.cuda.is_available(),
        "flash_attention_available": semantic_search.flash_attention_available,
        "gemini_available": semantic_search.gemini_available
    }

def main():
    """メイン実行関数"""
    print("🚀 Gemini Flash 2.0 + Flash Attention 2.0 セマンティック検索 起動中...")
    print("📖 API ドキュメント: http://localhost:8000/docs")
    print("🔍 ReDoc: http://localhost:8000/redoc")
    print("💻 CUDA利用可能:", torch.cuda.is_available())
    print("⚡ Flash Attention 2.0 対応:", semantic_search.flash_attention_available)
    print("🧠 Gemini Flash 2.0 対応:", semantic_search.gemini_available)
    print("⏹️  停止するには Ctrl+C を押してください")
    print("-" * 50)
    
    # サーバー起動
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main() 