import flet as ft

def object_detail(page, obj, back_callback):
    page.controls.clear()
    if obj.get("type") == "person":
        detail_controls = [
            ft.Text(f"名前: {obj['name']}", size=18),
            ft.Text(f"年齢: {obj['age']}"),
            ft.Text(f"職業: {obj['job']}"),
        ]
    else:
        detail_controls = [
            ft.Text(f"名前: {obj['name']}", size=18),
            ft.Text(f"状態: {obj.get('status', '不明')}"),
        ]
    detail_controls.append(ft.ElevatedButton("戻る", on_click=back_callback))
    page.add(
        ft.Column(
            detail_controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )
    page.update()
