import random

class Player:
    def __init__(self, x=100, y=50):
        self.x = x
        self.y = y
        self.size = 16  # ドット絵のサイズに合わせて変更
        self.dx = random.choice([-2, 2])
        self.dy = random.choice([-2, 2])

    def update(self):
        # 勝手に移動（壁で跳ね返る）
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= 200 - self.size:
            self.dx *= -1
            self.x = max(0, min(self.x, 200 - self.size))
        if self.y <= 0 or self.y >= 100 - self.size:
            self.dy *= -1
            self.y = max(0, min(self.y, 100 - self.size))

    def draw(self):
        import pyxel
        # イメージバンク1番からドット絵を描画
        pyxel.blt(self.x, self.y, 1, 0, 0, 16, 16)
