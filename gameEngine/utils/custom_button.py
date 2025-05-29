import pyxel

class Button:
    def __init__(self, x, y, width, height,
                 content,
                 color_default, color_hover, color_pressed,
                 callback=None,
                 text_color=7, # デフォルト: 白
                 content_padding_x=0,
                 content_padding_y=0,
                 is_outlined=False, # 枠線のみ表示するかどうかのフラグ
                 ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.content = content
        self.color_default = color_default
        self.color_hover = color_hover
        self.color_pressed = color_pressed
        self.callback = callback
        self.text_color = text_color
        self.content_padding_x = content_padding_x
        self.content_padding_y = content_padding_y
        self.is_outlined = is_outlined # 枠線フラグを保存

        self.is_hover = False
        self.is_pressed = False
        self.current_color = color_default

        self.is_icon = isinstance(self.content, tuple)

    def update(self):
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y

        self.is_hover = (self.x <= mouse_x < self.x + self.width and
                         self.y <= mouse_y < self.y + self.height)

        if self.is_hover:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.is_pressed = True
            elif pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) and self.is_pressed:
                self.is_pressed = False
                if self.callback:
                    self.callback()
        else:
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) and self.is_pressed:
                 self.is_pressed = False
            elif not self.is_hover:
                 self.is_pressed = False

        if self.is_pressed and self.is_hover:
            self.current_color = self.color_pressed
        elif self.is_hover:
            self.current_color = self.color_hover
        else:
            self.current_color = self.color_default

    def draw(self):
        # ボタンの背景または枠線を描画
        if self.is_outlined:
            pyxel.rectb(self.x, self.y, self.width, self.height, self.current_color)
        else:
            pyxel.rect(self.x, self.y, self.width, self.height, self.current_color)

        # コンテンツの描画 (テキストまたはアイコン)
        if self.is_icon:
            img_idx, u, v, w, h, *colkey_tuple = self.content
            colkey = colkey_tuple[0] if colkey_tuple else None

            icon_x = self.x + (self.width - w) / 2 + self.content_padding_x
            icon_y = self.y + (self.height - h) / 2 + self.content_padding_y
            if colkey is not None:
                pyxel.blt(icon_x, icon_y, img_idx, u, v, w, h, colkey)
            else:
                pyxel.blt(icon_x, icon_y, img_idx, u, v, w, h)
        else:
            text_content = str(self.content)
            text_width = len(text_content) * pyxel.FONT_WIDTH
            text_height = pyxel.FONT_HEIGHT

            text_x = self.x + (self.width - text_width) / 2 + self.content_padding_x
            text_y = self.y + (self.height - text_height) / 2 + self.content_padding_y
            pyxel.text(text_x, text_y, text_content, self.text_color)

# --- (Pyxel標準カラーパレットとsetup_image_bankは変更なしなので省略) ---
# ... (前回のコードのカラーパレット定義とsetup_image_bank関数をここにコピーしてください) ...
# --- Pyxel標準カラーパレット (参考) ---
# 0: 黒 (Black)
# 1: 濃い青 (Navy)
# 2: 濃い紫 (Purple)
# 3: 濃い緑 (Green)
# 4: 茶色 (Brown)
# 5: 暗い灰色 (Dark Gray)
# 6: 明るい灰色 (Light Gray)
# 7: 白 (White)
# 8: 赤 (Red)
# 9: オレンジ (Orange)
# 10: 黄色 (Yellow)
# 11: 明るい緑 (Lime)
# 12: 水色 (Cyan / Light Blue)
# 13: 薄い水色 (Pale Cyan / Light Cyan)
# 14: ピンク (Pink)
# 15: 薄いピンク (Peach / Light Pink)

def setup_image_bank():
    # イメージバンク0 (pyxel.images[0]) にアイコンを描画
    # ハート (赤: 8)
    pyxel.images[0].set(0, 0, [
        "00880880",
        "08778778", # 白(7)も使用
        "87777778",
        "87777778",
        "08777780",
        "00877800",
        "00088000",
        "00000000",
    ])
    # 星 (黄色: 10)
    pyxel.images[0].set(8, 0, [
        "000a0000",
        "00aaa000",
        "0aaaaa00",
        "aaaaaaaa",
        "0aaaaa00",
        "00aaa000",
        "000a0000",
        "00000000",
    ])
    # 矢印アイコン (白: 7) - 8x8
    pyxel.images[0].set(0, 8, [
        "00700700",
        "07707700",
        "77777770",
        "00700700",
        "00700700",
        "00700700",
        "00700700",
        "00000000",
    ])

class App:
    def __init__(self):
        pyxel.init(200, 220, title="Button Outline Example") # 少し高さを増やす
        setup_image_bank()

        # 色の定義 (0-15の整数値)
        NAVY = 1; BLUE = 12; LIGHT_BLUE = 13; RED = 8; PINK = 14; PEACH = 15
        ORANGE = 9; YELLOW = 10; LIME = 11; GRAY = 6; LIGHT_GRAY = 5; WHITE = 7; BLACK = 0
        DARK_GREEN = 3; PALE_GREEN = 11; BRIGHT_GREEN = 11 # 例として追加

        # --- 通常のボタン ---
        self.text_button = Button(
            x=20, y=20, width=60, height=20, content="START",
            color_default=NAVY, color_hover=BLUE, color_pressed=LIGHT_BLUE,
            callback=lambda: self.update_message("START clicked!"), text_color=WHITE
        )
        self.icon_button_heart = Button(
            x=100, y=20, width=24, height=24, content=(0, 0, 0, 8, 8, BLACK),
            color_default=RED, color_hover=PINK, color_pressed=PEACH,
            callback=lambda: self.update_message("Heart clicked!")
        )

        # --- 枠線のみのボタン ---
        self.outlined_text_button = Button(
            x=20, y=60, width=70, height=20, content="CANCEL",
            color_default=WHITE, color_hover=YELLOW, color_pressed=ORANGE, # 枠線の色が変わる
            callback=lambda: self.update_message("CANCEL clicked!"),
            text_color=WHITE, # 文字色は別途指定
            is_outlined=True # 枠線オプションをTrueに
        )
        self.outlined_icon_button = Button(
            x=110, y=60, width=24, height=24, content=(0, 8, 0, 8, 8, BLACK), # 星アイコン
            color_default=LIME, color_hover=YELLOW, color_pressed=WHITE, # 枠線の色
            callback=lambda: self.update_message("Outlined Star clicked!"),
            is_outlined=True
        )

        # 枠線ボタン (コンテンツなし、ただの枠)
        self.simple_outlined_button = Button(
            x=20, y=100, width=50, height=30, content="", # コンテンツなし
            color_default=GRAY, color_hover=LIGHT_GRAY, color_pressed=WHITE,
            is_outlined=True,
            callback=lambda: self.update_message("Simple Outlined Box clicked!")
        )

        # 枠線ボタン (色固定、文字だけ)
        self.fixed_color_outlined_text_button = Button(
            x=90, y=100, width=80, height=20, content="INFO",
            color_default=DARK_GREEN, color_hover=DARK_GREEN, color_pressed=DARK_GREEN, # 色を固定
            callback=lambda: self.update_message("INFO clicked!"),
            text_color=PALE_GREEN, # 文字色は枠線と変えることも可能
            is_outlined=True
        )


        self.message = "Click a button"
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update_message(self, msg):
        self.message = msg
        print(msg)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.text_button.update()
        self.icon_button_heart.update()
        self.outlined_text_button.update()
        self.outlined_icon_button.update()
        self.simple_outlined_button.update()
        self.fixed_color_outlined_text_button.update()

    def draw(self):
        pyxel.cls(1) # 背景色: 濃い青

        self.text_button.draw()
        self.icon_button_heart.draw()
        self.outlined_text_button.draw()
        self.outlined_icon_button.draw()
        self.simple_outlined_button.draw()
        self.fixed_color_outlined_text_button.draw()

        pyxel.text(10, 180, self.message, 7)
        pyxel.text(10, 190, f"Mouse:({pyxel.mouse_x},{pyxel.mouse_y})", 10)
        # pyxel.text(10, 200, f"OutlinedHover:{self.outlined_text_button.is_hover}", 10)


# App()