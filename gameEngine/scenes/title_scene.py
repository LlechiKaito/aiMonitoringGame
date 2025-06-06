# scenes/title_scene.py
import pyxel
from .base_scene import BaseScene
from gameEngine.utils.custom_button import Button

class TitleScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.title_text = "My Pyxel Game"
        self.prompt_text = "Press ENTER to Start"
        self.blink_timer = 0

        pyxel.mouse(True)

    def update(self):
        self.blink_timer = (self.blink_timer + 1) % 60 # 1秒周期で点滅

        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_KP_ENTER):
            self.scene_manager.change_scene('game') # 'game' はGameSceneを登録する際のキー名
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()


    def draw(self):
        pyxel.cls(7) # 明るい背景色

        title_x = (self.screen_width - len(self.title_text) * pyxel.FONT_WIDTH) // 2
        pyxel.text(title_x, self.screen_height // 3, self.title_text, 0) # Pyxel標準フォントで表示

        # PyxelUniversalFont を使う場合
        # if self.writer_play:
        #     title_w = self.writer_play.measure_text(self.title_text, self.font_point_size * 2) # 例:大きめフォント
        #     self.writer_play.draw(
        #         (self.screen_width - title_w) // 2,
        #         self.screen_height // 3,
        #         self.title_text,
        #         self.font_point_size * 2, # 例:大きめフォント
        #         0 # 黒色
        #     )

        if self.blink_timer < 30: # 点滅表現
            # prompt_x = (self.screen_width - len(self.prompt_text) * pyxel.FONT_WIDTH) // 2
            # pyxel.text(prompt_x, self.screen_height * 2 // 3, self.prompt_text, 0)

            # 一旦追加
            button_font_size = 8
            button_x = (self.screen_width - len(self.prompt_text) * button_font_size) // 2
            button_y = self.screen_height * 2 // 3
            button_width = len(self.prompt_text) * button_font_size
            button_height = pyxel.FONT_HEIGHT
            button_content = self.prompt_text
            button_color_default = 7
            button_color_hover = 7
            button_color_pressed = 7
            button_text_color = 0
            content_padding_x = 40

            button = Button(
                x=button_x,
                y=button_y,
                width=button_width,
                height=button_height,
                content=button_content,
                color_default=button_color_default,
                color_hover=button_color_hover,
                color_pressed=button_color_pressed,
                callback=lambda: self.scene_manager.change_scene('game'),
                text_color=button_text_color,
                font_size=button_font_size,
                content_padding_x=content_padding_x,
                is_pressed=True
            )
            button.update()
            button.draw()
            # if self.writer_play:
            #     prompt_w = self.writer_play.measure_text(self.prompt_text, self.font_point_size)
            #     self.writer_play.draw(
            #         (self.screen_width - prompt_w) // 2,
            #         self.screen_height * 2 // 3,
            #         self.prompt_text,
            #         self.font_point_size,
            #         0 # 黒色
            #     )

    def on_enter(self, previous_scene_name=None, **kwargs):
        print(f"Entered TitleScene from {previous_scene_name}")
        self.blink_timer = 0

    def on_exit(self, next_scene_name=None):
        print(f"Exiting TitleScene to {next_scene_name}")