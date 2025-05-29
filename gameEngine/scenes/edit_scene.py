import pyxel
from .base_scene import BaseScene
from PyxelUniversalFont import Writer
from gameEngine.utils.custom_button import Button

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
            self.scene_manager.change_scene("game")

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
        
        # ボタンの描画(文字表示されていないのとマウスカーソルでの移動になっていないため適用させる)
        self.cancel_button = Button(
            x=self.cancel_button_x_start, 
            y=self.cancel_button_y_start, 
            width=self.cancel_button_width, 
            height=self.cancel_button_height, 
            content=self.cancel_text, 
            color_default=self.cancel_button_color, 
            color_hover=self.cancel_button_color, 
            color_pressed=self.cancel_button_color
        )
        self.cancel_button.update()
        self.cancel_button.draw()

        self.set_button = Button(
            x=self.set_button_x_start, 
            y=self.set_button_y_start, 
            width=self.set_button_width, 
            height=self.set_button_height, 
            content=self.set_text, 
            color_default=self.set_button_color, 
            color_hover=self.set_button_color, 
            color_pressed=self.set_button_color
        )
        self.set_button.update()
        self.set_button.draw()

        # クロスボタンの描画
        self.cross_button = Button(
            x=self.cross_button_x_start, 
            y=self.cross_button_y_start, 
            width=self.cross_button_width, 
            height=self.cross_button_height, 
            content=self.cross_text, 
            color_default=self.cross_button_color, 
            color_hover=self.cross_button_color, 
            color_pressed=self.cross_button_color
        )
        self.cross_button.update()
        self.cross_button.draw()