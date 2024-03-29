import pyxel
import random

class Player:
    GRAVITY = 1
    PLAYER_VEL = 2

    def __init__(self):
        self.x = 0
        self.y = 70
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "right"
        self.fall_count = 0
        self.jump_count = 0
        self.scroll_area_width = 48
        self.offset_x = 0
        self.modified_x = 0
        self.score = 0
        self.get_tile = lambda x, y: pyxel.tilemap(0).pget(x, y)

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
    
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"

    def jump(self):
        self.y_vel = self.GRAVITY * -3
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.y_vel = 0
        self.jump_count = 2

    def handle_vertical_collision(self, dy):
        player_left = int(self.modified_x // 8)
        player_right = int((self.modified_x + 7) // 8)
        player_top = int(self.y // 8)
        player_bottom = int((self.y + 7) // 8)

        if self.fall_count > 0:
            for yi in range(player_top, player_bottom + 1):
                for xi in range(player_left, player_right + 1):
                    if self.get_tile(xi, yi)[1] >= 16:
                        if dy > 0:
                            self.y = (yi - 1) * 8
                            self.landed()
                        elif dy < 0:
                            self.y = (yi + 1) * 8
                            self.hit_head()
    
    def detect_horizontal_collision(self, dx):
        if self.x == self.offset_x and dx < 0:
            return True
        
        x = self.modified_x + dx
        player_left = int(x // 8)
        player_right = int((x + 7) // 8)
        player_top = int(self.y // 8)
        player_bottom = int((self.y + 7) // 8)

        for xi in range(player_left, player_right + 1):
            for yi in range(player_top, player_bottom + 1):
                if self.get_tile(xi, yi)[1] >= 16:
                    return True

    def handle_move(self):
        self.x_vel = 0
        collide_left = self.detect_horizontal_collision(-self.PLAYER_VEL)
        collide_right = self.detect_horizontal_collision(self.PLAYER_VEL)

        if pyxel.btn(pyxel.KEY_LEFT) and not collide_left:
            self.move_left(self.PLAYER_VEL)
        if pyxel.btn(pyxel.KEY_RIGHT) and not collide_right:
            self.move_right(self.PLAYER_VEL) 
        if ((pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_SPACE))
            and self.jump_count < 2):
            self.jump()

        self.handle_vertical_collision(self.y_vel)
        self.y_vel += min(1, (self.fall_count / 30) * self.GRAVITY) 

    def update(self, idlist):
        last_x = self.x
        self.x += self.x_vel
        self.y += self.y_vel
        
        if (self.x - self.offset_x >= pyxel.width - self.scroll_area_width) and self.x_vel > 0:
            self.offset_x += self.x_vel

        if self.x % 128 == 0 and self.x != 0:
            if self.direction == "right":
                self.modified_x = idlist[1] * 128 - self.x_vel
            else:
                self.modified_x = 128 + idlist[0] * 128 - self.x_vel

        self.modified_x += self.x_vel

        self.fall_count += 1

        if last_x < self.x and self.score < self.x:
            self.score = self.x

    def draw(self):
        u = (2 if self.y_vel > 0.5 else pyxel.frame_count // 10 % 2) * 8
        w = 8 if self.direction == "right" else -8
        pyxel.blt(self.x, self.y, 0, u, 0, w, 8, 2)

    def detect_enemy_collision(self, enemy):
        a = (enemy.a_x, enemy.a_y)
        b = (enemy.b_x, enemy.b_y)
        c = (enemy.vertex_x, enemy.vertex_y)
        p = (self.x + 3, self.y + 3) 
        vec = lambda a, b: (a[0] - b[0], a[1] - b[1])
        
        if enemy.is_powered == True:
            ab = vec(b, a)
            bp = vec(p, b)

            bc = vec(c, b)
            cp = vec(p, c)

            ca = vec(a, c)
            ap = vec(p, a)

            c1 = ab[0] * bp[1] - ab[1] * bp[0]
            c2 = bc[0] * cp[1] - bc[1] * cp[0]
            c3 = ca[0] * ap[1] - ca[1] * ap[0]

            if (c1 >= 0 and c2 >= 0 and c3 >= 0) or (c1 <= 0 and c2 <= 0 and c3 <= 0):
                return True

        else:
            return False


class Stage:
    def __init__(self, id, count):
        self.x = count * 128
        self.selector_x = id * 128

    def draw(self):
        pyxel.bltm(self.x, 0, 0, self.selector_x, 0, 128, 128)


class Enemy1:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = 0
        self.timer_u = 0

        self.vertex_x = self.x + 3.5
        self.vertex_y = self.y + 3.5
        self.a_x = x - 16
        self.b_x = x + 16 + 7
        self.a_y = y + 8 * 5 + 7
        self.b_y = y + 8 * 5 + 7

        self.timer = random.randrange(40, 121, 20)
        self.is_powered = False
        self.animation_count = 0
        self.frame_count = 0

    def update(self):
        self.frame_count += 1

        if (self.frame_count // self.timer % 2) == 1:
            self.is_powered = True
            self.animation_count = 0
            
        if (self.frame_count // self.timer % 2) == 0:
            self.is_powered = False
        
        if self.is_powered == False:
            self.animation_count += 1
        
        self.v = (self.frame_count // 10 % 2) * 8
        self.timer_u = (self.animation_count // (self.timer / 4)) * 8

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 128, self.v, 8, 8, 2)
        pyxel.blt(self.x - 8, self.y - 8, 0, 32 if self.is_powered else self.timer_u, 72, 8, 8, 2)

        if self.is_powered == True:
            pyxel.tri(self.a_x, self.a_y, self.b_x, self.b_y, self.vertex_x, self.vertex_y, 10)


class Enemy2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = 0
        self.timer_u = 0

        self.vertex_x = self.x + 3.5
        self.vertex_y = self.y + 3.5
        self.a_x = x + 16 + 7
        self.b_x = x - 16
        self.a_y = y - 8 * 5 + 7
        self.b_y = y - 8 * 5 + 7

        self.timer = random.randrange(40, 121, 20)
        self.is_powered = False
        self.animation_count = 0
        self.frame_count = 0

    def update(self):
        self.frame_count += 1

        if (self.frame_count // self.timer % 2) == 1:
            self.is_powered = True
            self.animation_count = 0
            
        if (self.frame_count // self.timer % 2) == 0:
            self.is_powered = False
        
        if self.is_powered == False:
            self.animation_count += 1
        
        self.v = (self.frame_count // 10 % 2) * 8
        self.timer_u = (self.animation_count // (self.timer / 4)) * 8

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 136, self.v, 8, 8, 2)
        pyxel.blt(self.x + 8, self.y + 8, 0, 32 if self.is_powered else self.timer_u, 72, 8, 8, 2)

        if self.is_powered == True:
            pyxel.tri(self.a_x, self.a_y, self.b_x, self.b_y, self.vertex_x, self.vertex_y, 10)


class App:
    def __init__(self):
        pyxel.init(128, 128)
        pyxel.load("assets/daruma_action7.pyxres")
        self.get_tile = lambda x, y: pyxel.tilemap(0).pget(x, y)
        pyxel.mouse(True)

        pyxel.image(0).rect(0, 16, 8, 16, 0)
        pyxel.image(0).rect(8, 16, 8, 16, 0)
        self.player = Player()
        self.idlist = [0, 0]
        self.stages_count = 0
        self.stages = [Stage(self.idlist[0], self.stages_count)]
        self.enemies = []
        self.last_border_x = 0
        self.is_pushed = False
        self.loop_limit = 0
        self.is_ended = False
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.is_ended == False:
            self.player.update(self.idlist)
            self.player.handle_move()

            if (len(self.idlist) >= 2
                and self.last_border_x != self.player.x
                and self.player.x % 128 == 64
                and self.player.x != 0
                and self.player.x_vel > 0):
                self.last_border_x = self.player.x
                self.idlist.append(pyxel.rndi(1, 5))
                del self.idlist[0]
                self.stages_count += 1
                self.stages.append(Stage(self.idlist[1], self.stages_count))
                self.enemy_spawn()
            
            if len(self.stages) > 2:
                del self.stages[0]
            if len(self.enemies) > 4:
                del self.enemies[0:1]
            if len(self.idlist) > 2:
                del self.idlist[0]
            
            if self.player.y >= pyxel.height + 64:
                self.is_ended = True

            for enemy in self.enemies:
                if self.is_pushed == False:
                    enemy.update()
                if self.player.detect_enemy_collision(enemy):
                    self.is_ended = True

            if (95 <= pyxel.mouse_x <= 110
                and 95 <= pyxel.mouse_y <= 110
                and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
                and self.is_pushed == False
                and self.loop_limit <= 60):
                    self.is_pushed = True
            if self.is_pushed == True:
                self.loop_limit += 1
                if self.loop_limit >= 60:
                    self.is_pushed = False
                    self.loop_limit = 0
        
        else:
            if pyxel.btn(pyxel.KEY_R):
                self.game_over()
            elif pyxel.btn(pyxel.KEY_Q):
                pyxel.quit()

    def draw(self):
        pyxel.cls(6)
        pyxel.camera(self.player.offset_x, 0)
        for stage in self.stages:
            stage.draw()
        for enemy in self.enemies:
            enemy.draw()
        self.player.draw()

        pyxel.camera()
        pyxel.text(9, 9, str("SCORE {:>4}".format(self.player.score)), 0)
        pyxel.text(9, 8, str("SCORE {:>4}".format(self.player.score)), 7)
        v = 16 + (self.loop_limit // 20 * 16)
        pyxel.blt(95, 95, 0, v if self.is_pushed == True else 0, 40, 16, 16)
        
        if self.is_ended == True:
            pyxel.text(46, 51, "GAME OVER", 0)
            pyxel.text(46, 50, "GAME OVER", 7)
            pyxel.text(28, 59, "PRESS R TO RESTART", 0)
            pyxel.text(28, 58, "PRESS R TO RESTART", 7)
            pyxel.text(28, 67, "PRESS Q TO Q U I T", 0)
            pyxel.text(28, 66, "PRESS Q TO Q U I T", 7)

    def enemy_spawn(self):
        left_x = self.idlist[1] * 16
        right_x = self.idlist[1] * 16 + 15
        adjuster = self.idlist[1] * -16 + self.stages_count * 16

        for x in range(left_x, right_x + 1):
            for y in range(16):
                if self.get_tile(x, y) == (0, 2):
                    self.enemies.append(Enemy1((x + adjuster) * 8, y * 8))
                if self.get_tile(x, y) == (1, 2):
                    self.enemies.append(Enemy2((x + adjuster) * 8, y * 8))
    
    def game_over(self):
        pyxel.image(0).rect(0, 16, 8, 16, 0)
        pyxel.image(0).rect(8, 16, 8, 16, 0)
        self.player = Player()
        self.idlist = [0, 0]
        self.stages_count = 0
        self.stages = [Stage(self.idlist[0], self.stages_count)]
        self.enemies = []
        self.last_border_x = 0
        self.is_pushed = False
        self.loop_limit = 0
        self.is_ended = False


App()