import tkinter as tk
import random

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        # increase the below value to increase the speed of ball
        self.speed = 8
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='white')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        # set the shape and position of paddle
        self.width = 80
        self.height = 10
        self.ball = None
        self.attached = False      # only move the ball with the paddle while attached
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball, attached=True):
        self.ball = ball
        self.attached = attached

    def release_ball(self):
        # stop moving the ball with the paddle (ball continues on its own)
        self.attached = False

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            # only move the ball along when it's attached to the paddle (pre-launch)
            if self.ball is not None and self.attached:
                self.ball.move(offset, 0)

    def set_width(self, width):
        self.width = width
        # Re-draw the paddle with new width
        coords = self.get_position()
        x_center = (coords[0] + coords[2]) / 2
        y_center = (coords[1] + coords[3]) / 2
        self.canvas.coords(self.item,
                           x_center - self.width / 2,
                           y_center - self.height / 2,
                           x_center + self.width / 2,
                           y_center + self.height / 2)


class Brick(GameObject):
    COLORS = {1: '#4535AA', 2: '#ED639E', 3: '#8FE1A2'}

    def __init__(self, canvas, x, y, hits, game=None):
        self.width = 75
        self.height = 20
        self.hits = hits
        self.game = game
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            # spawn a bonus with some probability
            if self.game is not None and random.random() < 0.25:
                cx = (self.get_position()[0] + self.get_position()[2]) * 0.5
                cy = (self.get_position()[1] + self.get_position()[3]) * 0.5
                effect = random.choice(['expand', 'multiball'])
                bonus = Bonus(self.canvas, cx, cy, effect, self.game)
                self.game.items[bonus.item] = bonus
                self.game.bonuses.append(bonus)
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Bonus(GameObject):
    def __init__(self, canvas, x, y, effect_type, game):
        self.width = 30
        self.height = 10
        self.effect_type = effect_type
        self.game = game
        self.speed = 5
        color = 'green' if effect_type == 'expand' else 'red'
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='bonus')
        super(Bonus, self).__init__(canvas, item)

    def update(self):
        self.move(0, self.speed)


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#D6D1F5',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.bonuses = []
        self.balls = []
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle
        # generate bricks using a named layout: 'grid','staggered','pyramid','checker','random'
        # use 'random' for a procedurally generated layout (increase rows if you want more)
        self.generate_bricks(layout='random', rows=5)
        # other options: 'grid','staggered','checker','random'
        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-20))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(20))

    def setup_game(self):
           self.add_ball()
           self.update_lives_text()
           self.text = self.draw_text(300, 200,
                                      'Press Enter to start')
           self.canvas.bind('<Return>', lambda _: self.start_game())

    def add_ball(self):
        for b in self.balls:
            b.delete()
        self.balls = []
        
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        ball = Ball(self.canvas, x, 310)
        self.balls.append(ball)
        # attach the new ball to the paddle until the player starts the game
        self.paddle.set_ball(ball, attached=True)

    def spawn_extra_ball(self):
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        ball = Ball(self.canvas, x, 310)
        ball.direction = [random.choice([-1, 1]), -1]
        self.balls.append(ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits, game=self)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<Return>')
        self.canvas.delete(self.text)
        # release the ball so it is no longer carried by the paddle
        self.paddle.release_ball()
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            for b in self.balls: b.speed = None
            self.draw_text(300, 200, 'You win! You the Breaker of Bricks.')
        else:
            balls_to_remove = []
            for ball in self.balls:
                if ball.get_position()[3] >= self.height:
                    ball.delete()
                    balls_to_remove.append(ball)
                else:
                    ball.update()
            
            for b in balls_to_remove:
                self.balls.remove(b)

            if len(self.balls) == 0:
                self.lives -= 1
                if self.lives < 0:
                    self.draw_text(300, 200, 'You Lose! Game Over!')
                else:
                    self.after(1000, self.setup_game)
            else:
                self.update_bonuses()
                self.after(50, self.game_loop)

    def update_bonuses(self):
        for bonus in self.bonuses:
            bonus.update()
            # Check collision with paddle
            paddle_coords = self.paddle.get_position()
            bonus_coords = bonus.get_position()
            if (bonus_coords[2] >= paddle_coords[0] and bonus_coords[0] <= paddle_coords[2] and
                bonus_coords[3] >= paddle_coords[1] and bonus_coords[1] <= paddle_coords[3]):
                self.activate_bonus(bonus)
                bonus.delete()
                self.bonuses.remove(bonus)
            elif bonus_coords[1] > self.height:
                bonus.delete()
                self.bonuses.remove(bonus)

    def activate_bonus(self, bonus):
        if bonus.effect_type == 'expand':
            self.paddle.set_width(120)
            self.after(10000, self.reset_paddle_width)
        elif bonus.effect_type == 'multiball':
            self.spawn_extra_ball()
            self.spawn_extra_ball()

    def reset_paddle_width(self):
        self.paddle.set_width(80)

    def check_collisions(self):
        for ball in self.balls:
            ball_coords = ball.get_position()
            items = self.canvas.find_overlapping(*ball_coords)
            objects = [self.items[x] for x in items if x in self.items]
            ball.collide(objects)

    def generate_bricks(self, layout='grid', rows=3, hits=1):
        """
        Create bricks in different arrangements.
        layout: 'grid', 'staggered', 'pyramid', 'checker', 'random'
        rows: number of rows to attempt (ignored by pyramid which controls its own rows)
        hits: default hit count for created bricks
        """
        brick_w = 75
        brick_h = 20
        margin = 5
        cols = int((self.width - 2 * margin) // brick_w)
        start_x = margin + brick_w / 2
        top_y = 50

        if layout == 'grid':
            for r in range(rows):
                y = top_y + r * (brick_h + 6)
                for c in range(cols):
                    x = start_x + c * brick_w
                    self.add_brick(x, y, hits)

        elif layout == 'staggered':
            for r in range(rows):
                y = top_y + r * (brick_h + 6)
                offset = (brick_w / 2) if (r % 2 == 1) else 0
                for c in range(cols):
                    x = start_x + c * brick_w + offset
                    # keep bricks on-screen
                    if x - brick_w/2 >= 0 and x + brick_w/2 <= self.width:
                        self.add_brick(x, y, hits)

        elif layout == 'pyramid':
            pyramid_rows = 5
            for r in range(pyramid_rows):
                count = cols - r * 2
                y = top_y + r * (brick_h + 6)
                row_width = count * brick_w
                x0 = (self.width - row_width) / 2 + brick_w / 2
                for i in range(count):
                    x = x0 + i * brick_w
                    self.add_brick(x, y, hits)

        elif layout == 'checker':
            for r in range(rows):
                y = top_y + r * (brick_h + 6)
                for c in range(cols):
                    if (r + c) % 2 == 0:
                        x = start_x + c * brick_w
                        self.add_brick(x, y, hits)

        elif layout == 'random':
            prob = 0.6  # probability a cell has a brick
            for r in range(rows):
                y = top_y + r * (brick_h + 6)
                for c in range(cols):
                    if random.random() < prob:
                        x = start_x + c * brick_w
                        self.add_brick(x, y, hits)

        else:
            # fallback to simple grid
            for r in range(rows):
                y = top_y + r * (brick_h + 6)
                for c in range(cols):
                    x = start_x + c * brick_w
                    self.add_brick(x, y, hits)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()