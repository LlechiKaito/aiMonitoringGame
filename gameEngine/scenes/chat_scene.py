import pyxel
from .base_scene import BaseScene

class ChatScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.play_area_width = 192
        self.play_area_height = 144
        self.play_area_color = 1

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_G):
            self.scene_manager.set_scene("game_scene")

    def draw(self):
        pyxel.cls(0)
        pyxel.rect(0, 0, self.play_area_width, self.play_area_height, self.play_area_color)
        
        