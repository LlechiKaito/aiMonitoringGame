# drawing_utils.py
import pyxel
from . import coordinate_utils as cu # get_tile_center_pixel を使用

def draw_path_lines(path_coords, tile_size, color):
    """
    指定された経路（タイル座標のリスト）をタイルの中心を結ぶ線で描画します。
    
    Args:
        path_coords (list): [(x1, y1), (x2, y2), ...] の形式のタイル座標リスト。
        tile_size (int): 1タイルのピクセルサイズ。
        color (int): Pyxelのカラー定数。
    """
    if not path_coords or len(path_coords) < 2:
        return

    for i in range(len(path_coords) - 1):
        start_tile_x, start_tile_y = path_coords[i]
        end_tile_x, end_tile_y = path_coords[i+1]

        x1, y1 = cu.get_tile_center_pixel(start_tile_x, start_tile_y, tile_size)
        x2, y2 = cu.get_tile_center_pixel(end_tile_x, end_tile_y, tile_size)
        
        pyxel.line(x1, y1, x2, y2, color)

def highlight_tile_frame(tile_x, tile_y, tile_size, color, tilemap_to_check_bounds=None):
    """
    指定されたタイルを枠線でハイライトします。
    tilemap_to_check_boundsが指定されていれば、その範囲内のみハイライトします。
    
    Args:
        tile_x (int): ハイライトするタイルのX座標。
        tile_y (int): ハイライトするタイルのY座標。
        tile_size (int): 1タイルのピクセルサイズ。
        color (int): Pyxelのカラー定数。
        tilemap_to_check_bounds (pyxel.Tilemap, optional): 境界チェック用のタイルマップ。
    """
    if tilemap_to_check_bounds:
        if not (0 <= tile_x < tilemap_to_check_bounds.width and \
                0 <= tile_y < tilemap_to_check_bounds.height):
            return # マップ範囲外なら描画しない
    
    pixel_x, pixel_y = cu.tile_to_pixel(tile_x, tile_y, tile_size)
    pyxel.rectb(pixel_x, pixel_y, tile_size, tile_size, color)
