"""Models for the game."""

import pygame
import math
import util.rect
import util.vector
import view


class Teleporter:
    """
    Teleporter box around the Player.

        Attributes:
            [rect]      Rect object
            [period]    time it takes for one oscillation (expand & contract)
            [span]      tuple (min, max) span of the teleporter Rect's length
            [direction] [1|-1] where 1=expanding, -1=contracting

    """

    def __init__(self, center, size):
        """
        Create new Teleporter.

            Parameters:
                [center]    tuple (x, y)
                [size]      tuple (width, height)
                [period]    (optional) amount of time in ms
                [span]     (optional) tuple
                [direction] (optional) direction [-1|1]

        """
        self.span = self.min, self.max = 20, 200
        self.rect = util.rect.create(center, size)
        self.period = 1600
        self.velocity = 0.33

    def reset(self):
        """Reset teleporter to [min] length."""
        tmp_center = self.rect.center
        self.rect.width = self.min
        self.rect.height = self.min
        self.rect.center = tmp_center

    def grow(self, dt):
        """Expand the teleporter."""
        tmp_center = self.rect.center
        self.rect.width += dt*self.velocity
        self.rect.height += dt*self.velocity
        # Check [max] bound
        if self.rect.width > self.max or self.rect.height > self.max:
            self.rect.width = self.max
            self.rect.height = self.max
        self.rect.center = tmp_center

    def shrink(self, dt):
        """Contract the teleporter."""
        tmp_center = self.rect.center
        self.rect.width -= dt*self.velocity
        self.rect.height -= dt*self.velocity
        # Check [min] bound
        if self.rect.width < self.min or self.rect.height < self.min:
            self.rect.width = self.min
            self.rect.height = self.min
        self.rect.center = tmp_center

    def calculate_length(self, t):
        """
        Calculate oscillatory length based on time [t].

            Parameters:
                [t] time in ms

        """
        min_l, max_l = self.span
        return abs(
            (max_l-min_l) * math.sin(2*math.pi*t/self.period + math.pi/4.0)
            + min_l
        )

    def update(self, t, center):
        """
        Resize [rect] according to elapsed time.

            Parameters:
                [t] time in ms
                [center] center of player to center the teleporter around

        """
        # Resize [rect]
        # length = self.calculate_length(t)
        # self.rect.width = length
        # self.rect.height = length

        # Re-center [rect]
        self.rect.center = center

    def draw(self, surface):
        """Draw self to the [surface]."""
        stroke_width = 1
        pygame.draw.circle(surface, view.Color.blue, self.rect.center,
                           int(self.rect.width/2.0), stroke_width)
        # pygame.draw.rect(surface, view.Color.blue, self.rect, stroke_width)


class DecayingTeleporter:
    """A decaying teleporter left behind after the player moves."""

    def __init__(self, teleporter):
        """Create new decaying teleporter."""
        self.rect = pygame.Rect(teleporter.rect.topleft, teleporter.rect.size)
        self.decay_time = 100
        self.timer = 0

    def draw(self, surface):
        """Draw self to the [surface]."""
        # alpha = int(255.0 * (1.0 - float(self.timer)/self.decay_time))
        # stroke_color = pygame.Color(0, 0, 255, alpha)
        stroke_width = 1
        # pygame.draw.rect(surface, view.Color.blue, self.rect, stroke_width)
        pygame.draw.circle(surface, view.Color.blue, self.rect.center,
                           int(self.rect.width/2.0), stroke_width)


class Player:
    """
    Main player in the game.

        Attributes:
            [rect]       Rect object
            [teleporter] Teleporter object

    """

    def __init__(self, center, size):
        """
        Create new Player.

            Parameters:
                [center] tuple (x, y)
                [size]   tuple (width, height)

        """
        self.rect = util.rect.create(center, size)
        self.teleporter = Teleporter(center, size)

    def move(self, vec):
        """
        Move player in direction the [vec] vector points.

            Parameters:
                [vec] ([-1|0|1], [-1|0|1]) direction to move player (x, y)

        """
        x, y = vec
        # Move player
        width = self.teleporter.rect.width
        height = self.teleporter.rect.height
        self.rect.move_ip(x*width/2.0, y*height/2.0)
        if x != 0 or y != 0:
            self.teleporter.reset()
        # Update teleporter center
        self.teleporter.rect.center = self.rect.center

    def update(self, dt):
        """
        Update teleporter.

            Parameters:
                [dt] elapsed time in ms

        """
        self.teleporter.update(dt, self.rect.center)

    def draw(self, surface):
        """Draw self on the [surface]."""
        # pygame.draw.rect(surface, view.Color.black, self.rect)
        pygame.draw.circle(surface, view.Color.black, self.rect.center,
                           int(self.rect.width/2.0))
        self.teleporter.draw(surface)


class Projectile:
    """Base class for a projectile."""

    def __init__(self, center, size, velocity):
        """Create new Projectile."""
        self.rect = util.rect.create(center, size)
        self.velocity = velocity

    def update(self, dt):
        """Update bullet position by [velocity] over time [dt]."""
        dx, dy = util.vector.multiply_scalar(dt, self.velocity)
        self.rect.move_ip(dx, dy)

    def draw(self, surface):
        """Draw self on the [surface]."""
        pygame.draw.rect(surface, view.Color.red, self.rect)


class Enemy:
    """Base class for an enemy."""

    def __init__(self, center, size, cooldown=1600):
        """
        Create new Enemy.

            Parameters:
                [center]   tuple (x, y)
                [size]     tuple (width, height)
                [cooldown] time between shots

        """
        self.rect = util.rect.create(center, size)
        self.cooldown = cooldown
        self.timer = 0
        self.projectiles = []

    def update(self, dt):
        """
        Update Enemy.

            Parameters:
                [dt] elapsed time in ms

        """
        # Update timer - TODO: make all this logic in a controller later
        self.timer += dt

    def fire_projectile(self, target, speed=0.2):
        """
        Fire a projectile at the [target] with [speed].

            Parameters:
                [target] tuple (x, y) coordinates the projectile is aiming at
                [speed] optional projectile speed

        """
        p_size = util.vector.divide_scalar(2.0, self.rect.size)
        p_velocity = util.vector.multiply_scalar(
            speed,
            util.vector.normalize(
                util.vector.subtract(target, self.rect.center)
            )
        )
        # Create and append
        projectile = Projectile(self.rect.center, p_size, p_velocity)
        # Reset [timer]
        self.timer = 0
        # Return projectile
        self.projectiles.append(projectile)
        return projectile

    def draw(self, surface):
        """Draw self on the [surface]."""
        pygame.draw.rect(surface, view.Color.red, self.rect)
        # draw cooldown indicator
        frac = float(self.timer) / float(self.cooldown)
        radius = self.rect.width/2.0 + 1.5 * self.rect.width * (1.0 - frac)
        if radius < 1:
            radius = 1
        cooldown_rect = pygame.Rect((0, 0), (2*radius, 2*radius))
        cooldown_rect.center = self.rect.center
        pygame.draw.rect(surface, view.Color.red, cooldown_rect, 1)
