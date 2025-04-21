import pyxel

pyxel.init(160, 120, title="Pyxel Test")

def update():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(0)

pyxel.run(update, draw)