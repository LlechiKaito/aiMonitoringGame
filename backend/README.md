# AI Monitoring Game Backend

FastAPIとSQLiteを使用したAIモニタリングゲーム用のバックエンドAPIです。

## 機能概要

このバックエンドAPIは以下の機能を提供します：

- **Memories管理**: AIの記憶データの作成・取得・更新・削除
- **Objects管理**: 監視対象オブジェクトの管理
- **Summaries管理**: オブジェクトの要約データの管理
- **リレーション機能**: Memories/SummariesとObjectsの関連付け

## 技術スタック

- **Python**: 3.8+
- **FastAPI**: 0.115.0+ (高速なWeb APIフレームワーク)
- **SQLAlchemy**: 2.0.0+ (ORM)
- **SQLite**: データベース
- **Pydantic**: 2.10.0+ (データバリデーション)
- **Pytest**: 8.4.1+ (テストフレームワーク)
- **Uvicorn**: ASGI サーバー

## 環境構築

### 1. 前提条件

- Python 3.8以上がインストールされていること
- pip がインストールされていること

### 2. プロジェクトのクローン

```bash
git clone <repository-url>
cd aiMonitoringGame/backend
```

### 3. 仮想環境の作成（推奨）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

### 4. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 5. データベースの初期化

初回実行時に自動的にSQLiteデータベースが作成されます。
データベースファイルは `data/aimonitoringgame.db` に保存されます。

## 実行方法

### 開発環境での実行

```bash
# 方法1: 起動スクリプトを使用（推奨）
python run.py

# 方法2: uvicornコマンドを直接使用
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 方法3: Pythonファイルから直接実行
python src/main.py
```

### 起動確認

サーバー起動後、以下のURLにアクセスしてAPI動作を確認できます：

- **API ドキュメント (Swagger UI)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## テスト実行

```bash
# 全テストの実行
pytest

# 特定のテストファイルの実行
pytest tests/test_memories.py
pytest tests/test_objects.py
pytest tests/test_summaries.py

# 詳細出力付きテスト実行
pytest -v

# カバレッジレポート付きテスト実行
pytest --cov=src tests/
```

## API仕様

### Memories API

| Method | Endpoint | 説明 |
|--------|----------|------|
| POST | `/memories/` | 新しいメモリを作成 |
| GET | `/memories/{memory_id}` | 特定のメモリを取得 |
| GET | `/memories/` | メモリ一覧を取得（object_id必須） |
| PUT | `/memories/{memory_id}` | メモリを更新 |
| DELETE | `/memories/{memory_id}` | メモリを削除 |

### Objects API

| Method | Endpoint | 説明 |
|--------|----------|------|
| POST | `/objects/` | 新しいオブジェクトを作成 |
| GET | `/objects/{object_id}` | 特定のオブジェクトを取得 |
| GET | `/objects/` | オブジェクト一覧を取得（name必須） |
| PUT | `/objects/{object_id}` | オブジェクトを更新 |
| DELETE | `/objects/{object_id}` | オブジェクトを削除 |
| GET | `/objects/{object_id}/memories` | オブジェクトに関連するメモリを取得 |
| GET | `/objects/{object_id}/summaries` | オブジェクトに関連するサマリーを取得 |
| GET | `/objects/{object_id}/details` | オブジェクトの詳細情報を取得 |

### Summaries API

| Method | Endpoint | 説明 |
|--------|----------|------|
| POST | `/summaries/` | 新しいサマリーを作成 |
| GET | `/summaries/{summary_id}` | 特定のサマリーを取得 |
| GET | `/summaries/` | サマリー一覧を取得（object_id必須） |
| PUT | `/summaries/{summary_id}` | サマリーを更新 |
| DELETE | `/summaries/{summary_id}` | サマリーを削除 |

## データモデル

### Memory

```python
class Memory(BaseModel):
    id: int
    object_id: int
    content: str
    importance: int = Field(default=5, description="重要度（1-9の整数値）")
    timestamp: datetime
    last_accessed: datetime
```

### Object

```python
class Object(BaseModel):
    id: int
    name: str
    summary: str
    description: str
    photos: Optional[str] = "[]"  # JSON文字列として配列を保存
```

### Summary

```python
class Summary(BaseModel):
    id: int
    object_id: int
    key_features: str
    current_daily_tasks: str
    recent_progress_feelings: str
    created_at: datetime
```

## バリデーション仕様

### 入力値検証

- **文字列フィールド**: 1文字以上の入力が必要
- **重要度（importance）**: 1-9の範囲の整数値
- **JSON形式（photos）**: 有効なJSON文字列形式

### エラーハンドリング

- **400 Bad Request**: 入力値が無効な場合
- **404 Not Found**: 指定されたリソースが存在しない場合
- **422 Unprocessable Entity**: リクエストボディの形式が無効な場合

## プロジェクト構造

```
backend/
├── src/
│   ├── main.py              # メインアプリケーション
│   ├── memories/            # メモリ管理モジュール
│   │   ├── __init__.py
│   │   ├── models.py        # Pydanticデータモデル
│   │   ├── service.py       # ビジネスロジック
│   │   └── router.py        # APIエンドポイント
│   ├── objects/             # オブジェクト管理モジュール
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── service.py
│   │   └── router.py
│   ├── summaries/           # サマリー管理モジュール
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── service.py
│   │   └── router.py
│   └── utils/               # ユーティリティ
│       ├── __init__.py
│       ├── database.py      # データベース設定
│       └── db_models.py     # SQLAlchemyモデル
├── tests/                   # テストコード
│   ├── __init__.py
│   ├── conftest.py         # テスト設定
│   ├── test_memories.py    # メモリテスト
│   ├── test_objects.py     # オブジェクトテスト
│   └── test_summaries.py   # サマリーテスト
├── data/                    # データベースファイル
│   └── aimonitoringgame.db  # SQLiteデータベース
├── requirements.txt         # 依存関係
├── run.py                  # 起動スクリプト
├── pytest.ini             # テスト設定
└── README.md               # プロジェクト説明
```

## 使用例

### メモリの作成

```bash
curl -X POST "http://localhost:8000/memories/" \
  -H "Content-Type: application/json" \
  -d '{
    "object_id": 1,
    "content": "重要な記憶データ",
    "importance": 8
  }'
```

### オブジェクトの取得

```bash
curl -X GET "http://localhost:8000/objects/?name=テスト"
```

### オブジェクトの詳細情報取得

```bash
curl -X GET "http://localhost:8000/objects/1/details?memory_limit=5&summary_limit=3"
```

## 設定

### データベース設定

デフォルトではSQLiteを使用しますが、環境変数でデータベースURLを変更できます：

```bash
export DATABASE_URL="sqlite:///./data/aimonitoringgame.db"
```

### CORS設定

現在は開発用に全オリジンを許可しています。本番環境では適切なオリジンを設定してください。

## トラブルシューティング

### よくある問題

1. **ポート8000が使用中**: `--port`オプションで別のポートを指定
2. **データベースエラー**: `data/`ディレクトリが存在することを確認
3. **インポートエラー**: `pip install -r requirements.txt`を再実行

### ログ確認

```bash
# 詳細ログ出力
uvicorn src.main:app --reload --log-level debug
```

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。開発に参加する場合は、まずテストを実行して既存の機能が動作することを確認してください。 