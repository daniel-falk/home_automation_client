import pygame

class HallView:

    def __init__(self, devices, screen, write_text):
        self.devices = devices
        self.screen = screen
        self.write_text = write_text

    def update(self, flip=True):
        self.screen.fill((255,255,255))

        w, h = self._get_dimension()

        # Write action buttons
        self.write_text("on/off", (int(w/10), 0), valign="bottom")

        if flip:
            pygame.display.flip()

    def button_clicked(self, name):
        self.update(flip=False)
        self.write_text(name, (0, 0), valign="center", halign="center")
        pygame.display.flip()

    def _get_dimension(self):
        w, h = pygame.display.get_surface().get_size()
        return (w, h)

