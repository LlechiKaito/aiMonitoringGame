# player.py
import pyxel
from pathfinding import find_shortest_path # 既存の外部モジュール

# 作成したユーティリティモジュールをインポート
import utils.coordinate_utils as cu
import utils.map_utils as mu
import utils.drawing_utils as du

# グローバル定数
TILE_SIZE = 8
PASSABLE_TILE_GRAPHIC = (0, 0) # map_utils.is_tile_passable_on_map に渡される

class Character:
    def __init__(self, x, y, speed=1):
        self.x = x  # ピクセル座標
        self.y = y  # ピクセル座標
        self.speed = speed
        self.size = TILE_SIZE # キャラクターの描画サイズ
        self.color = pyxel.COLOR_RED
        self.last_direction = "down"
        self.path_to_follow = []
        self.path_index = 0

    def is_current_tile_passable_for_corner(self, corner_pixel_x, corner_pixel_y, tilemap_index=0):
        """キャラクターの四隅のいずれかが占めるタイルが通行可能かチェック"""
        tile_x, tile_y = cu.pixel_to_tile(corner_pixel_x, corner_pixel_y, TILE_SIZE)
        tilemap = pyxel.tilemaps[tilemap_index]
        return mu.is_tile_passable_on_map(tile_x, tile_y, tilemap, PASSABLE_TILE_GRAPHIC)

    def update_movement(self):
        old_x, old_y = self.x, self.y
        moved_by_input = False

        if not self.path_to_follow: # 手動操作
            if pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_UP):
                self.y -= self.speed
                self.last_direction = "up"
                moved_by_input = True
            if pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN):
                self.y += self.speed
                self.last_direction = "down"
                moved_by_input = True
            if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT):
                self.x -= self.speed
                self.last_direction = "left"
                moved_by_input = True
            if pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT):
                self.x += self.speed
                self.last_direction = "right"
                moved_by_input = True
        
            if moved_by_input:
                # 移動後の四隅が全て通行可能かチェック
                corners_passable = True
                # 左上、右上、左下、右下
                coords_to_check_pixels = [
                    (self.x, self.y),
                    (self.x + self.size - 1, self.y),
                    (self.x, self.y + self.size - 1),
                    (self.x + self.size - 1, self.y + self.size - 1)
                ]
                for px, py in coords_to_check_pixels:
                    tile_x_check, tile_y_check = cu.pixel_to_tile(px, py, TILE_SIZE)
                    if not mu.is_tile_passable_on_map(tile_x_check, tile_y_check, pyxel.tilemaps[0], PASSABLE_TILE_GRAPHIC):
                        corners_passable = False
                        break
                
                if not corners_passable:
                    self.x = old_x # 元の位置に戻す
                    self.y = old_y

        else: # 自動経路追従
            if self.path_index < len(self.path_to_follow):
                target_tile_x, target_tile_y = self.path_to_follow[self.path_index]
                target_pixel_x, target_pixel_y = cu.tile_to_pixel(target_tile_x, target_tile_y, TILE_SIZE)

                dx = target_pixel_x - self.x
                dy = target_pixel_y - self.y

                if abs(dx) <= self.speed: self.x = target_pixel_x
                elif dx > 0: self.x += self.speed
                elif dx < 0: self.x -= self.speed
                
                if abs(dy) <= self.speed: self.y = target_pixel_y
                elif dy > 0: self.y += self.speed
                elif dy < 0: self.y -= self.speed

                if self.x == target_pixel_x and self.y == target_pixel_y:
                    self.path_index += 1
            else: # 目的地到着
                self.path_to_follow = []
                self.path_index = 0
                print("目的地に到着しました。")

        # 画面範囲外に出ないようにする
        self.x = max(0, min(self.x, pyxel.width - self.size))
        self.y = max(0, min(self.y, pyxel.height - self.size))
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.size, self.size, self.color)

    def set_path(self, path_coords):
        self.path_to_follow = path_coords
        self.path_index = 0
        if path_coords:
            print(f"新しい経路を設定しました: {path_coords}")
        else:
            print("経路が見つかりませんでした、またはクリアされました。")

    def get_current_tile_coord(self):
        # キャラクターの中心または左上のタイル座標を返すか明確にする
        # ここでは左上基準のタイル座標
        return cu.pixel_to_tile(self.x, self.y, TILE_SIZE)


class App:
    def __init__(self, resource_file="sprite.pyxres"):
        pyxel.init(160, 120, title="Pathfinding Demo Modularized", fps=30)

        try:
            pyxel.load(resource_file)
            print(f"リソースファイル '{resource_file}' をロードしました。")
        except Exception as e:
            print(f"警告: リソースファイル '{resource_file}' のロードに失敗しました: {e}")
            # 開発中はリソースファイルなしでも動作するように、基本的な図形などで代替表示も検討できる
            # pyxel.quit() # ここで終了させない場合は、リソースなしのフォールバックが必要
            # return

        initial_player_tile_x = 6
        initial_player_tile_y = 5
        player_start_x, player_start_y = cu.tile_to_pixel(initial_player_tile_x, initial_player_tile_y, TILE_SIZE)
        self.player = Character(player_start_x, player_start_y)
        
        self.current_path_coords = []
        self.destination_tile = None # (tile_x, tile_y)
        self.show_path_debug = True
        
        pyxel.mouse(visible=True)
        pyxel.run(self.update, self.draw)

    def set_target_and_find_path(self, goal_tile_coord):
        self.destination_tile = goal_tile_coord
        start_tile_coord = self.player.get_current_tile_coord()
        
        print(f"経路探索開始: スタート {start_tile_coord}, ゴール {self.destination_tile}")
        
        # pathfinding モジュールの関数はそのまま使用
        self.current_path_coords = find_shortest_path(
            start_coord=start_tile_coord,
            goal_coord=self.destination_tile,
            tilemap_index=0, # find_shortest_path 側で pyxel.tilemaps[0] を参照すると仮定
            passable_tile_graphic=PASSABLE_TILE_GRAPHIC # 通行可能なグラフィック情報を渡す
        )
        self.player.set_path(self.current_path_coords)

        if self.current_path_coords:
            print(f"経路発見: {self.current_path_coords}")
        else:
            print(f"経路が見つかりませんでした。スタート:{start_tile_coord}, ゴール:{self.destination_tile}")

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.player.update_movement()

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mouse_tile_x, mouse_tile_y = cu.pixel_to_tile(pyxel.mouse_x, pyxel.mouse_y, TILE_SIZE)
            
            tilemap = pyxel.tilemaps[0] # 現在のタイルマップ参照
            if mu.is_tile_on_map(mouse_tile_x, mouse_tile_y, tilemap):
                # クリック地点が通行可能かどうかもチェックした方が親切かもしれない
                # if mu.is_tile_passable_on_map(mouse_tile_x, mouse_tile_y, tilemap, PASSABLE_TILE_GRAPHIC):
                self.set_target_and_find_path((mouse_tile_x, mouse_tile_y))
                # else:
                #     print(f"クリック地点 ({mouse_tile_x}, {mouse_tile_y}) は通行不可能なタイルです。")
            else:
                print(f"クリック地点 ({mouse_tile_x}, {mouse_tile_y}) はマップ範囲外です。")
        
        if pyxel.btnp(pyxel.KEY_P):
            self.show_path_debug = not self.show_path_debug

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        
        current_tilemap = pyxel.tilemaps[0] # 描画対象のタイルマップ
        pyxel.bltm(0, 0, 0, 0, 0, current_tilemap.width, current_tilemap.height, colkey=pyxel.COLOR_LIME)

        self.player.draw()

        # 経路のデバッグ表示
        if self.show_path_debug and self.current_path_coords:
            du.draw_path_lines(self.current_path_coords, TILE_SIZE, pyxel.COLOR_GREEN)
            # 目的地タイルをハイライト
            if self.destination_tile:
                 du.highlight_tile_frame(self.destination_tile[0], self.destination_tile[1], TILE_SIZE, pyxel.COLOR_YELLOW)

        # マウスカーソル情報表示
        mouse_pixel_x = pyxel.mouse_x
        mouse_pixel_y = pyxel.mouse_y
        mouse_tile_x, mouse_tile_y = cu.pixel_to_tile(mouse_pixel_x, mouse_pixel_y, TILE_SIZE)

        # マウスカーソルのあるタイルをハイライト
        du.highlight_tile_frame(mouse_tile_x, mouse_tile_y, TILE_SIZE, pyxel.COLOR_PINK, tilemap_to_check_bounds=current_tilemap)

        # デバッグ情報テキスト表示
        text_start_y = 5
        line_height = 10
        
        player_tile_display = self.player.get_current_tile_coord()
        pyxel.text(5, text_start_y, f"Player Tile: {player_tile_display}", pyxel.COLOR_WHITE)
        
        if self.destination_tile:
            pyxel.text(5, text_start_y + line_height, f"Target Tile: {self.destination_tile}", pyxel.COLOR_WHITE)
        
        if self.player.path_to_follow: # path_to_follow が空でない場合のみ表示
             pyxel.text(5, text_start_y + line_height * 2, f"Path Seg: {self.player.path_index}/{len(self.player.path_to_follow)}", pyxel.COLOR_WHITE)
        
        pyxel.text(5, text_start_y + line_height * 3, f"Mouse(px): ({mouse_pixel_x},{mouse_pixel_y})", pyxel.COLOR_WHITE)
        pyxel.text(5, text_start_y + line_height * 4, f"Mouse(tile): ({mouse_tile_x},{mouse_tile_y})", pyxel.COLOR_WHITE)
        
        pyxel.text(5, pyxel.height - 10, "LMB: Set Target / P:Toggle Path / Q:Quit", pyxel.COLOR_WHITE)


if __name__ == '__main__':
    # 実際のプロジェクトでは、`pathfinding.py` も同じディレクトリにあるか、
    # Pythonがモジュールとして認識できる場所にある必要があります。
    App(resource_file="sprite.pyxres") # リソースファイル名を適宜変更してください
