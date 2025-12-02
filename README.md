# GameBreaker

**GameBreaker** adalah permainan arcade klasik penghancur batu bata (brick breaker) yang dibangun menggunakan Python dan pustaka Tkinter. Tujuan permainan ini adalah menghancurkan semua batu bata di layar dengan memantulkan bola menggunakan paddle, tanpa membiarkan bola jatuh ke bawah layar.

## Fitur

*   **Paddle**: Pemain mengendalikan paddle di bagian bawah layar untuk memantulkan bola.
*   **Bola**: Bola memantul di sekitar layar, menghancurkan batu bata saat bertabrakan.
*   **Batu Bata (Bricks)**: Target yang harus dihancurkan. Batu bata memiliki warna berbeda berdasarkan ketahanannya.
*   **Bonus**:
    *   **Expand**: Melebarkan paddle untuk sementara waktu.
    *   **Multiball**: Memunculkan bola tambahan.
*   **Sistem Nyawa**: Pemain memiliki 3 nyawa. Permainan berakhir jika semua nyawa habis.
*   **Level Acak**: Susunan batu bata dapat diatur secara acak atau pola tertentu.

## Kontrol

*   **Panah Kiri (`<Left>`)**: Gerakkan paddle ke kiri.
*   **Panah Kanan (`<Right>`)**: Gerakkan paddle ke kanan.
*   **Enter (`<Return>`)**: Mulai permainan (melepaskan bola dari paddle).

## Screenshot Output

Berikut adalah tampilan antarmuka permainan GameBreaker:

### Tampilan Gameplay
![Gameplay Mockup](gameplay_mockup.png)
*Ilustrasi tampilan saat permainan berlangsung dengan paddle, bola, dan susunan batu bata.*

### Tampilan Game Over
![Game Over Mockup](game_over_mockup.png)
*Ilustrasi tampilan saat permainan berakhir (Game Over).*

## Cuplikan Kode (Code Snippets)

Berikut adalah beberapa bagian penting dari kode sumber `GameBreaker.py` untuk memahami logika permainan.

### 1. Class `Paddle` (Pengendali Pemain)
Class ini mengatur pergerakan paddle dan interaksinya dengan bola.

```python
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

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            # only move the ball along when it's attached to the paddle (pre-launch)
            if self.ball is not None and self.attached:
                self.ball.move(offset, 0)
```

### 2. Class `Ball` (Logika Bola)
Class ini mengatur pergerakan bola dan pantulan saat menabrak dinding.

```python
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
```

### 3. Logika Tabrakan (`check_collisions`)
Fungsi ini memeriksa apakah bola menabrak objek lain (batu bata atau paddle).

```python
    def check_collisions(self):
        for ball in self.balls:
            ball_coords = ball.get_position()
            items = self.canvas.find_overlapping(*ball_coords)
            objects = [self.items[x] for x in items if x in self.items]
            ball.collide(objects)
```

### 4. Logika Bonus (`Brick.hit` & `Game.activate_bonus`)
Bagian ini menangani kemunculan bonus saat balok hancur dan efek bonus tersebut.

```python
    # Di dalam class Brick
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

    # Di dalam class Game
    def activate_bonus(self, bonus):
        if bonus.effect_type == 'expand':
            self.paddle.set_width(120)
            self.after(10000, self.reset_paddle_width)
        elif bonus.effect_type == 'multiball':
            self.spawn_extra_ball()
            self.spawn_extra_ball()
```

### 5. Pola Balok (`Game.generate_bricks`)
Fungsi ini membuat susunan balok dengan berbagai pola (grid, staggered, pyramid, checker, random).

```python
    def generate_bricks(self, layout='grid', rows=3, hits=1):
        """
        Create bricks in different arrangements.
        layout: 'grid', 'staggered', 'pyramid', 'checker', 'random'
        """
        # ... (inisialisasi variabel) ...
        
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

        # ... (pola lainnya: pyramid, checker, random) ...
```

## Cara Menjalankan

1.  Pastikan Anda telah menginstal Python di komputer Anda.
2.  Pastikan pustaka `tkinter` sudah tersedia (biasanya sudah termasuk dalam instalasi standar Python).
3.  Jalankan file `GameBreaker.py` melalui terminal atau command prompt:

```bash
python GameBreaker.py
```

Selamat bermain!
