"""Controllers for the game."""

import pygame
import sys
import random
import model
import view


class GameController:
    """Main controller for the game."""

    def __init__(self):
        """Create game controller."""
        # Initialize pygame
        pygame.init()

        # Instance variables
        self.prev_time = 0
        self.dt = 0
        self.game_over = False
        self.game_view = view.GameView()
        self.player_controller = PlayerController(self.game_view.size)
        self.enemy_controller = EnemyController(self.game_view.size)
        self.collision_controller = CollisionController()
        self.input_controller = InputController()

        # Initialize pygame music
        # pygame.mixer.init()
        # pygame.mixer.music.load('assets/Cipher2.mp3')

    def start(self):
        """Start game."""
        # Start music
        # pygame.mixer.music.play()
        # Create player
        self.player_controller.reset_player()
        # Start gameplay loop
        self.gameplay_loop()

    def restart(self):
        """Restart the game."""
        self.input_controller.reset()
        self.player_controller.reset_player()
        self.enemy_controller.reset()
        self.collision_controller.reset()
        self.game_over = False
        # Reset timers
        self.prev_time = 0
        self.dt = 0

    def gameplay_loop(self):
        """Infinite gameplay loop."""
        while 1:
            # Update time variables
            time = pygame.time.get_ticks()
            self.dt = time - self.prev_time
            self.prev_time = time

            # Handle Inputs
            self.input_controller.handle_events(pygame.event.get())

            # Update
            if self.game_over:
                if self.input_controller.quit:
                    sys.exit()
                elif self.input_controller.restart:
                    self.restart()
            else:
                # Update player
                self.player_controller.update(self.dt,
                                              self.input_controller.move_vec,
                                              self.input_controller.hold)
                # Update enemies
                self.enemy_controller.update(self.dt,
                                             self.player_controller.player)

                # Handle collisions
                # Enemy collisions FIRST (destroy enemies)
                self.collision_controller.update_enemy(
                    self.player_controller.player,
                    self.enemy_controller.enemies
                )
                for enemy in self.collision_controller.enemy_collisions:
                    self.enemy_controller.enemies.remove(enemy)
                # Player collisions SECOND (see if player lost)
                self.collision_controller.update_player(
                    self.player_controller.player,
                    self.enemy_controller.enemies
                )
                if self.collision_controller.player_collisions != []:
                    self.game_over = True
                    continue

            # Draw
            self.game_view.draw(self.player_controller.player,
                                self.enemy_controller.enemies,
                                self.player_controller.decaying_teleporters)

    def out_of_bounds(self, rect):
        """Return if the [rect] is completely inside the the [game_view]."""
        return not self.game_view.screen.rect.contains(rect)


class InputController:
    """Control input state."""

    def __init__(self):
        """Create input controller."""
        self.reset()

    def reset(self):
        """Reset input state."""
        self.move_vec = [0, 0]  # [x, y]
        self.hold = False
        # self.grow = False
        # self.shrink = False
        self.restart = False
        self.quit = False

    def handle_events(self, events):
        """
        Handle game events for current iteration of the game loop.

            Parameters:
                [events] the events to process

        """
        # Reset movement state
        self.move_vec = [0, 0]
        self.restart = False
        self.quit = False
        # Read events
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.move_vec[1] = -1
                elif event.key == pygame.K_s:
                    self.move_vec[1] = 1
                elif event.key == pygame.K_a:
                    self.move_vec[0] = -1
                elif event.key == pygame.K_d:
                    self.move_vec[0] = 1
                elif event.key == pygame.K_SPACE:
                    self.hold = True
                # elif event.key == pygame.K_LEFT:
                #     self.shrink = True
                # elif event.key == pygame.K_RIGHT:
                #     self.grow = True
                elif event.key == pygame.K_r:
                    self.restart = True
                elif event.key == pygame.K_q:
                    self.quit = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.hold = False
            #     if event.key == pygame.K_LEFT:
            #         self.shrink = False
            #     if event.key == pygame.K_RIGHT:
            #         self.grow = False


class CollisionController:
    """Control collisions between all game objects."""

    def __init__(self):
        """Create collision controller."""
        self.player_collisions = []  # projectiles player collides with
        self.enemy_collisions = []  # enemies player's teleporter collides with

    def reset(self):
        """Reset collision controller."""
        self.player_collisions = []
        self.enemy_collisions = []

    def update_player(self, player, enemies):
        """Update and return player collision state."""
        self.player_collisions = []
        for enemy in enemies:
            i = player.rect.collidelist(enemy.projectiles)
            if i != -1:
                self.player_collisions.append(enemy.projectiles[i])
        return self.player_collisions

    def update_enemy(self, player, enemies):
        """Update and return enemy collision state."""
        # TODO: make sure player is taking out multiple enemies
        self.enemy_collisions = []
        i = player.teleporter.rect.collidelist(enemies)
        if i != -1:
            self.enemy_collisions.append(enemies[i])

    # def update(self, player, enemies):
    #     """Update collision state."""
    #     i = player.teleporter.rect.collidelist(enemies)
    #     if i != -1:
    #         self.enemy_collisions.append(enemies[i])
    #     for enemy in enemies:
    #         i = player.rect.collidelist(enemy.projectiles)
    #         if i != -1:
    #             self.player_collisions.append(enemy.projectiles[i])


class EnemyController:
    """Control enemy intelligence."""

    def __init__(self, game_view_size):
        """Create enemy controller."""
        self.spawn_cooldown_step = 400
        self.max_spawn_cooldown = 2400
        self.min_spawn_cooldown = 1600
        self.spawn_cooldown = self.max_spawn_cooldown
        self.spawn_timer = 0
        self.enemies = []
        self.enemy_size = (20, 20)
        self.game_view_size = game_view_size

    def reset(self):
        """Reset enemy controller."""
        self.spawn_cooldown = self.max_spawn_cooldown
        self.spawn_timer = 0
        self.enemies = []

    def update(self, dt, player):
        """Update enemy controller and decide what enemies should do."""
        # Spawn enemies
        self.spawn_timer += dt
        if self.spawn_timer > self.spawn_cooldown:
            self.spawn_enemy(player)
        # Enemy projectiles
        for enemy in self.enemies:
            enemy.timer += dt
            for projectile in enemy.projectiles:
                projectile.update(dt)
            if enemy.timer > enemy.cooldown:
                enemy.fire_projectile(player.rect.center)

    def spawn_enemy(self, player):  # TODO:
        """Randomly spawn an enemy and reset the timer for cooldown."""
        # Calculate player padding
        player_padding = 100
        player_padding_rect = pygame.Rect(
            (0, 0),
            (player.teleporter.rect.width+player_padding,
             player.teleporter.rect.height+player_padding))
        player_padding_rect.center = player.rect.center
        # Calculate boundary padding
        boundary_padding = 20
        game_view_rect = pygame.Rect((0, 0), self.game_view_size)
        enemy_center = self.random_position(game_view_rect, boundary_padding)
        enemy = model.Enemy(enemy_center, self.enemy_size)
        while player_padding_rect.colliderect(enemy.rect):
            enemy.rect.center = self.random_position(game_view_rect,
                                                     boundary_padding)
        self.enemies.append(enemy)
        # Reset cooldown timer
        self.spawn_timer = 0
        # Decrease spawn cooldown
        self.decrement_spawn_cooldown()

    def random_position(self, rect, padding=0):
        """Get random position in [rect]."""
        random_position = (
            random.uniform(padding, rect.width-padding),
            random.uniform(padding, rect.height-padding)
        )
        return random_position

    def decrement_spawn_cooldown(self):
        """Decrement the spawn cooldown time."""
        if self.spawn_cooldown > self.min_spawn_cooldown:
            self.spawn_cooldown -= self.spawn_cooldown_step


class PlayerController:
    """Control player & teleporter actions."""

    def __init__(self, game_view_size):
        """
        Create player controller.

            Parameters:
                [game_view_size] tuple (width, height) of the game view

        """
        # Instance variables
        self.game_view_size = width, height = game_view_size
        self.player_start_center = (
            width/2.0,
            height/2.0
        )
        self.player_size = (20, 20)
        self.player = None

    # def create_player(self):
    #     """Create player."""
    #     player = model.Player(player_start_center, player_size)

    def reset_player(self):
        """Reset player."""
        self.player = model.Player(self.player_start_center, self.player_size)
        self.decaying_teleporters = []

    def update(self, dt, move_vec, hold):
        """Update player."""
        # Move player
        if not (move_vec[0] == 0 and move_vec[1] == 0):
            self.decaying_teleporters.append(
                model.DecayingTeleporter(self.player.teleporter)
            )
            self.player.move(move_vec)
            self.keep_player_in_bounds(
                pygame.Rect((0, 0), self.game_view_size)
            )
        # Update teleporter
        if not hold:
            self.player.teleporter.grow(dt)
        # Update decaying teleporters
        for decaying_teleporter in self.decaying_teleporters:
            decaying_teleporter.timer += dt
            if decaying_teleporter.timer > decaying_teleporter.decay_time:
                self.decaying_teleporters.remove(decaying_teleporter)
            pass

    def keep_player_in_bounds(self, rect):
        """Keep the player in the [rect]."""
        if self.player.rect.top < 0:
            self.player.rect.move_ip(0, 0-self.player.rect.top)
        if self.player.rect.bottom > rect.height:
            self.player.rect.move_ip(0, rect.height-self.player.rect.bottom)
        if self.player.rect.left < 0:
            self.player.rect.move_ip(0-self.player.rect.left, 0)
        if self.player.rect.right > rect.width:
            self.player.rect.move_ip(rect.width-self.player.rect.right, 0)
