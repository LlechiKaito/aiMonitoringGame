import pyxel
from .base_scene import BaseScene
from PyxelUniversalFont import Writer

class MenuScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)

        self.font_path = "misaki_gothic.ttf"
        self.writer = Writer(self.font_path)
        self.width = pyxel.width
        self.height = pyxel.height
        self.font_size = 8
        self.text_color = 2
        
        self.menu_area_width = 64
        self.menu_area_height = 144
        self.menu_area_color = 1

        self.menu_main_area_width = 64
        self.menu_main_area_height = 96
        self.menu_main_area_color = 7

        self.menu_main_area_x_start = self.width - self.menu_area_width
        self.menu_main_area_y_start = 0

        self.title_text = "オブジェクト名"
        self.menu_title_text_x_start = self.width - self.menu_area_width
        self.menu_title_text_y_start = 2

        # ここは文章が長くなるので、フォントサイズを検討してから、中央揃えにする
        self.main_text = "説明文(詳細)"
        self.menu_main_text_x_start = self.width - self.menu_area_width
        self.menu_main_text_y_start = 44

        self.button_text = [
            "操作",
            "会話",
            "編集"
        ]
        self.menu_button_text_x_start = self.width - self.menu_area_width
        self.menu_button_text_y_start = 86
        self.menu_button_text_color = 2
        self.menu_button_text_font_size = 8
        self.menu_button_text_x_space = 24

    def update(self):
        if pyxel.btnp(pyxel.KEY_W):
            self.scene_manager.change_scene('game')  # 'game' シーンに遷移
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        
        # 背景の配置
        pyxel.rect(self.menu_main_area_x_start, self.menu_main_area_y_start, self.menu_area_width, self.menu_area_height, self.menu_area_color)
        pyxel.rect(self.menu_main_area_x_start, self.menu_main_area_y_start, self.menu_area_width, self.menu_main_area_height, self.menu_main_area_color)
        
        # textの配置
        self.writer.draw(self.menu_title_text_x_start, self.menu_title_text_y_start, self.title_text, self.font_size, self.text_color)
        self.writer.draw(self.menu_main_text_x_start, self.menu_main_text_y_start, self.main_text, self.font_size, self.text_color)

        # ボタンの配置
        for i, text in enumerate(self.button_text):
            self.writer.draw(self.menu_button_text_x_start + i * self.menu_button_text_x_space, self.menu_button_text_y_start, text, self.font_size, self.text_color)
