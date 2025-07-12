import flet as ft

class ColorPalette:
    def __init__(self, colors=None):
        if colors is None:
            self.colors = ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF"]
        else:
            self.colors = colors
        
        self.current_color = self.colors[0]
        self.color_blocks = []
        self.selected_color_block = None
        self.page = None
        self.color_change_callback = None
        
    def set_page(self, page):
        self.page = page
        
    def set_color_change_callback(self, callback):
        """色変更時に呼び出されるコールバック関数を設定"""
        self.color_change_callback = callback
        
    def create_color_palette(self):
        """カラーパレットのUIを作成"""
        self.color_blocks = []
        
        # 各カラーブロックを生成
        for color in self.colors:
            color_container = ft.Container(
                width=30,
                height=30,
                bgcolor=color,
                border_radius=ft.border_radius.all(5),
                border=ft.border.all(1, ft.Colors.BLACK),
            )
            self.color_blocks.append(color_container)
        
        # カラーパレットのRowを作成
        color_palette = ft.Row(
            [
                ft.GestureDetector(
                    content=color_block,
                    on_tap=lambda e, color=color_block.bgcolor, block=color_block: self.set_current_color(color, block),
                )
                for color_block in self.color_blocks
            ],
            spacing=10,
        )
        
        # 初期選択色をセット
        if self.color_blocks:
            self.set_current_color(self.colors[0], self.color_blocks[0])
        
        return color_palette

    def set_current_color(self, color, new_selected_block):
        """現在の選択色を設定"""
        # 以前選択されていたブロックのボーダーをリセット
        if self.selected_color_block is not None:
            self.selected_color_block.border = ft.border.all(1, ft.Colors.BLACK)
            
        # 新しい選択色を設定
        self.current_color = color
        
        # 新しく選択されたブロックに目立つボーダーを設定
        new_selected_block.border = ft.border.all(3, ft.Colors.BLUE_ACCENT_700)
        
        # 選択中のブロックを更新
        self.selected_color_block = new_selected_block
        
        # コールバック関数を呼び出し
        if self.color_change_callback:
            self.color_change_callback(color)
        
        if self.page:
            self.page.update()

    def get_current_color(self):
        """現在選択中の色を取得"""
        return self.current_color
