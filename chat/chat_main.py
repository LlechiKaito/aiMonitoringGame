import flet as ft
from chat.chat_detail import chat_detail

# object_list.pyのobjectsから人間のみ抜粋
USERS = [
    {"name": "田中 太郎", "age": 28, "job": "エンジニア"},
    {"name": "佐藤 花子", "age": 34, "job": "デザイナー"},
    {"name": "鈴木 次郎", "age": 22, "job": "学生"},
    {"name": "高橋 美咲", "age": 41, "job": "マネージャー"},
    {"name": "伊藤 健一", "age": 30, "job": "営業"},
    {"name": "山本 直樹", "age": 25, "job": "プログラマー"},
    {"name": "中村 由美", "age": 29, "job": "マーケター"},
    {"name": "小林 拓也", "age": 33, "job": "コンサルタント"},
    {"name": "加藤 さくら", "age": 27, "job": "ライター"},
    {"name": "渡辺 大輔", "age": 38, "job": "ディレクター"},
    {"name": "松本 佳奈", "age": 24, "job": "アナリスト"},
    {"name": "斎藤 剛", "age": 36, "job": "プロデューサー"},
]

# 1人分だけ適当なチャット履歴
latest_messages = {
    "田中 太郎": "こんにちは！お元気ですか？",
    "佐藤 花子": "",
    "鈴木 次郎": "",
    "高橋 美咲": "",
    "伊藤 健一": "",
    "山本 直樹": "",
    "中村 由美": "",
    "小林 拓也": "",
    "加藤 さくら": "",
    "渡辺 大輔": "",
    "松本 佳奈": "",
    "斎藤 剛": "",
}

def chat_main(page, back_callback):
    page.controls.clear()

    def on_user_click(e, user):
        chat_detail(page, user, lambda e=None: chat_main(page, back_callback))  # チャット詳細画面へ

    user_list = ft.ListView(
        controls=[
            ft.ListTile(
                title=ft.Text(user["name"]),
                subtitle=ft.Text(latest_messages.get(user["name"], "")),
                on_click=lambda e, u=user: on_user_click(e, u)
            ) for user in USERS
        ],
        expand=False,
        height=350,
        spacing=10,
    )

    back_btn = ft.ElevatedButton("戻る", on_click=back_callback)
    page.add(
        ft.Column(
            [
                ft.Text("ユーザーリスト", size=20, weight="bold"),
                ft.Text("チャットしたいユーザーを選択してください", size=14, color="grey"),
                user_list,
                back_btn
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )
    page.update()
