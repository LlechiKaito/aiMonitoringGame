Python バージョン: 3.13.2  
データベース: SQLite  
ORM: SQLAlchemy

<!-- Pythonの環境構築手順 -->
1. 仮想環境を作成します:
   ```bash
   python3 -m venv environment
   ```
2. 仮想環境を有効化します:
   ```bash
   source environment/bin/activate
   ```
3. 必要なパッケージをインストールします:
   ```bash
   pip install -r requirements.txt
   ```

<!-- データベースの環境構築手順 -->
1. Dockerコンテナを起動します:
   ```bash
   docker compose up
   ```

<!-- テストの実行 -->
1. テストスクリプトを実行します:
   ```bash
   python gameEngine/test.py
   ```
   - 画面が表示されれば成功です。
   - 画面が表示されない場合は失敗です。

<!-- データベースコンテナへのアクセス方法 -->
1. SQLiteコンテナに入るには以下のコマンドを使用します:
   ```bash
   docker exec -it sqlite_container /bin/sh
   ```

現在の課題: SQLAlchemyを使用してORMでデータベース操作が可能かどうかを確認する必要があります。

ビルド方法
```
pyinstaller -windowed main.py
```

エラー表示後、main.specから以下を修正
- icon行をコメントアウト
- Analysisに.pyxresを追加

修正後
```
pyinstaller main.spec
```