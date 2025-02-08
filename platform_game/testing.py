import pygame

class Game:
    def __init__(self):
        # General setup
        self.clock = pygame.time.Clock()
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("pygame project")
        icon = pygame.image.load('images/icon.png').convert_alpha()
        pygame.display.set_icon(icon)

        # Score setup
        self.score_timer = pygame.USEREVENT + 2
        pygame.time.set_timer(self.score_timer, 1300)
        self.score = 0
        self.score_font = pygame.font.Font('fonts/fontforgame.ttf', 20)
        self.score_text = self.score_font.render('score:' + f'{self.score}', True, 'White')
        self.score_rect = self.score_text.get_rect(topleft=(20, 10))

        self.gameplay = True

        # Background
        self.bg = pygame.image.load('images/bg.jpg').convert()
        self.bg = pygame.transform.scale(self.bg, (800, 600))
        self.bg_x = 0
        self.bg_sound = pygame.mixer.Sound('sounds/bgmusic.mp3')
        self.bg_sound.play()
        self.bg_sound.set_volume(0.5)

        # Player setup
        self.walk_right = [pygame.image.load('images/player_right.png'), pygame.image.load(
            'images/player_right_walk.png')]
        self.walk_left = [pygame.image.load('images/player_left.png'), pygame.image.load(
            'images/player_left_walk.png')]
        self.player_anim_count = 0
        self.player_x = 150
        self.player_y = 450
        self.is_jump = False
        self.jump_count = 8
        self.player_speed = 5
        self.move_direction = self.walk_right

        # Enemy setup
        self.enemy = pygame.image.load('images/ghost.png')
        self.enemy = pygame.transform.scale(self.enemy, (35, 35))
        self.enemy_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.enemy_timer, 3800)
        self.enemy_list_in_game = []

        # Restart setup
        self.lose_font = pygame.font.Font('fonts/fontforgame.ttf', 30)
        self.lose_text = self.lose_font.render('You Lose!', True, 'White')
        self.restart_text = self.lose_font.render('Restart?', True, 'Red')
        self.restart_text_rect = self.restart_text.get_rect(topleft=(347, 300))

        # Bullet setup
        self.bullet = pygame.image.load('images/bullets.png')
        self.bullets = []
        self.bullet_left = 3

        # Running flag
        self.running = True

    def update_score(self, points):
        self.score += points
        self.score_text = self.score_font.render('score:' + f'{self.score}', True, 'White')

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == self.enemy_timer:
                self.enemy_list_in_game.append(self.enemy.get_rect(topleft=(802, 445)))
            if self.gameplay and event.type == pygame.KEYUP and event.key == pygame.K_f and self.bullet_left > 0:
                self.bullets.append(self.bullet.get_rect(topleft=(self.player_x + 30, self.player_y + 10)))
                self.bullet_left -= 1
            if self.gameplay and event.type == self.score_timer:
                self.update_score(1)
                if self.score > 30:
                    self.bullet_left += 1
                    self.score -= 30
                    self.update_score(0)
        return True

    def update(self, keys):
        # Player movement
        if keys[pygame.K_LEFT] and self.player_x > 10:
            self.player_x -= self.player_speed
            self.move_direction = self.walk_left
        elif keys[pygame.K_RIGHT] and self.player_x < 700:
            self.player_x += self.player_speed
            self.move_direction = self.walk_right

        self.bg_x -= 5
        if self.bg_x == -800:
            self.bg_x = 0
        if not self.is_jump:
            if keys[pygame.K_SPACE]:
                self.is_jump = True
        else:
            if self.jump_count >= -8:
                if self.jump_count > 0:
                    self.player_y -= (self.jump_count ** 2) / 2
                else:
                    self.player_y += (self.jump_count ** 2) / 2
                self.jump_count -= 1
            else:
                self.is_jump = False
                self.jump_count = 8

        self.player_anim_count = (self.player_anim_count + 1) % 2

        if self.bullets:
            for (i, el) in enumerate(self.bullets):
                el.x += 4
                if el.x > 800:
                    self.bullets.pop(i)
                if self.enemy_list_in_game:
                    for (index, enemy_el) in enumerate(self.enemy_list_in_game):
                        if el.colliderect(enemy_el):
                            self.bullets.pop(i)
                            self.enemy_list_in_game.pop(index)
                            self.update_score(2)

        if self.enemy_list_in_game:
            for (i, el) in enumerate(self.enemy_list_in_game):
                el.x -= 10
                if el.x < -10:
                    self.enemy_list_in_game.pop(i)
                if self.walk_right[0].get_rect(topleft=(self.player_x, self.player_y)).colliderect(el):
                    self.gameplay = False

    def draw(self):
        self.screen.blit(self.bg, (self.bg_x, 0))
        self.screen.blit(self.bg, (self.bg_x + 800, 0))
        self.screen.blit(self.move_direction[self.player_anim_count], (self.player_x, self.player_y))
        self.screen.blit(self.score_text, self.score_rect)
        for el in self.enemy_list_in_game:
            self.screen.blit(self.enemy, el)
        for el in self.bullets:
            self.screen.blit(self.bullet, el)
        if not self.gameplay:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.lose_text, (340, 270))
            self.screen.blit(self.restart_text, self.restart_text_rect.topleft)
            mouse_pos = pygame.mouse.get_pos()
            if self.restart_text_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.reset_game()

    def reset_game(self):
        self.gameplay = True
        self.player_x = 150
        self.enemy_list_in_game.clear()
        self.bullets.clear()
        self.bullet_left = 3
        self.score = 0
        self.update_score(0)

    def run(self):
        while self.running:
            self.running = self.handle_events()
            keys = pygame.key.get_pressed()
            if self.gameplay:
                self.update(keys)
            self.draw()
            pygame.display.update()
            self.clock.tick(12)

if __name__ == "__main__":
    game = Game()
    game.run()
