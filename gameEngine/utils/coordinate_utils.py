# coordinate_utils.py

def pixel_to_tile(pixel_x, pixel_y, tile_size):
    """
    ピクセル座標をタイル座標に変換します。
    tile_sizeが0の場合は(0,0)を返します（エラー回避）。
    """
    if tile_size == 0:
        # エラーを発生させるか、デフォルト値を返すかを選択できます
        # ここでは(0,0)を返します
        return 0, 0
    return pixel_x // tile_size, pixel_y // tile_size

def tile_to_pixel(tile_x, tile_y, tile_size):
    """
    タイル座標をピクセル座標（タイルの左上基準）に変換します。
    """
    return tile_x * tile_size, tile_y * tile_size

def get_tile_center_pixel(tile_x, tile_y, tile_size):
    """
    指定されたタイルの中心のピクセル座標を取得します。
    """
    offset = tile_size // 2
    return tile_x * tile_size + offset, tile_y * tile_size + offset
