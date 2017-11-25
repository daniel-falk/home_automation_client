from time import sleep
import pygame

from ..interface import InterfacePanelMapping as IOMap
from views.hall_view import HallView


class Gui:

    def __init__(self, config, panel, devices):
        self.config = config
        self.panel = panel
        self.devices = devices

        self.w = int(self.config["width"])
        self.h = int(self.config["height"])

        for name, pins in IOMap.RotaryEncoders.iteritems():
            panel.add_rotary_encoder(name, self._wheel_callback, *pins)

        for name, pin in IOMap.Buttons.iteritems():
            panel.add_button(name, self._button_callback, pin)

        pygame.init()
        self.screen = pygame.display.set_mode(
                (self.w, self.h),
                pygame.FULLSCREEN)

        pygame.font.init()

        self.views = []
        self.views.append(HallView(devices, self.screen, self._write_text))

        self.current_view_id = 0
        self.current_view = self.views[self.current_view_id]
        self.current_view.update()

    def run(self):
        try:
            while(True):
                sleep(1)
        except KeyboardInterrupt:
            pass

    def _wheel_callback(self, pos, dir):
        pass

    def _button_callback(self, name):
        self.current_view.button_clicked(name)

    def _write_text(self, text, pos, size = 50, color = (0, 0, 0),
            valign="top", halign="left"):
        x, y = pos

        text = str(text)
        font = pygame.font.SysFont('Comic Sans MS', size)
        text = font.render(text, True, color)

        if halign in ["right", "r"]:
            x += self.w - text.get_width()
        if halign in ["center", "c"]:
            x += int(self.w - text.get_width())/2
        if valign in ["bottom", "b"]:
            y += self.h - text.get_height()
        if halign in ["center", "c"]:
            y += int(self.h - text.get_height())/2

        self.screen.blit(text, (x, y))


