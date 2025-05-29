import pyxel

# ボタンの描画
# x, y: ボタンの左上の座標
# width, height: ボタンの幅と高さ
# rect_color: ボタンの背景色
# text_color: ボタンのテキスト色
# text: ボタンのテキスト
# font_size: ボタンのテキストのフォントサイズ
# writer: テキストの描画に使用するWriterインスタンス
def draw_button(x, y, width, height, rect_color, text_color, text, font_size, writer):
    # ボタンの背景を描画
    pyxel.rect(x, y, width, height, rect_color)

    # テキストの中央揃え
    text_x = x + (width - len(text) * font_size) / 2
    text_y = y + (height - font_size) / 2

    # テキストを描画
    writer.draw(text_x, text_y, text, font_size, text_color)  # 0はテキストの色（黒）を示す