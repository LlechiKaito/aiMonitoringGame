import flet as ft

def createNPC_main(page: ft.Page, back_callback=None):
    page.controls.clear()

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

    # キャラクター情報の入力フィールド
    character_name_field = ft.TextField(
        hint_text="キャラクター名",
        width=300,
        multiline=False,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        border_color=ft.Colors.BLUE_GREY_300,
        focused_border_color=ft.Colors.BLUE_ACCENT,
        filled=True,
        dense=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=16),
    )
    
    character_description_field = ft.TextField(
        hint_text="キャラクターの説明",
        width=300,
        multiline=True,
        min_lines=5,
        max_lines=10,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        border_color=ft.Colors.BLUE_GREY_300,
        focused_border_color=ft.Colors.BLUE_ACCENT,
        filled=True,
        dense=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=16),
    )

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

    # キャラクター登録機能 (変更)
    def register_character(e):
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
        
        # キャラクター情報の取得
        character_name = character_name_field.value or "名前未設定"
        character_description = character_description_field.value or "説明なし"
        
        # DB登録処理（仮実装）
        # TODO: 実際のDB登録処理を実装する
        register_to_database(character_name, character_description, file_path)
        
        page.snack_bar = ft.SnackBar(ft.Text(f"キャラクター「{character_name}」を登録しました！"))
        page.snack_bar.open = True
        page.update()

    # DB登録の仮関数
    def register_to_database(name, description, image_path):
        """
        キャラクター情報をデータベースに登録する（仮実装）
        TODO: 実際のDB接続・登録処理を実装
        """
        print(f"DB登録 - 名前: {name}, 説明: {description}, 画像: {image_path}")
        # ここに実際のDB登録処理を実装予定

    # UIのレイアウト (修正)
    # 左側のドット絵エディター部分
    editor_section = ft.Column(
        [
            ft.Text(
                "ドット絵エディター",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            ft.Container(height=10),
            canvas_with_drag,
            ft.Container(height=15),
            ft.Text(
                "カラーパレット",
                size=14,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.WHITE70,
            ),
            ft.Container(height=5),
            color_palette,
            ft.Container(height=20),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Undo", 
                        on_click=undo_action,
                        width=100,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_GREY_700,
                            color=ft.Colors.WHITE,
                        )
                    ),
                    ft.ElevatedButton(
                        "登録", 
                        on_click=register_character,
                        width=100,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_ACCENT_700,
                            color=ft.Colors.WHITE,
                        )
                    ),
                    ft.ElevatedButton(
                        "戻る", 
                        on_click=lambda e: back_callback() if back_callback else None,
                        width=100,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.ORANGE_ACCENT_700,
                            color=ft.Colors.WHITE,
                        )
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )
    
    # 右側のキャラクター情報入力フォーム
    character_form = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "キャラクター情報", 
                    size=20, 
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Divider(color=ft.Colors.BLUE_GREY_400),
                ft.Container(height=5),
                ft.Text(
                    "キャラクター名",
                    size=14,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Container(height=5),
                character_name_field,
                ft.Container(height=20),
                ft.Text(
                    "説明文",
                    size=14,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Container(height=5),
                character_description_field,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=0,
        ),
        width=350,
        padding=ft.padding.all(25),
        bgcolor=ft.Colors.BLUE_GREY_900,
        border_radius=ft.border_radius.all(12),
        border=ft.border.all(1, ft.Colors.BLUE_GREY_600),
    )
    
    # メイン画面のレイアウト
    main_layout = ft.Row(
        [
            ft.Container(
                content=editor_section,
                padding=ft.padding.all(5),
            ),
            ft.VerticalDivider(color=ft.Colors.BLUE_GREY_600),
            ft.Container(
                content=character_form,
                padding=ft.padding.all(5),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20,
    )
    
    page.add(main_layout)