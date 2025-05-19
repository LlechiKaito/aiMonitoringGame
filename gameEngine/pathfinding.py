# pathfinding.py
import heapq
import pyxel

def heuristic(a, b):
    """
    2点間のヒューリスティックコスト（マンハッタン距離）を計算します。
    Args:
        a (tuple[int, int]): 点Aの座標 (x, y)
        b (tuple[int, int]): 点Bの座標 (x, y)
    Returns:
        int: マンハッタン距離
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(tile_x, tile_y, tilemap_width, tilemap_height):
    """
    指定されたタイルの上下左右の隣接タイル座標のリストを返します。
    マップ範囲外の座標は含めません。
    Args:
        tile_x (int): 現在のタイルのX座標
        tile_y (int): 現在のタイルのY座標
        tilemap_width (int): タイルマップの幅（タイル数）
        tilemap_height (int): タイルマップの高さ（タイル数）
    Returns:
        list[tuple[int, int]]: 隣接する有効なタイル座標のリスト
    """
    neighbors = []
    moves = [(0, -1), (0, 1), (-1, 0), (1, 0)] # 上, 下, 左, 右

    for dx, dy in moves:
        nx, ny = tile_x + dx, tile_y + dy
        if 0 <= nx < tilemap_width and 0 <= ny < tilemap_height:
            neighbors.append((nx, ny))
    return neighbors

def is_tile_passable_for_pathfinding(tile_x, tile_y, tilemap_index, passable_tile_graphic):
    """
    指定されたタイルが通行可能かどうかを判定します。
    Pyxelのタイルマップ情報を参照します。
    Args:
        tile_x (int): 確認するタイルのX座標
        tile_y (int): 確認するタイルのY座標
        tilemap_index (int): 対象のタイルマップ番号 (0-7)
        passable_tile_graphic (tuple[int, int]): 通行可能なタイルのイメージバンク上の(u,v)座標
    Returns:
        bool: 通行可能ならTrue、そうでなければFalse
    """
    # Pyxelが初期化されていないか、タイルマップが存在しない場合のガード
    if not hasattr(pyxel, 'tilemaps') or tilemap_index >= len(pyxel.tilemaps):
        print(f"警告: Tilemap {tilemap_index} にアクセスできません。")
        return False
        
    tile_graphic = pyxel.tilemaps[tilemap_index].pget(tile_x, tile_y)
    return tile_graphic == passable_tile_graphic

def reconstruct_path(came_from, current_coord):
    """
    came_from辞書を辿って、ゴールからスタートまでの経路を再構築します。
    Args:
        came_from (dict): 各座標がどの座標から来たかを記録した辞書
        current_coord (tuple[int, int]): ゴール座標
    Returns:
        list[tuple[int, int]]: スタートからゴールまでのタイル座標のリスト
    """
    path = [current_coord]
    while current_coord in came_from:
        current_coord = came_from[current_coord]
        path.append(current_coord)
    path.reverse()  # スタートからゴールの順にする
    return path

def find_shortest_path(start_coord, goal_coord, tilemap_index, passable_tile_graphic):
    """
    A*アルゴリズムを使用して、スタート座標からゴール座標までの最短経路を計算します。
    Args:
        start_coord (tuple[int, int]): スタートのタイル座標 (x, y)
        goal_coord (tuple[int, int]): ゴールのタイル座標 (x, y)
        tilemap_index (int): 使用するタイルマップのインデックス (0-7)
        passable_tile_graphic (tuple[int, int]): 通行可能なタイルのイメージバンク上の(u,v)座標
                                                例: (0, 0)
    Returns:
        list[tuple[int, int]]: 最短経路上のタイル座標のリスト。
                               経路が見つからない場合は空のリストを返します。
    """
    if not hasattr(pyxel, 'tilemaps') or tilemap_index >= len(pyxel.tilemaps):
        print(f"エラー: Tilemap {tilemap_index} がロードされていません。経路探索を中止します。")
        return []
        
    tilemap = pyxel.tilemaps[tilemap_index]
    tilemap_width = tilemap.width
    tilemap_height = tilemap.height

    # スタート地点またはゴール地点が通行不可能な場合は空のリストを返す
    if not is_tile_passable_for_pathfinding(start_coord[0], start_coord[1], tilemap_index, passable_tile_graphic) or \
       not is_tile_passable_for_pathfinding(goal_coord[0], goal_coord[1], tilemap_index, passable_tile_graphic):
        print("警告: スタート地点またはゴール地点が通行不可能です。")
        return []

    open_set = []  # 優先度付きキュー。要素は (f_score, g_score, coord) g_scoreはtie-breaker
    heapq.heappush(open_set, (heuristic(start_coord, goal_coord), 0, start_coord))

    came_from = {}  # came_from[coord] = previous_coord

    # g_score[coord] = コスト from start to coord
    g_score = {start_coord: 0}

    # f_score[coord] = g_score[coord] + heuristic(coord, goal) (open_setの優先度用だが、ここでは直接タプルに入れる)

    processed_coords = set() # 既に処理したノードを記録 (経路復元とは別)

    while open_set:
        current_f_score, current_g_score, current_coord = heapq.heappop(open_set)
        
        if current_coord in processed_coords: # 既に最適な経路で処理済みならスキップ
            continue
        processed_coords.add(current_coord)

        if current_coord == goal_coord:
            return reconstruct_path(came_from, current_coord)

        for neighbor_coord in get_neighbors(current_coord[0], current_coord[1], tilemap_width, tilemap_height):
            if not is_tile_passable_for_pathfinding(neighbor_coord[0], neighbor_coord[1], tilemap_index, passable_tile_graphic):
                continue  # 通行不可タイルはスキップ

            # 隣接ノードへの移動コスト (ここでは常に1)
            tentative_g_score = current_g_score + 1

            if tentative_g_score < g_score.get(neighbor_coord, float('inf')):
                came_from[neighbor_coord] = current_coord
                g_score[neighbor_coord] = tentative_g_score
                new_f_score = tentative_g_score + heuristic(neighbor_coord, goal_coord)
                heapq.heappush(open_set, (new_f_score, tentative_g_score, neighbor_coord))
                # open_set に同じ座標があってもf_scoreが低ければ更新される (実際は新しい要素として追加される)
                # 処理済みセット(processed_coords)で重複処理を防ぐ

    return []  # 経路が見つからなかった場合
