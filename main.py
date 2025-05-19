# main.py
import os
import pyxel # SceneManager内でinitされますが、実行時エラー回避のため念のため
from gameEngine.scene_manager import SceneManager
from gameEngine.scenes.title_scene import TitleScene
from gameEngine.scenes.game_scene import GameScene
from gameEngine.scenes.menu_scene import MenuScene
# PyxelUniversalFont の Writer は SceneManager 内で import されます

# --- アプリケーション設定 ---
SCREEN_WIDTH = 192 + 64
SCREEN_HEIGHT = 144
APP_TITLE = "My Game with Scenes"
FPS = 30

# フォントファイルのパス (assetsフォルダ内を想定、main.pyからの相対パス)
FONT_FILENAME = "misaki_gothic.ttf"
# スクリプト(main.py)があるディレクトリを基準にフォントパスを解決
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONT_PATH = os.path.join(ASSETS_DIR, FONT_FILENAME)

exit_flag = False

#外部フォント利用時
#if not os.path.exists(FONT_PATH):
#    print(f"警告: フォントファイルが見つかりません: {FONT_PATH}")
#    print(f"{FONT_FILENAME} を {ASSETS_DIR} フォルダに配置するか、パスを正しく設定してください。")
#    # pyxel.quit() や exit() で終了させることも検討
#    # この時点ではpyxel.initが呼ばれていないのでpyxel.quitは使えない
#    # exit_flag = True # 実行前にフラグで管理
#else:
#    exit_flag = False


class MainApp:
    def __init__(self):
        if exit_flag: # フォントがない場合は初期化しない
            print("フォントファイルが見つからないため、アプリケーションを起動できません。")
            return

        self.scene_manager = SceneManager(
            SCREEN_WIDTH, SCREEN_HEIGHT, APP_TITLE, FPS, FONT_PATH
        )

        # シーンの登録
        self.scene_manager.add_scene('title', TitleScene)
        self.scene_manager.add_scene('game', GameScene)
        self.scene_manager.add_scene('menu', MenuScene)
        # 他のシーンも同様に追加

        # 初期シーンの設定
        self.scene_manager.change_scene('title')

    def run(self):
        if exit_flag:
            return
        self.scene_manager.run()

if __name__ == '__main__':
    app = MainApp()
    app.run()