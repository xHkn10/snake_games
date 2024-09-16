import random
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

root: tk.Tk

WIDTH = 600
HEIGHT = 600
snake_head_bigger = 20
snake_body_bigger = 9
apple_bigger = 12
SQRS = 20
SQR_LEN = WIDTH / SQRS

BACKGROUND_COLOR = "#062E03"
GRIDDED: bool = True

SPEED = 200
ACCELERATION = 0.96  # should be in (0, 1]; the lesser the float, the faster the snake gets, 1 means no acceleration

curr_direction: str
score: int = 0

head_coords = [1, 1]  # x y
snake_coords = [head_coords]
rects = []

xs = (SQRS // 10) * [SQRS - x for x in range(SQRS // 10)]
ys = [y for y in range(1, SQRS // 10 + 1) for _ in range(SQRS // 10)]
score_board_coords = tuple(zip(xs, ys))

apple: int
apple_coords: list[int, int]

started: bool = False
just_ate_apple: bool = False


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        global root
        root = self

        self.resizable(False, False)
        self.geometry(f"{WIDTH + 3}x{HEIGHT + 3}")
        self.title("Snake Game")

        self.bg = Background(self)

        self.mainloop()


class Background(tk.Canvas):
    def __init__(self, master):
        super().__init__(master=master)

        self.pack(expand=True, fill=tk.BOTH)
        self.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BACKGROUND_COLOR)

        if GRIDDED:
            self.grid()

        self.binder()

        self.apple_img = ImageTk.PhotoImage(
            Image.open("bilg_apple.png").resize((int(SQR_LEN) + apple_bigger, int(SQR_LEN) + apple_bigger)))
        self.up_snake_img = ImageTk.PhotoImage(
            Image.open("up_snake.png").resize((int(SQR_LEN) + snake_head_bigger, int(SQR_LEN) + snake_head_bigger)))
        self.down_snake_img = ImageTk.PhotoImage(
            Image.open("down_snake.png").resize((int(SQR_LEN) + snake_head_bigger, int(SQR_LEN) + snake_head_bigger)))
        self.left_snake_img = ImageTk.PhotoImage(
            Image.open("left_snake.png").resize((int(SQR_LEN) + snake_head_bigger, int(SQR_LEN) + snake_head_bigger)))
        self.right_snake_img = ImageTk.PhotoImage(
            Image.open("right_snake.png").resize((int(SQR_LEN) + snake_head_bigger, int(SQR_LEN) + snake_head_bigger)))
        self.snake_imgs = {"Up": self.up_snake_img, "Down": self.down_snake_img,
                           "Left": self.left_snake_img, "Right": self.right_snake_img}
        self.snake_body_img = ImageTk.PhotoImage(
            Image.open("snake_body.png").resize((int(SQR_LEN) + snake_body_bigger, int(SQR_LEN) + snake_body_bigger)))

        self.scoreboard = Score(self, "0")

        self.head = self.create_image(SQR_LEN / 2, SQR_LEN / 2, image=self.right_snake_img)
        rects.append(self.head)
        apple_gen(self)

    def grid(self):
        for i in range(SQRS + 1):
            self.create_line((i * SQR_LEN, 10, i * SQR_LEN, HEIGHT), fill="#012107")
        for i in range(SQRS + 1):
            self.create_line((10, i * SQR_LEN, WIDTH, i * SQR_LEN), fill="#012107")

    def binder(self):
        root.bind("<Up>", lambda event: key_press(event, self, self.head))
        root.bind("<Down>", lambda event: key_press(event, self, self.head))
        root.bind("<Left>", lambda event: key_press(event, self, self.head))
        root.bind("<Right>", lambda event: key_press(event, self, self.head))


class Score(tk.Label):
    def __init__(self, master, text):
        super().__init__(master=master, text=text, font=("Arial", 30, "bold"), width=3, height=1, bg="#87ceeb",
                         relief="raised", bd=2)
        self.place(x=WIDTH - 70, y=1)


def key_press(event: tk.Event, canvas: tk.Canvas, head: int):
    global curr_direction, started
    if event.keysym in ["Up", "Down", "Left", "Right"]:
        curr_direction = event.keysym
    if not started:
        move(canvas, head)
        started = True


def move(canvas: tk.Canvas, head: int):
    global just_ate_apple, SPEED, score, SQR_LEN
    directions = {"Up": [0, -1], "Down": [0, 1], "Left": [-1, 0], "Right": [1, 0]}

    canvas.move(head, directions[curr_direction][0] * SQR_LEN, directions[curr_direction][1] * SQR_LEN)

    for i in range(1, len(rects)):
        dx = (snake_coords[i - 1][0] - snake_coords[i][0]) * SQR_LEN
        dy = (snake_coords[i - 1][1] - snake_coords[i][1]) * SQR_LEN
        canvas.move(rects[i], dx, dy)

    if just_ate_apple:
        score += 1
        x0, y0 = snake_coords[-1][0] * SQR_LEN, snake_coords[-1][1] * SQR_LEN
        new_tail = canvas.create_image((2 * x0 - SQR_LEN) / 2, (2 * y0 - SQR_LEN) / 2, image=canvas.snake_body_img)
        rects.append(new_tail)
        snake_coords.append(snake_coords[-1].copy())
        just_ate_apple = False
        SPEED *= ACCELERATION
        canvas.scoreboard.config(text=str(score))

    for i in range(len(snake_coords) - 1, 0, -1):
        snake_coords[i] = snake_coords[i - 1].copy()

    head_coords[0] += directions[curr_direction][0]
    head_coords[1] += directions[curr_direction][1]
    canvas.itemconfig(head, image=canvas.snake_imgs[curr_direction])

    if apple_coords == head_coords:
        just_ate_apple = True
        canvas.delete(apple)
        apple_gen(canvas)

    if collision_occurred():
        messagebox.showinfo(title="Game OVER!", message=f"SCORE: {score}")
        root.destroy()
        return

    canvas.update()
    canvas.after(int(SPEED), lambda: move(canvas, head))


def apple_gen(canvas: tk.Canvas):
    global apple, apple_coords, SQR_LEN
    while True:
        rand_x, rand_y = random.randint(0, SQRS - 1), random.randint(0, SQRS - 1)
        if not ([rand_x + 1, rand_y + 1] in snake_coords or (rand_x + 1, rand_y + 1) in score_board_coords):
            break
    x0, y0 = rand_x * SQR_LEN, rand_y * SQR_LEN
    x1, y1 = x0 + SQR_LEN, y0 + SQR_LEN

    apple = canvas.create_image((x0 + x1) / 2, (y0 + y1) / 2, image=canvas.apple_img)
    apple_coords = [x1 // SQR_LEN, y1 // SQR_LEN]


def collision_occurred() -> bool:
    if not (1 <= head_coords[0] <= SQRS and 1 <= head_coords[1] <= SQRS):
        return True
    if head_coords in snake_coords[1:]:
        return True
    return False


if __name__ == '__main__':
    App()
