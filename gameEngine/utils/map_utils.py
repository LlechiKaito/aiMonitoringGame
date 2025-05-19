# map_utils.py
import pyxel

def is_tile_on_map(tile_x, tile_y, tilemap):
    """指定されたタイル座標がタイルマップの範囲内かを確認します。"""
    return 0 <= tile_x < tilemap.width and 0 <= tile_y < tilemap.height

def get_tile_graphic(tile_x, tile_y, tilemap):
    """指定されたタイルマップのタイルグラフィックを取得します。範囲外ならNoneを返します。"""
    if is_tile_on_map(tile_x, tile_y, tilemap):
        return tilemap.pget(tile_x, tile_y)
    return None

def is_tile_passable_on_map(tile_x, tile_y, tilemap, passable_graphic_tuple):
    """
    指定されたタイルマップ上のタイルが通行可能かどうかを判定します。
    
    Args:
        tile_x (int): タイルのX座標。
        tile_y (int): タイルのY座標。
        tilemap (pyxel.Tilemap): Pyxelのタイルマップオブジェクト。
        passable_graphic_tuple (tuple): 通行可能なタイルグラフィックのタプル (例: (0,0))。
        
    Returns:
        bool: 通行可能ならTrue、そうでなければFalse。
    """
    if not is_tile_on_map(tile_x, tile_y, tilemap):
        return False
    tile_graphic = tilemap.pget(tile_x, tile_y)
    return tile_graphic == passable_graphic_tuple
