# AI Monitoring Game Backend

FastAPIを使用したAIモニタリングゲーム用のバックエンドAPIです。

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. サーバーの起動

```bash
# 方法1: Pythonファイルから直接実行
python src/main.py

# 方法2: uvicornコマンドを使用
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. APIドキュメントの確認

サーバー起動後、以下のURLでAPIドキュメントを確認できます：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API エンドポイント

### 基本エンドポイント
- `GET /` - ルートエンドポイント
- `GET /health` - ヘルスチェック

### ゲームデータ管理
- `GET /games` - 全ゲームデータの取得
- `GET /games/{game_id}` - 特定のゲームデータの取得
- `POST /games` - 新しいゲームデータの作成
- `PUT /games/{game_id}` - ゲームデータの更新
- `DELETE /games/{game_id}` - ゲームデータの削除

### メモリ管理 (Memories)
- `POST /memories/` - 新しいメモリを作成
- `GET /memories/{memory_id}` - 特定のメモリを取得
- `GET /memories/` - 条件に基づいてメモリを取得
- `PUT /memories/{memory_id}` - メモリを更新
- `DELETE /memories/{memory_id}` - メモリを削除
- `GET /memories/stats/{user_id}` - ユーザーのメモリ統計を取得

### オブジェクト管理 (Objects)
- `POST /objects/` - 新しいオブジェクトを作成
- `GET /objects/{object_id}` - 特定のオブジェクトを取得
- `GET /objects/` - 条件に基づいてオブジェクトを取得
- `PUT /objects/{object_id}` - オブジェクトを更新
- `DELETE /objects/{object_id}` - オブジェクトを削除
- `GET /objects/{object_id}/memories` - オブジェクトに関連するメモリを取得
- `GET /objects/{object_id}/summaries` - オブジェクトに関連するサマリーを取得
- `GET /objects/{object_id}/details` - オブジェクトの詳細情報を取得（メモリとサマリーを含む）

### サマリー管理 (Summaries)
- `POST /summaries/` - 新しいサマリーを作成
- `GET /summaries/{summary_id}` - 特定のサマリーを取得
- `GET /summaries/` - 条件に基づいてサマリーを取得
- `PUT /summaries/{summary_id}` - サマリーを更新
- `DELETE /summaries/{summary_id}` - サマリーを削除

## データモデル

### GameData
```python
class GameData(BaseModel):
    id: Optional[int] = None
    player_name: str
    score: int
    timestamp: Optional[str] = None
```

### Memory
```python
class Memory(BaseModel):
    id: Optional[int] = None
    object_id: int
    content: str
    importance: float = 0.5
    timestamp: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
```

### Object
```python
class Object(BaseModel):
    id: Optional[int] = None
    name: str
    summary: str
    description: str
```

### Summary
```python
class Summary(BaseModel):
    id: Optional[int] = None
    object_id: int
    key_features: str
    current_daily_tasks: str
    recent_progress_feelings: str
    created_at: Optional[datetime] = None
```

## プロジェクト構造

```
backend/
├── src/
│   ├── main.py              # メインアプリケーションファイル
│   ├── memories/            # メモリ関連モジュール
│   │   ├── __init__.py
│   │   ├── models.py        # データモデル
│   │   ├── service.py       # ビジネスロジック
│   │   └── router.py        # APIエンドポイント
│   ├── objects/             # オブジェクト関連モジュール
│   │   ├── __init__.py
│   │   ├── models.py        # データモデル
│   │   ├── service.py       # ビジネスロジック
│   │   └── router.py        # APIエンドポイント
│   └── summaries/           # サマリー関連モジュール
│       ├── __init__.py
│       ├── models.py        # データモデル
│       ├── service.py       # ビジネスロジック
│       └── router.py        # APIエンドポイント
├── requirements.txt         # 依存関係
├── run.py                  # 起動スクリプト
└── README.md               # プロジェクト説明
```

## 開発環境

- Python 3.8+
- FastAPI 0.115.0+
- Uvicorn 0.30.0+
- Pydantic 2.10.0+

## 注意事項

- 現在はインメモリデータストレージを使用しています
- 本番環境では適切なデータベースを使用してください
- CORS設定は開発用に設定されています。本番環境では適切に設定してください 