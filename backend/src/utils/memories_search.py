from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import minmax_scale
import numpy as np

class MemoriesSearch:
    def __init__(self, memories: list, embedder: SentenceTransformer = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2"), top_n: int = 5, decay_rate: float = 0.99, alpha_relevance: float = 0.5, alpha_recency: float = 0.25, alpha_importance: float = 0.25):
        self.embedder = embedder
        self.memory_contents = np.array([
            {"id": memory["id"], "object_id": memory["object_id"], "content": memory["content"], "timestamp": memory["timestamp"], "importance": memory["importance"], "last_accessed": memory["last_accessed"]} for memory in memories
        ])
        self.relevance_scores = np.array([])
        self.recency_scores = np.array([])
        self.importance_scores = np.array([])
        self.decay_rate = decay_rate
        self.alpha_relevance = alpha_relevance
        self.alpha_recency = alpha_recency
        self.alpha_importance = alpha_importance
        self.top_n = top_n
        
    def relevance_score(self, query: str):
        query_embedding = self.embedder.encode(np.array([query]))
        memory_embeddings = self.embedder.encode(np.array([memory["content"] for memory in self.memory_contents]))
        
        # 一度に全ての類似度を計算
        similarities = np.array(cosine_similarity(query_embedding, memory_embeddings)[0])
        return similarities
      
    def recency_score(self):
        """新近性スコアの計算（時間単位、1時間ごとの減衰率）"""
        recency_scores = np.array([])
        current_time = datetime.now()
        
        for i, memory in enumerate(self.memory_contents):
            # 時間差を時間単位で計算
            memory_time = datetime.strptime(memory["timestamp"], '%Y-%m-%d %H:%M:%S')
            hours_ago = (current_time - memory_time).total_seconds() / 3600
            
            # 指数減衰を使用（新しいメモリほど高いスコア）
            # 減衰率を1時間で設定された割合だけ減少
            recency_score = self.decay_rate ** hours_ago
            recency_scores = np.append(recency_scores, recency_score)
        
        return recency_scores
      
    def importance_score(self):
        """重要性スコアの計算"""
        importance_scores = np.array([])
        for memory in self.memory_contents:
            importance_scores = np.append(importance_scores, memory["importance"])
        return importance_scores

    def min_max_scale(self, scores: np.array):
        return minmax_scale(scores)
      
    def calculate_scores(self, query: str):
        self.relevance_scores = self.min_max_scale(self.relevance_score(query))
        self.recency_scores = self.min_max_scale(self.recency_score())
        self.importance_scores = self.min_max_scale(self.importance_score())
        self.scores = self.relevance_scores * self.alpha_relevance + self.recency_scores * self.alpha_recency + self.importance_scores * self.alpha_importance
    
    def search(self, query: str):
        self.calculate_scores(query)
        most_similar_memory_indices = self.scores.argsort()[-self.top_n:][::-1]
        most_similar_memory = self.memory_contents[most_similar_memory_indices]
        
        return {
            "memory": most_similar_memory,
            "combined_score": self.scores[most_similar_memory_indices],
            "relevance_score": self.relevance_scores[most_similar_memory_indices],
            "recency_score": self.recency_scores[most_similar_memory_indices],
            "importance_score": self.importance_scores[most_similar_memory_indices],
            "all_scores": self.scores.tolist()
        }
    
    def __main__(self, query: str):
        result = self.search(query)
        print(f"クエリ: {query}")
        print(f"上位{self.top_n}件の結果:")
        print("=" * 50)
        
        for i in range(len(result['memory'])):
            print(f"【{i+1}位】")
            print(f"メモリ: {result['memory'][i]['content']}")
            print(f"組み合わせスコア: {result['combined_score'][i]:.4f}")
            print(f"関連性スコア: {result['relevance_score'][i]:.4f}")
            print(f"新近性スコア: {result['recency_score'][i]:.4f}")
            print(f"重要性スコア: {result['importance_score'][i]:.4f}")
            print("-" * 30)
        
        print(f"全スコア: {result['all_scores']}")
        return result

if __name__ == "__main__":
    memories = [
        {"id": 1, "object_id": 1, "content": "今日は天気が良くて、散歩に行きました。", "timestamp": "2025-07-18 15:30:00", "importance": 1, "last_accessed": "2025-07-18 15:30:00"},
        {"id": 2, "object_id": 1, "content": "昨日は友達と一緒にカラオケに行きました。", "timestamp": "2025-07-17 15:30:00", "importance": 6, "last_accessed": "2025-07-17 15:30:00"},
        {"id": 3, "object_id": 1, "content": "先週は家族と一緒に旅行に行きました。", "timestamp": "2025-07-16 09:00:00", "importance": 5, "last_accessed": "2025-07-16 09:00:00"},
        {"id": 4, "object_id": 1, "content": "一昨日は仕事で忙しくて、夜遅くまで働きました。", "timestamp": "2025-07-15 22:00:00", "importance": 8, "last_accessed": "2025-07-15 22:00:00"},
        {"id": 5, "object_id": 1, "content": "一昨日は友達と一緒にカラオケに行きました。", "timestamp": "2025-07-14 20:00:00", "importance": 2, "last_accessed": "2025-07-14 20:00:00"},
        {"id": 6, "object_id": 1, "content": "先週は家族と一緒に旅行に行きました。", "timestamp": "2025-07-13 14:00:00", "importance": 9, "last_accessed": "2025-07-13 14:00:00"},
        {"id": 7, "object_id": 1, "content": "一昨日は仕事で忙しくて、夜遅くまで働きました。", "timestamp": "2025-07-12 18:30:00", "importance": 4, "last_accessed": "2025-07-12 18:30:00"},
    ]
    embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    memories_search = MemoriesSearch(memories, embedder, top_n=3)
    memories_search.__main__("先週は家族と一緒に過ごしました。")
