import pyxel
from .base_scene import BaseScene

class ChatScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)        
        self.chat_area_width = 192
        self.chat_area_height = 104
        self.chat_area_color = 1
        self.y_padding = 4
        self.x_padding = 5

        self.chat_input_area_width = 192
        self.chat_input_area_height = 16
        self.chat_input_area_color = 1
        self.chat_input_area_text_color = 7
        self.chat_input_area_text_size = 8
        self.chat_input_area_x_padding = 5
        self.chat_input_area_y_padding = 5
        self.chat_input_bottom_margin = 10

        self.input_text = ""
        self.chat_text = []

        # スライドバーの設定
        self.scroll_bar_width = 5
        self.scroll_bar_color = 7

        # テキストの高さを考慮
        self.text_size = 8
        self.text_color = 7
        
        # チャットテキストの表示開始インデックスを計算
        self.max_visible_lines = (self.chat_area_height - self.y_padding * 2) // self.text_size
        self.start_index = max(0, len(self.chat_text) - self.max_visible_lines)

    def update(self):
        # キー入力を処理して入力文字列を更新
        for key in range(pyxel.KEY_A, pyxel.KEY_Z + 1):
            if pyxel.btnp(key):
                self.input_text += chr(key)
                # バックスペースキーで文字を削除
        if pyxel.btnp(pyxel.KEY_BACKSPACE) and len(self.input_text) > 0:
            self.input_text = self.input_text[:-1]
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.chat_text.append(self.input_text)
            self.input_text = ""
            if len(self.chat_text) > self.max_visible_lines:
                self.scroll_offset = min(
                    len(self.chat_text) - self.max_visible_lines, self.scroll_offset + 1)

        # スクロールオフセットを保持するための変数
        if not hasattr(self, 'scroll_offset'):
            self.scroll_offset = 0
        if pyxel.btnp(pyxel.KEY_UP):
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.scroll_offset = min(
                len(self.chat_text) - self.max_visible_lines, self.scroll_offset + 1)

    def draw(self):
        pyxel.cls(0)

        start_x = (self.screen_width - self.chat_area_width) // 2
        start_y = (self.screen_height - self.chat_area_height) // 5
        pyxel.rect(start_x, start_y, self.chat_area_width,
                   self.chat_area_height, self.chat_area_color)

        # スクロールオフセットを考慮してテキストを描画
        for i, text in enumerate(self.chat_text[self.scroll_offset:self.scroll_offset + self.max_visible_lines]):
            pyxel.text(start_x + self.x_padding, start_y + self.y_padding + (i * self.text_size), text, self.text_color)

        # スライドバーの描画
        scroll_bar_x = start_x + self.chat_area_width - self.scroll_bar_width
        scroll_bar_y = start_y
        scroll_bar_height = self.chat_area_height
        pyxel.rect(scroll_bar_x, scroll_bar_y, self.scroll_bar_width,
                   scroll_bar_height, self.scroll_bar_color)

        # スクロール位置のインジケーター
        if len(self.chat_text) > self.max_visible_lines:
            indicator_height = max(
                10, scroll_bar_height * self.max_visible_lines // len(self.chat_text))
            indicator_y = scroll_bar_y + (scroll_bar_height - indicator_height) * \
                self.scroll_offset // (len(self.chat_text) - self.max_visible_lines)
            pyxel.rect(scroll_bar_x, indicator_y,
                       self.scroll_bar_width, indicator_height, self.scroll_bar_color)

        input_start_x = (self.screen_width - self.chat_input_area_width) // 2
        input_start_y = (self.screen_height - self.chat_input_area_height) - self.chat_input_bottom_margin
        pyxel.rect(input_start_x, input_start_y, self.chat_input_area_width,
                   self.chat_input_area_height, self.chat_input_area_color)
        pyxel.text(input_start_x + self.chat_input_area_x_padding, input_start_y + self.chat_input_area_y_padding, ">", self.chat_input_area_text_color)  # 入力プロンプトを表示

        # 入力された文字列を表示
        pyxel.text(input_start_x + self.chat_input_area_x_padding, input_start_y + self.chat_input_area_y_padding, self.input_text, self.chat_input_area_text_color)
