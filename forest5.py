import pyxel
import math

PLAYER_VEL = 2

class Player:
    ANIMATION_DELAY = 5
    GRAVITY = 1

    def __init__(self):
        self.x = 0
        self.y = 70
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.scroll_area_width = 48
        self.offset_x = 0
        self.get_tile = lambda x, y: pyxel.tilemap(0).pget(x, y)
    
    def jump(self):
        self.y_vel = self.GRAVITY * -3
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
    
    def move(self, x, y, dx, dy):
        x += dx
        y += dy
        return x, y

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
    
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def handle_vertical_collision(self, dy):
        player_left = int(self.x // 8)
        player_right = int((self.x + 7) // 8)
        player_top = int(self.y // 8)
        player_bottom = int((self.y + 7) // 8)

        if self.fall_count > 0:
            for xi in range(player_left, player_right + 1):
                for yi in range(player_top, player_bottom + 1):
                    if self.get_tile(xi, yi)[1] >= 16:
                        if dy > 0: #ここに and self.fall_count > 0.5 を加えたらいいのではないか
                            self.y = (yi - 1) * 8
                            self.landed()
                            print("FLOOR: " +str((yi - 1) * 8))
                        elif dy < 0:
                            self.y = (yi + 1) * 8
                            self.hit_head()
                            print("HEAD : " + str(yi))
    
    def detect_horizontal_collision(self, dx):
        x, y = self.move(self.x, self.y, dx, 0)
        player_left = int(x // 8)
        player_right = int((x + 7) // 8)
        player_top = int(y // 8)
        player_bottom = int((y + 7) // 8)

        for xi in range(player_left, player_right + 1):
            for yi in range(player_top, player_bottom + 1):
                if self.get_tile(xi, yi)[1] >= 16:
                    return True

    def handle_move(self):
        self.x_vel = 0
        collide_left = self.detect_horizontal_collision(-PLAYER_VEL)
        collide_right = self.detect_horizontal_collision(PLAYER_VEL)

        if pyxel.btn(pyxel.KEY_LEFT) and not collide_left:
            self.move_left(PLAYER_VEL)
        if pyxel.btn(pyxel.KEY_RIGHT) and not collide_right:
            self.move_right(PLAYER_VEL) 
        if pyxel.btnp(pyxel.KEY_Z) and self.jump_count < 2:
            self.jump()

        self.handle_vertical_collision(self.y_vel)
    
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.y_vel = 0

    def update(self):
        self.y_vel += min(1, (self.fall_count / 30) * self.GRAVITY) #30fpsなので、1秒間で1に最大速度に達する
        self.x, self.y = self.move(self.x, self.y, self.x_vel, self.y_vel)

        if ((self.x - self.offset_x >= pyxel.width - self.scroll_area_width) and self.x_vel > 0) or (
            (self.x - self.offset_x <= self.scroll_area_width) and self.x_vel < 0):
            self.offset_x += self.x_vel

        self.fall_count += 1

    def draw(self):
        u = (2 if self.y_vel > self.GRAVITY else pyxel.frame_count // 10 % 2) * 8 #10フレームずつ0と1を交互に出力する
        #y_vel > 0 とした場合、接地時に毎フレームy_vel = 0.00001ぐらいになっているので、チラついてしまう
        w = 8 if self.direction == "right" else -8
        pyxel.blt(self.x - self.offset_x, self.y, 0, u, 0, w, 8, 0)
    
    def game_over(self):
        self.x = 0
        self.y = 70
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.scroll_area_width = 48
        self.offset_x = 0

    def detect_enemy_collision(self, enemy):
        start_x = math.cos(math.radians(enemy.start_angle))
        start_y = math.sin(math.radians(enemy.start_angle))
        end_x = math.cos(math.radians(enemy.end_angle))
        end_y = math.sin(math.radians(enemy.end_angle))

        for xi in range(self.x, self.x + 7 + 1):
            for yi in range(self.y, self.y + 7 + 1):
                distance_x = xi - enemy.center_x
                distance_y = yi - enemy.center_y

                if abs(self.player.x - enemy.x) < 6 and abs(self.player.y - enemy.y) < 6:
                    return True
                if distance_x ** 2 + distance_y ** 2 > enemy.radius ** 2:
                    return False
                if start_x * distance_y - distance_x * start_y < 0:
                    return False
                if end_x * distance_y - distance_x * end_y > 0:
                    return False
                else:
                    return True


class Stage:
    def __init__(self):
        self.selector_x = 0
        #128 * pyxel.rndi(0, 3)

    def update(self):
        pass

    def draw(self, offset):
        #pyxel.bltm(0, 0, 0, 0 + offset, 0, 128, 128)
        pyxel.bltm(0 - offset, 0, 0, self.selector_x, 0, 128, 128)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.center_x = self.x + 3.5
        self.center_y = self.y + 3.5
        self.start_angle = 0
        self.end_angle = 0
        self.radius = pyxel.rndi(0, 96)

        self.direction = "left"
        self.is_alive = True
        self.animation_count = 0

    def update(self):
        pass

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 128, 16, 8, 8, 0)


class App:
    def __init__(self):
        pyxel.init(128, 128, fps = 30)
        pyxel.load("assets/forest3.pyxres")
        pyxel.image(0).rect(0, 16, 8, 16, 0)
        self.player = Player()
        self.stages = [Stage()]
        self.enemies = []
        #self.enemy_spawn(0, 127)
        self.get_tile = lambda x, y: pyxel.tilemap(0).pget(x, y)
        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update()
        self.player.handle_move()
        self.stages.append = Stage()

        #self.enemy_spawn()
        #for enemy in self.enemies:
        #    if self.player.detect_enemy_collision(enemy):
        #        self.player.game_over(enemy)
        #        self.enemies = []
        #        self.enemy_spawn(0, 127)
        #    enemy.update()
            #if enemy.x < scroll_x - 8 or enemy.x > scroll_x + 160 or enemy.y > 160:
            #    enemy.is_alive = False
        #self.cleanup()

        #if ((self.player.x - self.player.offset_x >= pyxel.width - self.player.scroll_area_width)
        #    and self.x_vel > 0):
        #    self.stages.append(Stage())

    def draw(self):
        pyxel.cls(6)
        for stage in self.stages:
            stage.draw(self.player.offset_x)
        self.player.draw()
        pyxel.text(8, 8, "Y_VEL: " + str(self.player.y_vel), 14)
        pyxel.text(8, 24, "GRAV: " + str(self.player.GRAVITY), 14)
        pyxel.text(8, 16, "X_VEL: " + str(self.player.x_vel), 14)
        pyxel.text(8, 32, "OFFSET: " + str(self.player.offset_x), 14)
        pyxel.text(64, 16, "X: " + str(self.player.x), 14)
        pyxel.text(64, 32, "Y: " + str(self.player.y), 14)
        pyxel.text(64, 8, "X: " + str(self.player.x - self.player.offset_x), 14)
        pyxel.text(64, 24, "FC: " + str(self.player.fall_count), 14)

    def enemy_spawn(self):
        newarea_x = pyxel.width + self.player.offset_x
        #left_x = pyxel.ceil((newarea_x)) / 8)
        #right_x = pyxel.floor((self.player.offset_x + 7) / 8)
        #for x in range(left_x, right_x + 1):
        #    for y in range(16):
        #        if self.get_tile(x, y) == (0, 2):
        #            self.enemies.append = Enemy(x * 8, y * 8)
    
    def cleanup(self):
        pass

App()