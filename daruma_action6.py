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
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.scroll_area_width = 48
        self.offset_x = 0
        self.modified_x = 0
        self.score = 0
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
        x, y = self.move(self.modified_x, self.y, dx, 0)
        player_left = int(x // 8)
        player_right = int((x + 7) // 8)
        player_top = int(y // 8)
        player_bottom = int((y + 7) // 8)

        if self.x == self.offset_x and dx < 0:
            return True

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
        if pyxel.btnp(pyxel.KEY_Z) and self.jump_count < 2:
            self.jump()

        self.handle_vertical_collision(self.y_vel)
    
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.y_vel = 0
        self.jump_count = 2 #天井にあたったら2段目のジャンプは不可能になる

    def update(self, idlist):
        last_x = self.x
        self.y_vel += min(1, (self.fall_count / 30) * self.GRAVITY) #30fpsなので、1秒間で1に最大速度に達する
        self.x, self.y = self.move(self.x, self.y, self.x_vel, self.y_vel)
        
        if (self.x - self.offset_x >= pyxel.width - self.scroll_area_width) and self.x_vel > 0:
            self.offset_x += self.x_vel

        if self.x % 128 == 0 and self.x != 0:
            if self.x_vel > 0:
                self.modified_x = idlist[1] * 128 - self.x_vel
            if self.x_vel < 0:
                self.modified_x = (idlist[0] * 128 + 127) + self.x_vel
        self.modified_x, _ = self.move(self.modified_x, self.y, self.x_vel, self.y_vel)

        self.fall_count += 1

        if last_x < self.x:
            self.score =  "SCORE {:>4}".format(self.x)

    def draw(self):
        u = (2 if self.y_vel > self.GRAVITY else pyxel.frame_count // 10 % 2) * 8 #10フレームずつ0と1を交互に出力する
        #y_vel > 0 とした場合、接地時に毎フレームy_vel = 0.00001ぐらいになっているので、チラついてしまう
        w = 8 if self.direction == "right" else -8
        pyxel.blt(self.x, self.y, 0, u, 0, w, 8, 2)

    def detect_enemy_collision(self, enemy):
        a = (enemy.a_x, enemy.a_y)
        b = (enemy.b_x, enemy.b_y)
        c = (enemy.vertex_x, enemy.vertex_y)
        vec = lambda a, b: (a[0] - b[0], a[1] - b[1])
        corners_x = [self.x, self.x + 7]
        corners_y = [self.y, self.y + 7]
        
        if enemy.powered == True:
            for xi in corners_x:
                for yi in corners_y:
                    p = (xi, yi) 

                    ab = vec(b, a)
                    bp = vec(p, b)

                    bc = vec(c, b)
                    cp = vec(p, c)

                    ca = vec(a, c)
                    ap = vec(p, a)

                    c1 = ab[0] * bp[1] - ab[1] * bp[0]
                    c2 = bc[0] * cp[1] - bc[1] * cp[0]
                    c3 = ca[0] * ap[1] - ca[1] * ap[0]

                    return (c1 >= 0 and c2 >= 0 and c3 >= 0) or (c1 <= 0 and c2 <= 0 and c3 <= 0)
        
        else:
            return False


class Stage:
    def __init__(self, id, count):
        self.x = count * 128 #計算領域上座標の指定
        self.selector_x = id * 128 #UV座標の指定

    def update(self):
        pass

    def draw(self):
        pyxel.bltm(self.x, 0, 0, self.selector_x, 0, 128, 128)


class Enemy1:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.vertex_x = self.x + 3.5
        self.vertex_y = self.y + 3.5
        self.a_x = x - 16
        self.b_x = x + 16 + 7
        self.a_y = y + 8 * 5 + 7
        self.b_y = y + 8 * 5 + 7

        self.timer = random.randrange(20, 61, 20)

        self.powered = False
        self.animation_count = 0

    def update(self):
        if (pyxel.frame_count // self.timer % 2) == 1: #30フレームずつ0と1を交互に出力する
            self.powered = True
            
        elif (pyxel.frame_count // self.timer % 2) == 0: #30フレームずつ0と1を交互に出力する
            self.powered = False

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 128, 0, 8, 8, 2)

        if self.powered == True:
            pyxel.tri(self.a_x, self.a_y, self.b_x, self.b_y, self.vertex_x, self.vertex_y, 10)

class Enemy2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.vertex_x = self.x + 3.5
        self.vertex_y = self.y + 3.5
        self.a_x = x + 16 + 7
        self.b_x = x - 16
        self.a_y = y - 8 * 5 + 7
        self.b_y = y - 8 * 5 + 7

        self.timer = random.randrange(20, 61, 20)

        self.powered = False
        self.animation_count = 0

    def update(self):
        if (pyxel.frame_count // self.timer % 2) == 1: #30フレームずつ0と1を交互に出力する
            self.powered = True
            
        elif (pyxel.frame_count // self.timer % 2) == 0: #30フレームずつ0と1を交互に出力する
            self.powered = False

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 136, 0, 8, 8, 2)

        if self.powered == True:
            pyxel.tri(self.a_x, self.a_y, self.b_x, self.b_y, self.vertex_x, self.vertex_y, 10)


class App:
    def __init__(self):
        pyxel.init(128, 128)
        pyxel.load("assets/daruma_action6.pyxres")
        pyxel.image(0).rect(0, 16, 8, 16, 0)
        pyxel.image(0).rect(8, 16, 8, 16, 0)
        self.player = Player()
        self.idlist = [0, 1] #初期値だが、2番目の'1'の値はダミーでステージ生成に利用されない
        self.stages_count = 0
        self.stages = [Stage(self.idlist[0], self.stages_count)]
        self.enemies = []
        self.is_generated = False
        self.get_tile = lambda x, y: pyxel.tilemap(0).pget(x, y)
        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update(self.idlist)
        self.player.handle_move()

        if (len(self.idlist) >= 2
            and self.player.x % 128 == 64
            and self.player.x != 0
            and self.player.x_vel > 0):
            self.idlist.append(pyxel.rndi(1, 4))
            del self.idlist[0]
            self.stages_count += 1
            self.stages.append(Stage(self.idlist[1], self.stages_count))
            self.enemy_spawn()
        
        while len(self.stages) > 2:
            del self.stages[0]
        
        if len(self.enemies) >= 6:
            del self.enemies[0:1]
            #敵は2体ずつ増えていく
            #敵が4体になったときに手前の2体を消すことは、今いるところの敵を消すことを意味する

        while len(self.idlist) > 2:
            del self.idlist[0]

        if self.player.y >= pyxel.height + 64:
            self.game_over()

        for enemy in self.enemies:
            if self.player.detect_enemy_collision(enemy):
                self.game_over()
        
        for enemy in self.enemies:
            enemy.update()

    def draw(self):
        pyxel.cls(6)
        pyxel.camera(self.player.offset_x, 0)
        for stage in self.stages:
            stage.draw()
        for enemy in self.enemies:
            enemy.draw()
        self.player.draw()

        #スコア表示
        pyxel.camera()
        pyxel.text(9, 8, str(self.player.score), 1)
        pyxel.text(8, 8, str(self.player.score), 7)

    def enemy_spawn(self):
        left_x = (self.idlist[1] * 128) // 8
        right_x = (self.idlist[1] * 128 + 127) // 8
        for x in range(left_x, right_x + 1):
            for y in range(16):
                if self.get_tile(x, y) == (0, 2):
                    adjuster = self.idlist[1] * -16 + self.stages_count * 16
                    self.enemies.append(Enemy1((x + adjuster) * 8, y * 8))
                    #print(str((x + adjuster) * 8) + ", " + str(y))
                if self.get_tile(x, y) == (1, 2):
                    adjuster = self.idlist[1] * -16 + self.stages_count * 16
                    self.enemies.append(Enemy2((x + adjuster) * 8, y * 8))
    
    def game_over(self):
        pyxel.image(0).rect(0, 16, 8, 16, 0)
        self.player = Player()
        self.idlist = [0, 1]
        self.stages_count = 0
        self.stages = [Stage(self.idlist[0], self.stages_count)]
        self.enemies = []
        self.is_generated = False


App()