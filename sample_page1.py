import flet as ft

def sample_page1(page, on_back):
    count = ft.Text("0", size=30)
    def inc(e):
        count.value = str(int(count.value) + 1)
        count.update()
    page.controls.clear()
    page.add(
        ft.Column(
            [
                ft.Text("サンプルページ1: カウンター", size=20),
                count,
                ft.ElevatedButton("カウントアップ", on_click=inc),
                ft.ElevatedButton("戻る", on_click=on_back)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )
    page.update()
