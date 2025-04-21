Python 3.13.2
DB: sqlite
ORM: SQLAlchemy

<!-- pythonの環境構築 -->
python3 -m venv enviroment
source enviroment/bin/activate
pip install -r requirements.txt

<!-- DBの環境構築 -->
docker compose up

<!-- test -->
python gameEngine/test.py
->display ok
->not display not ok

<!-- dbのコンテナの入り方 -->
docker exec -it sqlite_container /bin/sh


今、できていないのは、SQLAlchemyを使った、ORMでのDBの操作が可能かどうか？