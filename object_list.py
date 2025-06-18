import flet as ft
from objects.object_detail import object_detail

def object_list(page, back_callback):
    # オブジェクト（人・部屋・車など）のリスト
    objects = [
        {"type": "person", "name": "田中 太郎", "age": 28, "job": "エンジニア"},
        {"type": "person", "name": "佐藤 花子", "age": 34, "job": "デザイナー"},
        {"type": "person", "name": "鈴木 次郎", "age": 22, "job": "学生"},
        {"type": "person", "name": "高橋 美咲", "age": 41, "job": "マネージャー"},
        {"type": "person", "name": "伊藤 健一", "age": 30, "job": "営業"},
        {"type": "person", "name": "山本 直樹", "age": 25, "job": "プログラマー"},
        {"type": "person", "name": "中村 由美", "age": 29, "job": "マーケター"},
        {"type": "person", "name": "小林 拓也", "age": 33, "job": "コンサルタント"},
        {"type": "person", "name": "加藤 さくら", "age": 27, "job": "ライター"},
        {"type": "person", "name": "渡辺 大輔", "age": 38, "job": "ディレクター"},
        {"type": "person", "name": "松本 佳奈", "age": 24, "job": "アナリスト"},
        {"type": "person", "name": "斎藤 剛", "age": 36, "job": "プロデューサー"},
        # 以下は物の例（部屋・車など）
        {"type": "room", "name": "子供部屋", "status": "空室"},
        {"type": "room", "name": "リビング", "status": "在室"},
        {"type": "car", "name": "社用車A", "status": "駐車場"},
    ]

    page.controls.clear()

    def on_object_click(e, obj):
        # オブジェクト選択時に詳細画面へ遷移
        object_detail(page, obj, lambda e=None: object_list(page, back_callback))

    # オブジェクト名のリスト表示（クリックで詳細へ）
    name_list = ft.ListView(
        controls=[
            ft.ListTile(
                title=ft.Text(
                    f"{obj['name']}"
                ),
                on_click=lambda e, o=obj: on_object_click(e, o)
            ) for obj in objects
        ],
        expand=False,
        height=300,  # 高さを指定してスクロール可能に
        spacing=10,
    )
    back_btn = ft.ElevatedButton("戻る", on_click=back_callback)
    page.add(
        ft.Column(
            [
                ft.Text("オブジェクトリスト", size=20, weight="bold"),
                ft.Text("下にスクロールできます", size=14, color="grey"),
                name_list,
                back_btn
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )
    page.update()
