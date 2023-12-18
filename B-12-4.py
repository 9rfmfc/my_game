import pyxel

class Ball:
    #すべてのボールで共通するものをここに書く
    speed = 1
    r = 10
    color = 6

    def __init__(self):
        self.score_flags = True
        Ball.restart(Ball)
    
    def move(self):
        # 毎フレーム移動させるための部分
        self.x += self.vx * Ball.speed
        self.y += self.vy * Ball.speed

        # ボールが左右の壁に当たったときの処理
        if (self.x < 0 and self.vx < 0) or (self.x > 200 and self.vx > 0):
            self.vx *= -1

    def restart(self):
        self.x = pyxel.rndi(0, 199)
        self.y = 0
        angle = pyxel.rndi(30, 150)
        self.vx = pyxel.cos(angle)
        self.vy = pyxel.sin(angle)

class Pad:
    w = 40
    h = 5
    color = 14

    def __init__(self):
        self.x = 100
        self.y = 195
    
    def catch(self, ball):
        if ball.y > 195 and self.x - 20 <= ball.x <= self.x + 20 and ball.score_flags:
            return(True)
        if ball.y >= 200 and ball.score_flags:
            return(False)

class App:
    def __init__(self):
        self.score = 0
        self.fails = 0
        self.end_flag = False
        
        pyxel.init(200, 200)
        pyxel.sound(0).set(notes='A2C3', tones='TT', volumes='33', effects='NN', speed=10)
        pyxel.sound(1).set(notes='B1A1', tones='TT', volumes='33', effects='NN', speed=10)
        self.balls = [Ball()]
        self.pads = Pad()

        pyxel.run(self.update, self.draw)

    def update(self):
        if self.end_flag == True:
            return

        self.pads.x = pyxel.mouse_x

        for b in self.balls:
            b.move()

            # 1個のとき10点、2個のとき20点に到達したらボールを追加し速度をリセット
            if self.score >= len(self.balls) * 10:
                self.balls.append(Ball())
                Ball.speed = 1
            
            # パッドがボールを受け取ったときの処理
            if self.pads.catch(b):
                pyxel.play(0, 0)
                self.score += 1
                b.score_flags = False
            
            # パッドがボールを受け取れずに落下していったときの処理
            elif self.pads.catch(b) == False:
                pyxel.play(0, 1)
                self.fails += 1

            # ボールが画面外に落ちたときの処理
            if b.y >= 200:
                # 画面外に落ちたボール全部に対する処理（位置のリセットと加速）
                b.restart()
                Ball.speed += 1
                b.score_flags = True

            if self.fails == 10:
                self.end_flag = True

    def draw(self):
        if self.end_flag == True:
            pyxel.text(100, 100, "GAME OVER", 0)

        else:
            pyxel.cls(7)
            for b in self.balls:
                pyxel.circ(b.x, b.y, Ball.r, Ball.color)

            pyxel.rect(self.pads.x - 20, self.pads.y, Pad.w, Pad.h, Pad.color)
            pyxel.text(0, 0, "SCORE: " + str(self.score), 0)

App()