import pygame
import random
import pickle
import sys
import os

pygame.init()

# Kích thước màn hình
screen_width = 1000
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

clock = pygame.time.Clock()

pygame.display.set_caption("Bắn UFO")

if len(sys.argv) > 1:
    player_name = sys.argv[1]
# player_name = 'player1'

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

moreDamage = False

shieldE = False
cooldown = 0
cooldowned = 100
score = 0
boss_alive = False
pause_game = False
running = True

# hinh nen
background = pygame.image.load('img/bg.jpeg')
background = pygame.transform.scale(background, (800, 800))
# Lấy kích thước hình nền
background_width, background_height = background.get_size()
# Thiết lập vị trí ban đầu của hình nền
bg_y1 = 0
bg_y2 = -background_height + 200
# Thiết lập tốc độ di chuyển
scroll_speed = 2

dangerous = pygame.image.load('img/dangerous.png')
dangerous = pygame.transform.scale(dangerous, (400, 300))

bullet_img = pygame.image.load('img/bullet.png')
bullet_img = pygame.transform.scale(bullet_img, (15, 20))

# VE SHIELD PLAYER
img_energyShield = pygame.image.load(f'img/energy_shield.png') 
img_energyShield = pygame.transform.scale(img_energyShield, (200, 150))

# VE SHIELD ENEMY
img_energyShield1 = pygame.image.load(f'img/energy1_shield.png') 
img_energyShield1 = pygame.transform.scale(img_energyShield1, (200, 150))

# AM THANH
soundDangerous = pygame.mixer.Sound("sound/tieng-coi-canh-bao-www (mp3cut.net).mp3")
soundDangerous.set_volume(0.1) 
soundBG = pygame.mixer.Sound("sound/8bit-music-for-game-68698.mp3")
soundBG.set_volume(0.5)
soundTakeBuff = pygame.mixer.Sound("sound/take-buff-buy_1.mp3")
soundTakeBuff.set_volume(0.5) 
soundBullletHit = pygame.mixer.Sound("sound/bullethit.mp3")
soundBullletHit.set_volume(0.5) 
playerhit = pygame.mixer.Sound("sound/player.mp3")
playerhit.set_volume(0.5) 

class Bullet:
    def __init__(self, x, y, img):
        self.image = img
        self.rect = self.image.get_rect(center=(x, y))
    
    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def move(self, vel):
        self.rect.y += vel

    def off_screen(self, height):
        return not(self.rect.y <= height + 100 and self.rect.y >= 0)

    def collision(self, obj):
        return self.rect.colliderect(obj.rect)

class Character:
    def __init__(self, hp, shield, x, y, speed, width, height, image):
        self.index_image = 0  
        self.images = image 
        self.image = self.images[self.index_image]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.hp = hp
        self.shield = shield
        self.x = x
        self.y = y
        self.speed = speed
        self.width = width
        self.height = height
        self.bullets = []
        self.shoot_delay = 30
        self.shoot_counter = 0
        self.bullet_img = bullet_img
    
    def animation(self):
        self.index_image += self.speed
        if int(self.index_image) >= len(self.images):
            self.index_image = 0
        self.image = self.images[int(self.index_image)]
        self.rect.topleft = (self.x, self.y)
    
    def draw(self, screen):
        if self.rect.x < screen_width - 200:
            screen.blit(self.image, self.rect.topleft)
            for bullet in self.bullets:
                bullet.draw(screen)

    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()

    def move_bullets(self, vel, objs):
        global score, moreDamage
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(screen_height):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        if obj.shield > 0:
                            obj.shield -= 1
                            print("co shield")
                        else:  # Check if shield is now zero or less
                            if moreDamage and (objs == enemies or obj == boss):
                                obj.hp -= 3
                                print("ko co shield")
                            else:
                                obj.hp -= 1
                                print("ko co shield")
                        
                        soundBullletHit.play()
                        if(obj.hp <= 0):
                            score += 1
                            print("a")
                            objs.remove(obj)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)


# PLAYER
class Player(Character):
    def __init__(self, hp, shield, x, y, speed, width, height, image):
        super().__init__(hp, shield, x, y, speed, width, height, image)
        self.diagonal_shooting = False
        
    def move_bullets(self, vel, objs):
        super().move_bullets(vel, objs)
    
    def shoot(self):
        if self.shoot_counter == 0:
            if self.diagonal_shooting:
                bullet_left = DiagonalBullet(self.rect.centerx, self.rect.top, pygame.transform.rotate(bullet_img, -30), -1)
                bullet_right = DiagonalBullet(self.rect.centerx, self.rect.top, pygame.transform.rotate(bullet_img, 30), 1)
                bullet_middle = Bullet(self.rect.centerx, self.rect.top, self.bullet_img)
                self.bullets.append(bullet_left)
                self.bullets.append(bullet_right)
                self.bullets.append(bullet_middle)
            else:
                bullet = Bullet(self.rect.centerx, self.rect.top, self.bullet_img)
                self.bullets.append(bullet)
            self.shoot_counter = self.shoot_delay
        else:
            self.shoot_counter -= 1
    
    def draw(self, screen):
        super().draw(screen)
        if self.shield > 0:
            screen.blit(img_energyShield, (self.x - 75, self.y - 45), (0, 0, self.width + 100, self.height + 150))

imagesPlayer = []
for i in range(1, 4):
    img = pygame.image.load(f'img/player{i}.png') 
    img = pygame.transform.scale(img, (50, 50))
    imagesPlayer.append(img)

player = Player(3, 1, 380, 500, 2, 50, 50, imagesPlayer)

# ENEMY
class Enemy(Character):
    def __init__(self, hp, shield, x, y, speed, width, height, image):
        super().__init__(hp, shield, x, y, speed, width, height, image)
        self.bullet_img = pygame.transform.flip(self.bullet_img, True, False)
        self.shoot_delay = 120
    
    def move(self, vel):
        self.y += vel
        if(self.y == screen_height):
            self.x = random.randrange(0, screen_width - self.width)
            self.y = -100

    def shoot(self):
        if self.shoot_counter == 0:
            bullet = Bullet(self.rect.centerx, self.rect.bottom, self.bullet_img)
            self.bullets.append(bullet)
            self.shoot_counter = self.shoot_delay
        else:
            self.shoot_counter -= 1
    
    def draw(self, screen):
        super().draw(screen)
        if self.shield > 0:
            screen.blit(img_energyShield1, (self.x - 75, self.y - 45), (0, 0, self.width + 100, self.height + 100))


# ENEMY
imagesEnemy = []
for i in range(1, 6):
    img = pygame.image.load(f'img/enemy{i}.png') 
    img = pygame.transform.scale(img, (50, 50))
    imagesEnemy.append(img)
enemies = []

imagesBoss = []
for i in range(1, 7):
    img = pygame.image.load(f'img/boss{i}.png') 
    img = pygame.transform.scale(img, (100, 50))
    imagesBoss.append(img)

imagesBoss2 = []
for i in range(7, 16):
    img = pygame.image.load(f'img/boss{i}.png') 
    img = pygame.transform.scale(img, (100, 50))
    imagesBoss2.append(img)

class Boss(Character):
    def __init__(self, hp, shield, x, y, speed, width, height, image):
        super().__init__(hp, shield, x, y, speed, width, height, image)
        self.max_health = hp  # Set hp cho player
        self.direction_x = 1  # 1 để di chuyển sang phải, -1 để di chuyển sang trái
        self.direction_y = 1  # 1 để di chuyển xuống dưới, -1 để di chuyển lên trên

    def move(self):
        # Di chuyển theo trục x
        if self.y > 50:
            self.x += self.speed * self.direction_x
            if self.x <= 0 or self.x >= (screen_width - self.width) - self.width:
                self.direction_x *= -1  # Đảo ngược hướng di chuyển khi chạm vào cạnh màn hình
            # Di chuyển theo trục y
            self.y += self.speed * self.direction_y
            if self.y <= 0 or self.y >= screen_height // 2:  # Giới hạn di chuyển của Boss ở nửa trên màn hình
                self.direction_y *= -1  # Đảo ngược hướng di chuyển khi chạm vào cạnh màn hình
        else:
            self.y += self.speed
        self.rect.x = self.x
        self.rect.y = self.y
    
    def shoot2(self):
        if self.shoot_counter == 0:
            for _ in range(1):
                bullet_left = DiagonalBullet(self.rect.centerx - 50, self.rect.bottom, pygame.transform.rotate(bullet_img, 150), -1)
                bullet_right = DiagonalBullet(self.rect.centerx + 50, self.rect.bottom, pygame.transform.rotate(bullet_img, -150), 1)
                bullet_straight_left = Bullet(self.rect.centerx - 20, self.rect.bottom, self.bullet_img)
                bullet_straight_right = Bullet(self.rect.centerx + 20, self.rect.bottom, self.bullet_img)
                self.bullets.append(bullet_left)
                self.bullets.append(bullet_right)
                self.bullets.append(bullet_straight_left)
                self.bullets.append(bullet_straight_right)
            self.shoot_counter = self.shoot_delay
        else:
            self.shoot_counter -= 1
    
    def shoot(self):
        if self.shoot_counter == 0:
            for _ in range(1):
                bullet_straight_left = Bullet(self.rect.centerx - 20, self.rect.bottom, self.bullet_img)
                bullet_straight_right = Bullet(self.rect.centerx + 20, self.rect.bottom, self.bullet_img)
                self.bullets.append(bullet_straight_left)
                self.bullets.append(bullet_straight_right)
            self.shoot_counter = self.shoot_delay
        else:
            self.shoot_counter -= 1
    
    def move_bullets(self, vel, objs):
        bullets_to_remove = []

        for bullet in self.bullets[:]:  # Lặp qua một bản sao của self.bullets
            bullet.move(vel)  # Di chuyển viên đạn xuống dưới
            if bullet.off_screen(screen_height):
                bullets_to_remove.append(bullet)
            else:
                bullet_removed = False
                for obj in objs[:]:  # Lặp qua một bản sao của objs
                    if bullet.collision(obj):
                        if obj.shield <= 0:
                            obj.hp -= 1
                        else:
                            obj.shield -= 1
                        bullets_to_remove.append(bullet)
                        bullet_removed = True
                        if obj.hp <= 0:
                            objs.remove(obj)  # Xóa đối tượng nếu hết máu
                        break  # Thoát khỏi vòng lặp khi đã xử lý va chạm
                # Xóa viên đạn nếu đã va chạm với đối tượng
                if bullet_removed:
                    self.bullets.remove(bullet)

        # Xóa các viên đạn cần thiết sau khi hoàn thành vòng lặp
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)

    def draw(self, screen):
        super().draw(screen)
        self.healthbar(screen)
    
    def healthbar(self, window):
        health_bar_width = self.rect.width
        health_bar_height = 10
        health_bar_x = self.rect.x
        health_bar_y = self.rect.y + self.rect.height - 65
        # Draw red background
        pygame.draw.rect(window, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        # Draw green foreground
        health_ratio = self.hp / self.max_health
        pygame.draw.rect(window, (0, 255, 0), (health_bar_x, health_bar_y, health_bar_width * health_ratio, health_bar_height))
        
boss = Boss(10, 0, 400, -100, 0.2, 180, 150, imagesBoss)

boss2 = Boss(10, 0, 400, -100, 0.2, 180, 150, imagesBoss2)

def drawBossAppear():
    if (boss.y > -100 and boss.y < -50) or (boss2.y > -100 and boss2.y < -50):
        soundDangerous.play()
        screen.blit(dangerous, (200, 100))

def drawPause():
    screen.blit(dangerous, (200, 100))

class DiagonalBullet(Bullet):
    def __init__(self, x, y, img, direction):
        super().__init__(x, y, img)
        self.direction = direction

    def move(self, vel):
        self.rect.y += vel
        self.rect.x += self.direction * (vel // 2)

def collide(obj1, obj2):
    return obj1.rect.colliderect(obj2.rect)

imgShield = pygame.image.load(f'img/shield.png') 
imgShield = pygame.transform.scale(imgShield, (35, 35))

def draw_shields(x, y, shields):
    for i in range(shields):
        shield_x = x + i * (imgShield.get_width() + 2)
        screen.blit(imgShield, (shield_x, y))

heartImg = pygame.image.load('img/heart.png')
heartImg = pygame.transform.scale(heartImg, (25, 25))
def draw_lives(x, y, lives):
    for i in range(lives):
        heart_x = x + i * (heartImg.get_width() + 5)
        screen.blit(heartImg, (heart_x, y))


def draw_score(x, y, score):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Scores: {score}", True, WHITE)
    screen.blit(text, (x - 20, y))

def draw_dash(x, y, cooldown):
    # Trong phần khai báo
    font = pygame.font.SysFont(None, 24)  # Chọn font và kích thước văn bản
    if cooldown == 0:
        cooldown_text = font.render("Dash: Ready", True, WHITE)
    else:
        cooldown_text = font.render(f"Dash: {cooldown}", True, WHITE)
    screen.blit(cooldown_text, (x, y))


imgwasd =  pygame.image.load('img/wasd.png')
imgwasd = pygame.transform.scale(imgwasd, (150, 100))
def draw_tutorial():
    font = pygame.font.SysFont(None, 20)
    font1 = pygame.font.SysFont(None, 50)
    text1 = font1.render(f"TUTORIAL", True, WHITE)
    text6 = font.render(f"SPACE: DASH", True, WHITE)
    text7 = font.render(f"ENTER: SAVE GAME", True, WHITE)
    text8 = font.render(f"ESC: PAUSE/CONTINUE", True, WHITE)
    screen.blit(text1, (810, 20))
    screen.blit(imgwasd, (810, 70))
    screen.blit(text6, (810, 200))
    screen.blit(text7, (810, 250))
    screen.blit(text8, (810, 300))
# dem = 0
def spawn_enemy(score):
    global boss_alive, boss1, boss2, shieldE, imagesBoss
    if score == 0:
        number = 5
    elif score == 5:
        number = 0
        boss_alive = True
    elif score == 15:
        shieldE = True
        number = 10
    elif score == 25:
        number = 0
        boss_alive = True
    else:
        number = 5
    # enemy
    for i in range(number):
        if shieldE == True:
            if i % 5 == 0:
                enemy = Enemy(3, 1, random.randrange(0, screen_width - 400), random.randrange(-500, -50), 1, 180, 150, imagesEnemy)
            else:
                enemy = Enemy(3, 0, random.randrange(0, screen_width - 400), random.randrange(-500, -50), 1, 180, 150, imagesEnemy)
        else:
            enemy = Enemy(1, 0, random.randrange(0, screen_width - 400), random.randrange(-500, -50), 1, 180, 150, imagesEnemy)
        enemies.append(enemy)

buffArray = ['moreSpeed', 'moreLife', 'moreDamage', 'moreShield', 'moreBullet']

def display_buff_selection(selected_buffs):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 48)

    images = {
        'moreSpeed': pygame.image.load('img/moreSpeed.png'),
        'moreLife': pygame.image.load('img/moreLife.png'),
        'moreDamage': pygame.image.load('img/moreDamage.png'),
        'moreShield': pygame.image.load('img/moreShield.png'),
        'moreBullet': pygame.image.load('img/moreBullet.png')
    }

    # Scale images
    for key in images:
        images[key] = pygame.transform.scale(images[key], (150, 200))

    # Render the title text
    title_text_surf = font.render("Choose a Buff:", True, WHITE)
    title_text_rect = title_text_surf.get_rect(center=(screen_width // 2, 100))
    screen.blit(title_text_surf, title_text_rect)

    # Define the dimensions and positions for the three rectangles
    rect_width = 150
    rect_height = 200
    rect_spacing = (screen_width - 3 * rect_width) // 4
    y_position = 250

    rects = []

    # Draw the rectangles and blit the selected images
    for i, buff in enumerate(selected_buffs):
        rect_x = rect_spacing + i * (rect_width + rect_spacing)
        rect = pygame.Rect(rect_x, y_position, rect_width, rect_height)
        screen.blit(images[buff], rect.topleft)
        rects.append(rect)

    pygame.display.update()

    return rects

def select_buff():
    global moreDamage
    start_time = pygame.time.get_ticks()  # Start the timer

    selected_buffs = random.sample(buffArray, 3)
    rects = display_buff_selection(selected_buffs)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  # Get the mouse position
                soundTakeBuff.play()
                # Check if the mouse click is inside any of the rectangles
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mouse_pos):
                        if selected_buffs[i] == 'moreSpeed':
                            player.speed += 1
                            print("Selected Buff: More Speed")
                        elif selected_buffs[i] == 'moreLife':
                            player.hp += 1
                            print("Selected Buff: More Life")
                        elif selected_buffs[i] == 'moreDamage':
                            moreDamage = True
                            print("Selected Buff: More Damage")
                        elif selected_buffs[i] == 'moreBullet':
                            player.diagonal_shooting = True
                            print("Selected Buff: More Bullet")
                        elif selected_buffs[i] == 'moreShield':
                            player.shield +=1
                            print("Selected Buff: More Bullet")
                        buffArray.remove(selected_buffs[i])
                        return selected_buffs[i]

        # Check if 5 seconds have passed
        current_time = pygame.time.get_ticks()
        if current_time - start_time > 5000:
            print("Time's up! Auto-selecting the first buff")
            auto_selected_buff = selected_buffs[0]
            if auto_selected_buff == 'moreSpeed':
                player.speed += 0.5
            elif auto_selected_buff == 'moreLife':
                player.hp += 1
            elif auto_selected_buff == 'moreDamage':
                moreDamage = True
            elif auto_selected_buff == 'moreBullet':
                player.diagonal_shooting = True
            elif auto_selected_buff == 'moreshield':
                player.shield +=1
            print(f"Auto-selected Buff: {auto_selected_buff}")
            return auto_selected_buff

        pygame.time.delay(100)

def save_game(state, player_name):
    directory = 'inforPlayer'
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(os.path.join(directory, player_name + '.pkl'), 'wb') as f:
        pickle.dump(state, f)
    print(f"Game saved for player: {player_name}")

def load_game(player_name):
    filename = os.path.join('inforPlayer', player_name + '.pkl')
    try:
        with open(filename, 'rb') as f:
            global game_state
            game_state = pickle.load(f)
            if game_state.get('player_name') == player_name:
                return game_state
    except FileNotFoundError:
        print(f"No saved game found for player: {player_name}")
        return None
    return None

def reset_game(state):
    global player, score, boss_alive, enemies, boss, moreDamage

    player.hp = state['player']['hp']
    player.x = state['player']['x']
    player.y = state['player']['y']
    player.speed = state['player']['speed']
    player.width = state['player']['width']
    player.height = state['player']['height']
    player.shield = state['player']['shield']
    score = state['player']['score']
    player.bullets = [Bullet(x, y, player.bullet_img) for x, y in state['player']['bullets']]
    player.shoot_delay = state['player']['shoot_delay']
    player.diagonal_shooting = state['player']['diagonal_shooting']
    moreDamage = state['player']['moreDamage']

    enemies.clear()
    for enemy_data in state['enemies']:
        enemy = Enemy(
            enemy_data['hp'], enemy_data['shield'], enemy_data['x'], enemy_data['y'], enemy_data['speed'],
            enemy_data['width'], enemy_data['height'], imagesEnemy
        )
        enemy.bullets = [Bullet(x, y, enemy.bullet_img) for x, y in enemy_data['bullets']]
        enemies.append(enemy)

    boss.hp = state['boss']['hp']
    boss.x = state['boss']['x']
    boss.y = state['boss']['y']
    boss.speed = state['boss']['speed']
    boss.width = state['boss']['width']
    boss.height = state['boss']['height']
    boss.bullets = [Bullet(x, y, boss.bullet_img) for x, y in state['boss']['bullets']]
    boss_alive = state['boss']['alive']

saved_state = load_game(player_name)
if saved_state:
    reset_game(saved_state)

count = 1
textBuff = ''
soundBG.play()


def game_over():
    font = pygame.font.SysFont(None, 96)  # Create a font object
    text_surf = font.render("GAME OVER", True, WHITE)  # Render the "GAME OVER" text
    screen.blit(text_surf, (screen_width // 2 - 150, screen_height // 2 - 48))  # Blit the text onto the screen
    pygame.display.update()  # Update the display
    pygame.time.wait(2000)  # Wait for 2 seconds
    pygame.quit()  # Quit the game
    sys.exit()  # Exit the program


while running:

    screen.fill(BLACK)

        # Di chuyển hình nền
    bg_y1 += scroll_speed
    bg_y2 += scroll_speed

    # Reset vị trí khi hình nền đi ra khỏi màn hình
    if bg_y1 >= screen_height:
        bg_y1 = -background_height
    if bg_y2 >= screen_height:
        bg_y2 = -background_height

    # Vẽ hình nền
    screen.blit(background, (0, bg_y1))
    screen.blit(background, (0, bg_y2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC key pressed
                pause_game = True
            if event.key == pygame.K_RETURN:
                if event.key == pygame.K_RETURN:
                    game_state = {
                        'player_name': player_name,
                        'player': {
                            'hp': player.hp,
                            'shield': player.shield,
                            'x': player.x,
                            'y': player.y,
                            'speed': player.speed,
                            'width': player.width,
                            'height': player.height,
                            'score': score,
                            'bullets': [(bullet.rect.x, bullet.rect.y) for bullet in player.bullets],
                            'shoot_delay': player.shoot_delay,
                            'moreDamage': moreDamage,
                            'diagonal_shooting': player.diagonal_shooting
                        },
                        'enemies': [{
                            'hp': enemy.hp,
                            'shield': enemy.shield,
                            'x': enemy.x,
                            'y': enemy.y,
                            'speed': enemy.speed,
                            'width': enemy.width,
                            'height': enemy.height,
                            'bullets': [(bullet.rect.x, bullet.rect.y) for bullet in enemy.bullets]
                        } for enemy in enemies],
                        'boss': {
                            'hp': boss.hp,
                            'x': boss.x,
                            'y': boss.y,
                            'speed': boss.speed,
                            'width': boss.width,
                            'height': boss.height,
                            'bullets': [(bullet.rect.x, bullet.rect.y) for bullet in boss.bullets],
                            'alive': boss_alive
                        }
                    }
                save_game(game_state, player_name)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player.x - player.speed > 0: # left
        player.x -= player.speed * 2
    if keys[pygame.K_d] and player.x + player.speed < screen_width - 200 - player.width: # right
        player.x += player.speed * 2
    if keys[pygame.K_w] and player.y - player.speed > 0: # up
        player.y -= player.speed * 2
    if keys[pygame.K_s] and player.y + player.speed < screen_height - player.height: # down
        player.y += player.speed * 2
    if keys[pygame.K_SPACE] and cooldown == 0:
        if keys[pygame.K_a] and player.x - player.speed > 0: # left
            player.x -= player.speed * 100
        if keys[pygame.K_d] and player.x + player.speed < screen_width - 200 - player.width: # right
            player.x += player.speed * 100
        if keys[pygame.K_w] and player.y - player.speed > 0: # up
            player.y -= player.speed * 100
        if keys[pygame.K_s] and player.y + player.speed < screen_height - player.height: # down
            player.y += player.speed * 100
        cooldown = cooldowned
        
    if cooldown > 0:
        cooldown -= 1

    if cooldown == 0:
        player.speed = player.speed

    player.rect.topleft = (player.x, player.y)
    # Giới hạn trái phải trên dưới
    player.x = max(0, min(player.x, screen_width - 200 - player.width))
    player.y = max(0, min(player.y, screen_height - player.height))

    player.draw(screen)
    player.animation()
    player.move_bullets(-5, enemies)
    player.shoot()


    if not enemies:
        spawn_enemy(score)
    
    if boss_alive == True:
        # soundDangerous.play()
        
        if score == 5:
            drawBossAppear()
            boss.draw(screen)
            boss.animation()
            boss.move()
            boss.shoot()

            for bullet in player.bullets:
                if bullet.collision(boss):
                    boss.hp -= 1
                    soundBullletHit.play()
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
                        if boss.hp <= 0:
                            score += 10
                            boss_alive = False
                            selected_buff = select_buff()
                            if textBuff == '':
                                font = pygame.font.SysFont(None, 30)
                                textBuff = font.render(f"Buff: {selected_buff}", True, WHITE)
                            print(f"Buff {selected_buff} selected")

            #Xử lý va chạm giữa đạn của Boss và người chơi
            for bullet in boss.bullets[:]:
                if bullet.collision(player):
                    player.hp -= 1
                    playerhit.play()
                    boss.bullets.remove(bullet)
                    if player.hp <= 0:
                        running = False

            boss.move_bullets(2, [player])

        if score == 25:
            drawBossAppear()
            boss2.draw(screen)
            boss2.animation()
            boss2.move()
            boss2.shoot2()

            for bullet in player.bullets:
                if bullet.collision(boss2):
                    boss2.hp -= 1
                    soundBullletHit.play()
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
                        if boss2.hp <= 0:
                            score += 10
                            boss_alive = False
                            selected_buff = select_buff()
                            if textBuff == '':
                                font = pygame.font.SysFont(None, 30)
                                textBuff = font.render(f"Buff: {selected_buff}", True, WHITE)
                            print(f"Buff {selected_buff} selected")

            #Xử lý va chạm giữa đạn của Boss và người chơi
            for bullet in boss2.bullets[:]:
                if bullet.collision(player):
                    player.hp -= 1
                    playerhit.play()
                    boss2.bullets.remove(bullet)
                    if player.hp <= 0:
                        running = False

            # Vẽ và di chuyển đạn của Boss
            boss2.move_bullets(2, [player])
    
    for enemy in enemies:
        enemy.draw(screen)
        enemy.move(0.5)
        enemy.animation()
        enemy.move_bullets(5, [player])
        enemy.shoot()

        if collide(enemy, player):
            if player.shield <= 0:
                player.hp -= 1
            else:
                player.shield -= 1
            enemies.remove(enemy)

    if textBuff != '':
        if count <= 180:
            screen.blit(textBuff, (810, 350))
            count +=1
        else:
            textBuff = ''
    
    draw_lives(10, 10, player.hp)
    draw_score(700, 10, score)
    draw_shields(10, 50, player.shield)
    draw_dash(10, 90, cooldown)
    draw_tutorial()
    
    if player.hp == 0:
        game_over()
        running = False

    while pause_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pause_game = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC key pressed again to unpause
                    pause_game = False
        # Display the "PAUSE" text on the screen
        font = pygame.font.SysFont(None, 96)  # Create a font object
        text_surf = font.render("PAUSE", True, WHITE)  # Render the "PAUSE" text
        screen.blit(text_surf, (screen_width // 2 - 100, screen_height // 2 - 48))  # Blit the text onto the screen
        pygame.display.update()  # Update the display
        clock.tick(60)

    pygame.display.update()
    clock.tick(60)


pygame.quit()