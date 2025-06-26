import flet as ft

def main(page: ft.Page):
    page.title = "ドット絵エディター"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    canvas_size = 16
    pixel_size = 20
    canvas_data = [["#FFFFFF" for _ in range(canvas_size)] for _ in range(canvas_size)]
    history = []
    
    # 初期選択色を黒にする
    current_color = "#000000" 
    
    # ドラッグ状態管理
    is_dragging = False

    # カラーブロックを管理するためのリストを定義
    color_blocks = []
    
    # 選択中のカラーブロックを追跡するための変数
    selected_color_block = None

    # ピクセル描画用のコンテナを生成する関数 (修正)
    def create_pixel(row, col):
        def on_pixel_click(e):
            nonlocal canvas_data, history, is_dragging
            
            if not is_dragging:
                history.append([r[:] for r in canvas_data]) 
            
            canvas_data[row][col] = current_color
            
            # UIコンテナの色も直接更新
            canvas_grid.controls[row].controls[col].content.bgcolor = current_color
            
            page.update()

        return ft.GestureDetector(
            content=ft.Container(
                width=pixel_size,
                height=pixel_size,
                bgcolor=canvas_data[row][col],
                border=ft.border.all(0.5, ft.Colors.BLACK26),
            ),
            on_tap=on_pixel_click,
        )

    # キャンバスのグリッドを作成
    canvas_grid = ft.Column(
        [
            ft.Row(
                [create_pixel(r, c) for c in range(canvas_size)],
                spacing=0,
            )
            for r in range(canvas_size)
        ],
        spacing=0,
    )

    # キャンバス全体のドラッグイベント処理
    def on_canvas_pan_start(e):
        nonlocal is_dragging, history
        is_dragging = True
        history.append([r[:] for r in canvas_data])

    def on_canvas_pan_update(e):
        nonlocal is_dragging
        if is_dragging:
            # ドラッグ位置からピクセル座標を計算
            local_x = e.local_x
            local_y = e.local_y
            
            col = int(local_x // pixel_size)
            row = int(local_y // pixel_size)
            
            # 範囲チェック
            if 0 <= row < canvas_size and 0 <= col < canvas_size:
                canvas_data[row][col] = current_color
                canvas_grid.controls[row].controls[col].content.bgcolor = current_color
                page.update()

    def on_canvas_pan_end(e):
        nonlocal is_dragging
        is_dragging = False

    # キャンバスをGestureDetectorで囲む
    canvas_with_drag = ft.GestureDetector(
        content=canvas_grid,
        on_pan_start=on_canvas_pan_start,
        on_pan_update=on_canvas_pan_update,
        on_pan_end=on_canvas_pan_end,
    )

    # カラーパレットの作成 (修正点)
    colors = ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF"]
    
    # 各カラーブロックを生成し、color_blocksリストに格納
    for color in colors:
        color_container = ft.Container(
            width=30,
            height=30,
            bgcolor=color,
            border_radius=ft.border_radius.all(5),
            border=ft.border.all(1, ft.Colors.BLACK), # 初期状態のボーダー
        )
        color_blocks.append(color_container) # リストに追加
        
        # GestureDetectorでタップイベントを処理
        color_palette_item = ft.GestureDetector(
            content=color_container,
            on_tap=lambda e, color=color, container=color_container: set_current_color(color, container),
        )
        # カラーパレットのRowに追加するため、一時的にリストに追加
        # 後でft.Rowのcontrolsに渡します
        
    # カラーパレットのRowを作成
    color_palette = ft.Row(
        [
            ft.GestureDetector(
                content=color_block,
                on_tap=lambda e, color=color_block.bgcolor, block=color_block: set_current_color(color, block),
            )
            for color_block in color_blocks
        ],
        spacing=10,
    )

    # set_current_color 関数の修正
    def set_current_color(color, new_selected_block):
        nonlocal current_color, selected_color_block
        
        # 以前選択されていたブロックのボーダーをリセット
        if selected_color_block is not None:
            selected_color_block.border = ft.border.all(1, ft.Colors.BLACK)
            
        # 新しい選択色を設定
        current_color = color
        
        # 新しく選択されたブロックに目立つボーダーを設定
        new_selected_block.border = ft.border.all(3, ft.Colors.BLUE_ACCENT_700) # 太めの青い枠線
        
        # 選択中のブロックを更新
        selected_color_block = new_selected_block
        
        page.update() # UIを更新

    # アプリ起動時に初期選択色をセットする
    # この部分を追加することで、アプリ起動時に最初のカラーブロックが選択された状態になる
    page.on_ready = lambda: set_current_color(colors[0], color_blocks[0])

    # Undo機能 (変更なし)
    def undo_action(e):
        nonlocal canvas_data, history
        if history:
            canvas_data = history.pop()
            
            for r in range(canvas_size):
                for c in range(canvas_size):
                    canvas_grid.controls[r].controls[c].content.bgcolor = canvas_data[r][c]
            page.update()

    # 保存機能 (変更なし)
    def save_image(e):
        ## todo ## 
        # 実行ファイル化した時のパスをうまいことする
        file_path = "dot_image.py"
        with open(file_path, "w") as f:
            f.write("import pyxel\n\n")
            f.write("image_data = [\n")
            for row in canvas_data:
                rgb_row = []
                for hex_color in row:
                    hex_color = hex_color.lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    rgb_row.append(rgb)
                f.write(f"    {rgb_row},\n")
            f.write("]\n")
        page.snack_bar = ft.SnackBar(ft.Text(f"画像を {file_path} に保存しました！"))
        page.snack_bar.open = True
        page.update()

    # UIのレイアウト (修正)
    page.add(
        canvas_with_drag,
        ft.Divider(),
        color_palette,
        ft.Divider(),
        ft.Row(
            [
                ft.ElevatedButton("Undo", on_click=undo_action),
                ft.ElevatedButton("保存", on_click=save_image),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
    )

ft.app(target=main)