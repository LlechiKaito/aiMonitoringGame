# このファイルはPyxel関連の機能だけを持つモジュール

import pyxel
import socket
import threading
from player import Player  # 追加

def run_pyxel_app():
    """Pyxelアプリケーションを初期化し、実行するメイン関数"""
    
    received_message = ""

    def udp_listener():
        nonlocal received_message
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind(("127.0.0.1", 50007))
            while True:
                data, _ = sock.recvfrom(1024)
                try:
                    received_message = data.decode("utf-8")
                except UnicodeDecodeError:
                    received_message = "<decode error>"
        except Exception as e:
            print(f"UDP Error: {e}")
        finally:
            sock.close()

    class App:
        def __init__(self):
            pyxel.init(200, 100, title="Pyxel受信画面")
            pyxel.load("sample.pyxres")  # 追加: 背景リソースを読み込む
            self.message = ""
            self.player = Player()  # プレイヤー生成
            threading.Thread(target=udp_listener, daemon=True).start()
            pyxel.run(self.update, self.draw)

        def update(self):
            nonlocal received_message
            self.message = received_message
            self.player.update()  # プレイヤーの移動処理

        def draw(self):
            pyxel.cls(0)
            # 追加: マップ(背景)を描画
            pyxel.bltm(0, 0, 0, 0, 0, pyxel.width, pyxel.height)
            msg = self.message
            x = max(0, (200 - pyxel.FONT_WIDTH * len(msg)) // 2)
            y = 45
            pyxel.text(x, y, msg, 7)
            self.player.draw()  # プレイヤーの描画

    # この関数が呼ばれたら、Appクラスをインスタンス化して実行
    App()