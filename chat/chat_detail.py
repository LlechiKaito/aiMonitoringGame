import flet as ft

def chat_detail(page, user, back_callback):
    page.controls.clear()

    # ダミーのチャット履歴（最後の"元気です！"は削除）
    chat_history = [
        {"from": "me", "text": "こんにちは！"},
        {"from": "you", "text": "こんにちは！お元気ですか？"},
    ] if user["name"] == "田中 太郎" else []

    chat_column = ft.Column([], expand=True, scroll="auto", height=200)

    def update_chat():
        chat_column.controls.clear()
        for msg in chat_history:
            align = ft.alignment.center_right if msg["from"] == "me" else ft.alignment.center_left
            color = "blue" if msg["from"] == "me" else "grey"
            chat_column.controls.append(
                ft.Container(
                    content=ft.Text(msg["text"], color="white"),
                    bgcolor=color,
                    alignment=align,
                    padding=10,
                    margin=5,
                    border_radius=10,
                )
            )
        chat_column.update()

    text_field = ft.TextField(label="メッセージを入力...", width=250)

    def on_send(e):
        if text_field.value.strip():
            chat_history.append({"from": "me", "text": text_field.value.strip()})
            update_chat()
            text_field.value = ""
            text_field.update()

    send_btn = ft.ElevatedButton("送信", on_click=on_send)
    back_btn = ft.ElevatedButton("戻る", on_click=back_callback)

    page.add(
        ft.Column(
            [
                ft.Text(f"{user['name']}さんとのチャット", size=20, weight="bold"),
                chat_column,
                ft.Row([text_field, send_btn], alignment=ft.MainAxisAlignment.CENTER),
                back_btn
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )
    update_chat()
    page.update()
