import pyxel
from .base_scene import BaseScene
from PyxelUniversalFont import Writer
from gameEngine.utils.draw_button import draw_button

class EditScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.font_path = "misaki_gothic.ttf"
        self.explainfont_size = 15  # フォントサイズを指定
        self.button_font_size = 8  # フォントサイズを指定
        self.play_area_width = 256
        self.play_area_height = 144
        self.play_area_color = 1

        self.cancel_button_x_start = 160
        self.cancel_button_y_start = 130
        self.cancel_button_width = 40
        self.cancel_button_height = 10
        self.cancel_button_text_color = 10
        self.cancel_button_color = 2

        self.set_button_x_start = 210
        self.set_button_y_start = 130
        self.set_button_width = 40
        self.set_button_height = 10
        self.set_button_text_color = 10
        self.set_button_color = 2

        self.cross_button_x_start = self.play_area_width - 15
        self.cross_button_y_start = 5
        self.cross_button_width = 10
        self.cross_button_height = 10
        self.cross_button_text_color = 10
        self.cross_button_color = 2

        self.writer = Writer(self.font_path)
        self.text_color = 10
        self.original_text = "元説明文"
        self.new_text = "新説明文"
        self.cancel_text = "キャンセル"
        self.set_text = "設定"
        self.cross_text = "X"

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        # ここも一旦ゲームシーンに移行するようにしておく
        if pyxel.btnp(pyxel.KEY_G):
            self.scene_manager.change_scene("game_scene")

    def draw(self):
        pyxel.cls(0)
        
        pyxel.rect(0, 0, self.play_area_width, self.play_area_height, self.play_area_color)

        # 元説明文（横方向の中央揃えと上から見て3分の1の位置）
        original_text_x = (self.play_area_width - (self.explainfont_size * len(self.original_text))) // 2
        original_text_y = (self.play_area_height - self.explainfont_size) / 3
        self.writer.draw(original_text_x, original_text_y, self.original_text, self.explainfont_size, self.text_color)

        # 新説明文（横方向の中央揃えと上から見て3分の2の位置）
        new_text_x = (self.play_area_width - (self.explainfont_size * len(self.new_text))) // 2
        new_text_y = (self.play_area_height - self.explainfont_size) / 3 * 2
        self.writer.draw(new_text_x, new_text_y, self.new_text, self.explainfont_size, self.text_color)
        
        # ボタンの描画
        draw_button(self.cancel_button_x_start, self.cancel_button_y_start, self.cancel_button_width, self.cancel_button_height, self.cancel_button_color, self.text_color, self.cancel_text, self.button_font_size, self.writer)
        draw_button(self.set_button_x_start, self.set_button_y_start, self.set_button_width, self.set_button_height, self.set_button_color, self.text_color, self.set_text, self.button_font_size, self.writer)

        # クロスボタンの描画
        draw_button(self.cross_button_x_start, self.cross_button_y_start, self.cross_button_width, self.cross_button_height, self.cross_button_color, self.text_color, self.cross_text, self.button_font_size, self.writer)

        