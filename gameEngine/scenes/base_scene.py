# scenes/base_scene.py
class BaseScene:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.screen_width = scene_manager.screen_width
        self.screen_height = scene_manager.screen_height
        # 必要に応じて、フォントライターなどの共有リソースを scene_manager から受け取る
        self.writer_menu = scene_manager.writer_menu
        self.writer_play = scene_manager.writer_play
        self.font_point_size = scene_manager.font_point_size
        self.text_color_original = scene_manager.text_color_original


    def update(self):
        """
        シーンのロジックを更新します。
        シーン遷移が必要な場合は、self.scene_manager.change_scene('next_scene_name') を呼び出します。
        """
        raise NotImplementedError

    def draw(self):
        """
        シーンを描画します。
        """
        raise NotImplementedError

    def on_enter(self, previous_scene_name=None, **kwargs):
        """
        このシーンがアクティブになったときに呼び出されます。
        オプションで前のシーン名や追加の引数を受け取れます。
        """
        pass # 必要に応じてオーバーライド

    def on_exit(self, next_scene_name=None):
        """
        このシーンが非アクティブになる直前に呼び出されます。
        オプションで次のシーン名を受け取れます。
        """
        pass # 必要に応じてオーバーライド