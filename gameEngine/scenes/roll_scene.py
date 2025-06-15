import pyxel
from gameEngine.scenes.base_scene import BaseScene

class RollScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.roll_area_height = 32
        self.roll_area_width = 192
        self.roll_area_x = (self.screen_width - self.roll_area_width) // 2
        self.roll_area_y = (self.screen_height - self.roll_area_height) // 2
        self.roll_area_color = 7
        self.roll_area_text_color = 7
        self.roll_area_text_size = 10

        self.placeholder_text = "Enter your roll text"
        self.roll_text = ""
        self.roll_text_x = (self.screen_width - self.roll_area_width) // 2
        self.roll_text_y = (self.screen_height - self.roll_area_height) // 2 + self.roll_area_height // 4
        self.roll_text_color = 8
        self.roll_text_size = 10

    def update(self):
        for i in range(pyxel.KEY_A, pyxel.KEY_Z):
            if pyxel.btnp(i):
                self.roll_text += chr(i)
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.scene_manager.change_scene('chat', roll_text=self.roll_text)

    def draw(self):
        pyxel.cls(0)
        pyxel.rect(self.roll_area_x, self.roll_area_y, self.roll_area_width,
                   self.roll_area_height, self.roll_area_color)
        if self.roll_text == "":
            pyxel.text(self.roll_text_x, self.roll_text_y,
                       self.placeholder_text, self.roll_text_color)
        else:
            pyxel.text(self.roll_text_x, self.roll_text_y,
                       self.roll_text, self.roll_text_color)
