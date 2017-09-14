"""Views for the game."""

import pygame


class Color:
    """Game colors."""

    # Class variables
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    purple = (127, 0, 255)


class GameView:
    """Game view."""

    def __init__(self):
        """Create game view."""
        # Instance variables
        self.size = width, height = 800, 450

        # Create [screen]
        self.screen = pygame.display.set_mode(self.size)

    def draw(self, player, enemies, decaying_teleporters):
        """Draw all elements on the screen."""
        # Clear [screen]
        self.screen.fill(Color.white)

        # Draw Objects
        player.draw(self.screen)
        for enemy in enemies:
            enemy.draw(self.screen)
            for projectile in enemy.projectiles:
                projectile.draw(self.screen)
        for decaying_teleporter in decaying_teleporters:
            decaying_teleporter.draw(self.screen)
        # for projectile in projectiles:
        #     projectile.draw(screen)

        # Display
        pygame.display.flip()
