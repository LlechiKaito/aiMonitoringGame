# scenes/game_scene.py
import pyxel
from PIL import ImageFont
# from PyxelUniversalFont import Writer # WriterインスタンスはSceneManager経由で渡される想定

from .base_scene import BaseScene

class GameScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        # GameScene固有の初期化
        self.play_area_width = 192
        self.menu_area_width = 64
        # self.screen_width, self.screen_height は BaseScene から継承
        self.grid_size = 16
        self.menu_area_x_start = self.play_area_width
        self.play_bg_color_1 = 12
        self.play_bg_color_2 = 1
        self.menu_bg_color_1 = 6
        self.menu_bg_color_2 = 5
        # self.text_color_original, self.font_point_size, self.writer_play, self.writer_menu は BaseScene から継承

        self.text_play_jp = "プレイエリア"
        self.text_menu_jp_long = "これはメニューエリアに表示する長いテキストです。幅に合わせて自動で改行されるはずです。美咲フォントで表示します。"
        self.text_menu_jp = self.text_menu_jp_long

        # PyxelUniversalFontのWriterインスタンスはSceneManagerから渡されるので、ここでは初期化しない
        # フォントパスもSceneManager側で管理する方が良いかもしれません

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q): # Qで終了はグローバルな処理なのでmain.pyに移管しても良い
            pyxel.quit() # もしくは self.scene_manager.quit_application() のようなメソッドを呼ぶ

        if pyxel.btnp(pyxel.KEY_T): # 例: Tキーでタイトルシーンへ遷移
            self.scene_manager.change_scene('title')
        if pyxel.btnp(pyxel.KEY_M):
            self.scene_manager.change_scene('menu')


    def draw_checkerboard(self, x_offset, y_offset, width, height, color1, color2):
        for yi in range(height // self.grid_size):
            for xi in range(width // self.grid_size):
                screen_x = x_offset + xi * self.grid_size
                screen_y = y_offset + yi * self.grid_size
                current_color = color1 if (xi + yi) % 2 == 0 else color2
                pyxel.rect(screen_x, screen_y, self.grid_size, self.grid_size, current_color)

    # draw_text_multiline メソッドはここに残すか、utils.py に移動
    def draw_text_multiline(self, writer_instance, x, y, text, max_width,
                            text_color,
                            font_size_to_use,
                            line_spacing_extra=3):
        if not writer_instance:
            print("Error: Writer instance is None.")
            return

        #if not hasattr(writer_instance, 'font_path') or not writer_instance.font_path:
        #    print("Error: Writer instance does not have a valid 'font_path' attribute.")
        #    try:
        #        writer_instance.draw(x, y, "[No Font Path]", font_size_to_use, text_color)
        #    except Exception as e_draw: print(f"Error in fallback draw: {e_draw}")
        #    return

        pillow_font = None
        try:
            pillow_font = ImageFont.truetype(writer_instance.font_path, font_size_to_use)
        except IOError:
            print(f"Error: Could not read font file at '{writer_instance.font_path}'.")
            try: writer_instance.draw(x, y, "[Font IO Error]", font_size_to_use, text_color)
            except Exception as e_draw: print(f"Error in fallback draw: {e_draw}")
            return
        except Exception as e:
            print(f"Error creating Pillow font object: {e}")
            try: writer_instance.draw(x, y, "[PillowFont Err]", font_size_to_use, text_color)
            except Exception as e_draw: print(f"Error in fallback draw: {e_draw}")
            return

        if not pillow_font:
            print("Error: Pillow font object could not be created.")
            try: writer_instance.draw(x, y, "[PFont Null Err]", font_size_to_use, text_color)
            except Exception as e_draw: print(f"Error in fallback draw: {e_draw}")
            return

        line_height = font_size_to_use + line_spacing_extra
        if hasattr(pillow_font, 'getmetrics'):
            try:
                metrics = pillow_font.getmetrics(); font_actual_height = metrics[0]
                line_height = font_actual_height + line_spacing_extra
            except Exception as e: print(f"Warning: Could not get font metrics: {e}.")
        elif hasattr(pillow_font, 'getsize'):
            try: _, text_h = pillow_font.getsize("A"); line_height = text_h + line_spacing_extra
            except Exception as e: print(f"Warning: Could not get font legacy size for height: {e}.")

        current_line = ""; current_y = y
        for char in text:
            temp_line = current_line + char; current_width = 0
            try:
                if hasattr(pillow_font, 'getlength'): current_width = int(pillow_font.getlength(temp_line))
                elif hasattr(pillow_font, 'getbbox'):
                    if not temp_line: current_width = 0
                    else: bbox = pillow_font.getbbox(temp_line); current_width = int(bbox[2] - bbox[0])
                elif hasattr(pillow_font, 'getsize'): text_w, _ = pillow_font.getsize(temp_line); current_width = int(text_w)
                else:
                    writer_instance.draw(x, current_y, "[WidthCalc Met Err]", font_size_to_use, text_color); return
            except Exception as e:
                print(f"Error calculating text width for '{temp_line}': {e}")
                if current_line: writer_instance.draw(x, current_y, current_line, font_size_to_use, text_color)
                current_y += line_height; current_line = ""; continue

            if current_width <= max_width: current_line = temp_line
            else:
                writer_instance.draw(x, current_y, current_line, font_size_to_use, text_color)
                current_y += line_height; current_line = char; single_char_width = 0
                try:
                    if hasattr(pillow_font, 'getlength'): single_char_width = int(pillow_font.getlength(char))
                    elif hasattr(pillow_font, 'getbbox'):
                        if not char: single_char_width = 0
                        else: bbox = pillow_font.getbbox(char); single_char_width = int(bbox[2] - bbox[0])
                    elif hasattr(pillow_font, 'getsize'): text_w, _ = pillow_font.getsize(char); single_char_width = int(text_w)
                except: pass
                if single_char_width > max_width and max_width > 0:
                    print(f"Warning: Char '{char}' ({single_char_width}px) > max_width ({max_width}px). Skipping."); current_line = ""
        if current_line: writer_instance.draw(x, current_y, current_line, font_size_to_use, text_color)


    def draw(self):
        pyxel.cls(0) # 背景クリアは各シーンで行うか、SceneManagerで行うか検討
        self.draw_checkerboard(0, 0, self.play_area_width, self.screen_height, self.play_bg_color_1, self.play_bg_color_2)
        if self.writer_play:
            text_play_x = 5; text_play_y = 5
            self.writer_play.draw(text_play_x, text_play_y, self.text_play_jp, self.font_point_size, self.text_color_original)

        self.draw_checkerboard(self.menu_area_x_start, 0, self.menu_area_width, self.screen_height, self.menu_bg_color_1, self.menu_bg_color_2)
        if self.writer_menu:
            text_menu_x = self.menu_area_x_start + 5; text_menu_y = 5
            drawable_menu_width = self.menu_area_width - 10
            self.draw_text_multiline(
                self.writer_menu, text_menu_x, text_menu_y, self.text_menu_jp,
                drawable_menu_width, self.text_color_original,
                font_size_to_use=self.font_point_size, line_spacing_extra=3
            )

    def on_enter(self, previous_scene_name=None, **kwargs):
        print(f"Entered GameScene from {previous_scene_name}")
        # ゲーム開始時の初期化処理など

    def on_exit(self, next_scene_name=None):
        print(f"Exiting GameScene to {next_scene_name}")
        # ゲーム終了時の後処理など