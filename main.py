import flet as ft
import sys
import os
import subprocess
import socket
import gameEngine.pyxel_app as pyxel_app  # 作成したPyxelモジュールをインポート
from objects.object_list import object_list
from chat.chat_main import chat_main
from createNPC.createNPC_main import createNPC_main

def main(page: ft.Page):
    # --- ページ基本設定 ---
    page.title = "Flet仮想デスクトップ"
    page.window_width = 400
    page.window_height = 300
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    pyxel_proc = None  # Pyxelプロセス管理用

    # --- 画面遷移用関数 ---
    def show_initial_screen(e=None):
        """
        アプリ起動時の初期画面を表示する関数。
        各機能へのボタンを配置。
        """
        page.controls.clear()
        pyxel_btn = ft.ElevatedButton("Pyxel起動", on_click=on_start_pyxel)
        list_btn = ft.ElevatedButton("リスト", on_click=lambda e: object_list(page, show_initial_screen))
        sample2_btn = ft.ElevatedButton("チャット", on_click=lambda e: chat_main(page, show_initial_screen))
        create_npc_btn = ft.ElevatedButton("NPC作成", on_click=lambda e: createNPC_main(page, show_initial_screen))
        page.add(
            ft.Column(
                [pyxel_btn, list_btn, sample2_btn, create_npc_btn],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        )
        page.update()

    def on_start_pyxel(e):
        """
        Pyxelアプリをサブプロセスとして起動する関数。
        既に起動済みの場合は新たに起動しない。
        """
        nonlocal pyxel_proc
        if pyxel_proc is None or pyxel_proc.poll() is not None:
            # 開発時: 現在のスクリプトをrun_pyxel引数付きで起動
            pyxel_proc = subprocess.Popen([sys.executable, __file__, "run_pyxel"])

            # ビルド時: 必要に応じてパスを修正
            # pyxel_proc = subprocess.Popen([sys.executable, "run_pyxel"])

    # 初期画面表示
    show_initial_screen()

# --- プログラムのエントリーポイント ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run_pyxel":
        # Pyxelアプリ起動
        pyxel_app.run_pyxel_app() 
    else:
        # Fletアプリ起動
        ft.app(target=main)