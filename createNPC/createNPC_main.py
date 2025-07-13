import flet as ft
from .canvas import Canvas
from .color_palette import ColorPalette
from .character_form import CharacterForm
from .database import register_to_database

def createNPC_main(page: ft.Page, back_callback=None):
    page.controls.clear()

    page.title = "ドット絵エディター"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 各コンポーネントのインスタンスを作成
    canvas = Canvas(size=16, pixel_size=20)
    color_palette = ColorPalette()
    character_form = CharacterForm()
    
    # ページを各コンポーネントに設定
    canvas.set_page(page)
    color_palette.set_page(page)
    
    # カラーパレットの色変更時にキャンバスの色も更新
    color_palette.set_color_change_callback(canvas.set_current_color)

    # Undo機能
    def undo_action(e):
        canvas.undo()

    # キャラクター登録機能
    def register_character(e):
        # 実行ファイル化した時のパスをうまいことする
        file_path = "dot_image.py"
        canvas.export_to_python_file(file_path)
        
        # キャラクター情報の取得
        character_name = character_form.get_character_name()
        character_description = character_form.get_character_description()
        
        # DB登録処理
        register_to_database(character_name, character_description, file_path)
        
        page.snack_bar = ft.SnackBar(ft.Text(f"キャラクター「{character_name}」を登録しました！"))
        page.snack_bar.open = True
        page.update()

    # UIコンポーネントの作成
    canvas_with_drag = canvas.create_canvas_with_drag()
    color_palette_ui = color_palette.create_color_palette()
    character_form_ui = character_form.create_form()

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
            color_palette_ui,
            ft.Container(height=20),
            ft.ElevatedButton(
                "Undo", 
                on_click=undo_action,
                width=100,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE_GREY_700,
                    color=ft.Colors.WHITE,
                )
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )
    
    # コントローラー部分
    controller_section = ft.Container(
        ft.Row(
            [
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
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
        ),
    )

    # メイン画面のレイアウト
    main_layout = ft.Column(
        [
            ft.Row(
                [
                    ft.Container(
                        content=editor_section,
                        padding=ft.padding.all(5),
                    ),
                    ft.VerticalDivider(color=ft.Colors.BLUE_GREY_600),
                    ft.Container(
                        content=character_form_ui,
                        padding=ft.padding.all(5),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=20,
            ),
            controller_section,
        ],
    )
    
    page.add(main_layout)