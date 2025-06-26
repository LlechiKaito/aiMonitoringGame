import flet as ft

class Canvas:
    def __init__(self, size=16, pixel_size=20):
        self.size = size
        self.pixel_size = pixel_size
        self.data = [["#FFFFFF" for _ in range(size)] for _ in range(size)]
        self.history = []
        self.is_dragging = False
        self.current_color = "#000000"
        self.grid = None
        self.page = None
        
    def set_page(self, page):
        self.page = page
        
    def set_current_color(self, color):
        self.current_color = color
        
    def create_pixel(self, row, col):
        """ピクセル描画用のコンテナを生成"""
        def on_pixel_click(e):
            if not self.is_dragging:
                self.history.append([r[:] for r in self.data]) 
            
            self.data[row][col] = self.current_color
            
            # UIコンテナの色も直接更新
            self.grid.controls[row].controls[col].content.bgcolor = self.current_color
            
            if self.page:
                self.page.update()

        return ft.GestureDetector(
            content=ft.Container(
                width=self.pixel_size,
                height=self.pixel_size,
                bgcolor=self.data[row][col],
                border=ft.border.all(0.5, ft.Colors.BLACK26),
            ),
            on_tap=on_pixel_click,
        )

    def create_grid(self):
        """キャンバスのグリッドを作成"""
        self.grid = ft.Column(
            [
                ft.Row(
                    [self.create_pixel(r, c) for c in range(self.size)],
                    spacing=0,
                )
                for r in range(self.size)
            ],
            spacing=0,
        )
        return self.grid

    def on_canvas_pan_start(self, e):
        """キャンバスドラッグ開始処理"""
        self.is_dragging = True
        self.history.append([r[:] for r in self.data])

    def on_canvas_pan_update(self, e):
        """キャンバスドラッグ更新処理"""
        if self.is_dragging:
            # ドラッグ位置からピクセル座標を計算
            local_x = e.local_x
            local_y = e.local_y
            
            col = int(local_x // self.pixel_size)
            row = int(local_y // self.pixel_size)
            
            # 範囲チェック
            if 0 <= row < self.size and 0 <= col < self.size:
                self.data[row][col] = self.current_color
                self.grid.controls[row].controls[col].content.bgcolor = self.current_color
                if self.page:
                    self.page.update()

    def on_canvas_pan_end(self, e):
        """キャンバスドラッグ終了処理"""
        self.is_dragging = False

    def create_canvas_with_drag(self):
        """ドラッグ機能付きキャンバスを作成"""
        grid = self.create_grid()
        return ft.GestureDetector(
            content=grid,
            on_pan_start=self.on_canvas_pan_start,
            on_pan_update=self.on_canvas_pan_update,
            on_pan_end=self.on_canvas_pan_end,
        )

    def undo(self):
        """Undo機能"""
        if self.history:
            self.data = self.history.pop()
            
            for r in range(self.size):
                for c in range(self.size):
                    self.grid.controls[r].controls[c].content.bgcolor = self.data[r][c]
            
            if self.page:
                self.page.update()

    def export_to_python_file(self, file_path):
        """キャンバスデータをPythonファイルとして出力"""
        with open(file_path, "w") as f:
            f.write("import pyxel\n\n")
            f.write("image_data = [\n")
            for row in self.data:
                rgb_row = []
                for hex_color in row:
                    hex_color = hex_color.lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    rgb_row.append(rgb)
                f.write(f"    {rgb_row},\n")
            f.write("]\n")
