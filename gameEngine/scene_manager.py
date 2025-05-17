# scene_manager.py
import pyxel # pyxel.quit() のためにインポート

class SceneManager:
    def __init__(self, screen_width, screen_height, title, fps, font_path):
        self.screen_width = screen_width
        self.screen_height = screen_height
        #self.font_path = font_path # 外部フォントを使用する場合は、ここで指定
        self.font_path = "misaki_gothic.ttf"

        pyxel.init(self.screen_width, self.screen_height, title=title, fps=fps)

        # 共有リソース (フォントライターなど)
        # PyxelUniversalFont のインポートは main.py かここで行う
        from PyxelUniversalFont import Writer
        try:
            self.writer_play = Writer(self.font_path)
            self.writer_menu = Writer(self.font_path) # 必要に応じて別のフォントも指定可能
        except Exception as e:
            print(f"フォントの読み込みに失敗しました: {e}")
            print(f"{self.font_path} が正しいパスにあるか確認してください。")
            # フォールバックやエラー処理
            self.writer_play = None
            self.writer_menu = None

        self.font_point_size = 8 # アプリケーション全体で共有するフォントサイズ
        self.text_color_original = 8 # アプリケーション全体で共有するテキストカラー

        self._scenes = {}
        self._current_scene_name = None
        self._current_scene = None
        self._next_scene_name = None
        self._scene_args = {} # シーン遷移時に渡す引数

    def add_scene(self, name, scene_class):
        """シーンクラスを登録します。インスタンス化はchange_sceneで行います。"""
        if name in self._scenes:
            print(f"Warning: Scene with name '{name}' already exists. Overwriting.")
        self._scenes[name] = scene_class

    def change_scene(self, name, **kwargs):
        """指定された名前のシーンに遷移します。kwargsは次のシーンのon_enterに渡されます。"""
        if name not in self._scenes:
            print(f"Error: Scene with name '{name}' not found.")
            return
        self._next_scene_name = name
        self._scene_args = kwargs # 次のシーンに渡す引数を保存

    def _perform_scene_change(self):
        if self._next_scene_name:
            previous_scene_name = self._current_scene_name
            if self._current_scene:
                self._current_scene.on_exit(next_scene_name=self._next_scene_name)

            self._current_scene_name = self._next_scene_name
            scene_class = self._scenes[self._current_scene_name]
            self._current_scene = scene_class(self) # シーンをインスタンス化し、自身を渡す
            self._current_scene.on_enter(previous_scene_name=previous_scene_name, **self._scene_args)

            self._next_scene_name = None
            self._scene_args = {}


    def update(self):
        self._perform_scene_change() # フレームの最初にシーン遷移処理
        if self._current_scene:
            self._current_scene.update()

    def draw(self):
        if self._current_scene:
            self._current_scene.draw()

    def run(self):
        pyxel.run(self.update, self.draw)

    def quit_application(self):
        pyxel.quit()