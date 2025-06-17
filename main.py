import flet as ft
import sys
import os
import subprocess
import socket
import pyxel_app  # 作成したPyxelモジュールをインポート
from objects.object_list import object_list
from chat.chat_main import chat_main

def main(page: ft.Page):
    page.title = "Flet仮想デスクトップ"
    page.window_width = 400
    page.window_height = 300
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    pyxel_proc = None

    # --- 画面遷移用関数 ---
    def show_initial_screen(e=None):  # ←ここを修正
        page.controls.clear()
        pyxel_btn = ft.ElevatedButton("Pyxel起動", on_click=on_start_pyxel)
        input_btn = ft.ElevatedButton("文字列入力", on_click=show_input_screen)
        list_btn = ft.ElevatedButton("リスト", on_click=lambda e: object_list(page, show_initial_screen))
        sample2_btn = ft.ElevatedButton("チャット", on_click=lambda e: chat_main(page, show_initial_screen))
        page.add(
            ft.Column(
                [pyxel_btn, input_btn, list_btn, sample2_btn],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        )
        page.update()

    def show_input_screen(e=None):
        page.controls.clear()
        text_field = ft.TextField(
            label="メッセージを入力してください...",
            width=300
        )
        def on_send(ev):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(text_field.value.encode("utf-8"), ("127.0.0.1", 50007))
            sock.close() 
            text_field.value = ""
            text_field.update()
        send_btn = ft.ElevatedButton("送信", on_click=on_send)
        back_btn = ft.ElevatedButton("戻る", on_click=lambda e: show_initial_screen())
        page.add(
            ft.Column(
                [text_field, ft.Row([send_btn, back_btn], alignment=ft.MainAxisAlignment.CENTER)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        )
        page.update()

    def on_start_pyxel(e):
        nonlocal pyxel_proc
        if pyxel_proc is None or pyxel_proc.poll() is not None:
            # 開発時
            pyxel_proc = subprocess.Popen([sys.executable, __file__, "run_pyxel"])

            # ビルド時
            # pyxel_proc = subprocess.Popen([sys.executable, "run_pyxel"])

    # 初期画面表示
    show_initial_screen()

# --- プログラムのエントリーポイント ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run_pyxel":
        pyxel_app.run_pyxel_app() 
    else:
        ft.app(target=main)