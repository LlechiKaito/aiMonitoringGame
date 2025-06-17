import flet as ft
from object_detail import object_detail

def object_list(page, back_callback):
    # 人名リストと詳細データ（人数増加）
    people = [
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

    page.controls.clear()

    def on_name_click(e, person):
        object_detail(page, person, lambda e=None: object_list(page, back_callback))

    name_list = ft.ListView(
        controls=[
            ft.ListTile(
                title=ft.Text(person["name"]),
                on_click=lambda e, p=person: on_name_click(e, p)
            ) for person in people
        ],
        expand=False,
        height=300,  # 高さを指定してスクロール可能に
        spacing=10,
    )
    back_btn = ft.ElevatedButton("戻る", on_click=back_callback)
    page.add(
        ft.Column(
            [ft.Text("人名リスト", size=20, weight="bold"),ft.Text("下にスクロールできます", size=14, color="grey"), name_list, back_btn],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )
    page.update()
