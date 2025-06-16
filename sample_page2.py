import flet as ft

def sample_page2(page, on_back):
    cb1 = ft.Checkbox(label="項目A")
    cb2 = ft.Checkbox(label="項目B")
    cb3 = ft.Checkbox(label="項目C")
    page.controls.clear()
    page.add(
        ft.Column(
            [
                ft.Text("サンプルページ2: チェックリスト", size=20),
                cb1, cb2, cb3,
                ft.ElevatedButton("戻る", on_click=on_back)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )
    page.update()
