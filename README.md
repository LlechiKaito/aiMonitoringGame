# ビルド方法
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