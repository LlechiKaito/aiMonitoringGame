import flet as ft

def object_detail(page, person, back_callback):
    page.controls.clear()
    page.add(
        ft.Column(
            [
                ft.Text(f"名前: {person['name']}", size=18),
                ft.Text(f"年齢: {person['age']}"),
                ft.Text(f"職業: {person['job']}"),
                ft.ElevatedButton("戻る", on_click=back_callback)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )
    page.update()
