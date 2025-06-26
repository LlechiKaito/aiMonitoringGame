import flet as ft

class CharacterForm:
    def __init__(self):
        self.name_field = None
        self.description_field = None
        self.form_container = None
        
    def create_form(self):
        """キャラクター情報入力フォームを作成"""
        # キャラクター名入力フィールド
        self.name_field = ft.TextField(
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
        
        # キャラクター説明入力フィールド
        self.description_field = ft.TextField(
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
        
        # フォームコンテナ
        self.form_container = ft.Container(
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
                    self.name_field,
                    ft.Container(height=20),
                    ft.Text(
                        "説明文",
                        size=14,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Container(height=5),
                    self.description_field,
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
        
        return self.form_container
    
    def get_character_name(self):
        """キャラクター名を取得"""
        return self.name_field.value if self.name_field.value else "名前未設定"
    
    def get_character_description(self):
        """キャラクター説明を取得"""
        return self.description_field.value if self.description_field.value else "説明なし"
    
    def clear_fields(self):
        """入力フィールドをクリア"""
        if self.name_field:
            self.name_field.value = ""
        if self.description_field:
            self.description_field.value = ""
