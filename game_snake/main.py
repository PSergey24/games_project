from tkinter import *
import random
import time


class SnakeGame:
    def __init__(self):
        self.game_is_running = True
        self.snake_x = 24
        self.snake_y = 24
        self.snake_direction_x = 0
        self.snake_direction_y = 0

        self.snake_list = []
        self.snake_size = 3

        self.food_list = []
        self.food_count = 20

        self.window_logic = WindowLogic()

    def start(self):
        self.window_logic.create_window()
        self.snake_list = self.window_logic.snake_paint_item(self.snake_list, self.snake_x, self.snake_y)
        self.generate_food()

        self.motion_handler(self.window_logic)
        self.window_logic.tk.mainloop()

    def generate_food(self):
        self.food_list = self.window_logic.generate_food(self.food_count)

    def motion_handler(self, window_logic):
        window_logic.canvas.bind_all("<KeyPress-Left>", self.snake_move)
        window_logic.canvas.bind_all("<KeyPress-Right>", self.snake_move)
        window_logic.canvas.bind_all("<KeyPress-Up>", self.snake_move)
        window_logic.canvas.bind_all("<KeyPress-Down>", self.snake_move)

        while self.game_is_running is True:
            self.snake_is_correct()
            self.food_is_found()
            self.is_borders()
            self.is_touch_self(self.snake_x + self.snake_direction_x, self.snake_y + self.snake_direction_y)

            self.snake_x += self.snake_direction_x
            self.snake_y += self.snake_direction_y
            self.snake_list = self.window_logic.snake_paint_item(self.snake_list, self.snake_x, self.snake_y)
            self.window_logic.tk.update_idletasks()
            self.window_logic.tk.update()
            time.sleep(0.5)

        window_logic.canvas.bind_all("<KeyPress-Left>", self.nothing_move)
        window_logic.canvas.bind_all("<KeyPress-Right>", self.nothing_move)
        window_logic.canvas.bind_all("<KeyPress-Up>", self.nothing_move)
        window_logic.canvas.bind_all("<KeyPress-Down>", self.nothing_move)

    def nothing_move(self):
        pass

    def snake_move(self, event):
        if event.keysym == "Up":
            self.snake_direction_x = 0
            self.snake_direction_y = -1
            self.snake_is_correct()
        elif event.keysym == "Down":
            self.snake_direction_x = 0
            self.snake_direction_y = 1
            self.snake_is_correct()
        elif event.keysym == "Left":
            self.snake_direction_x = -1
            self.snake_direction_y = 0
            self.snake_is_correct()
        elif event.keysym == "Right":
            self.snake_direction_x = 1
            self.snake_direction_y = 0
            self.snake_is_correct()

        self.snake_x += self.snake_direction_x
        self.snake_y += self.snake_direction_y
        self.snake_list = self.window_logic.snake_paint_item(self.snake_list, self.snake_x, self.snake_y)
        self.food_is_found()

    def snake_is_correct(self):
        if len(self.snake_list) >= self.snake_size:
            temp_item = self.snake_list.pop(0)
            self.window_logic.delete_snake_tail(temp_item)

    def food_is_found(self):
        for item_food in self.food_list:
            if item_food[0] == self.snake_x and item_food[1] == self.snake_y:
                self.snake_size += 1
                self.window_logic.canvas.delete(item_food[2])
                self.window_logic.canvas.delete(item_food[3])

    def is_borders(self):
        if self.snake_x > self.window_logic.world_size_width or self.snake_x < 0 or \
                self.snake_y > self.window_logic.world_size_height or self.snake_y < 0:
            self.game_over()

    def is_touch_self(self, future_x, future_y):
        if not (self.snake_direction_x == 0 and self.snake_direction_y == 0):
            for item_snake in self.snake_list:
                if item_snake[0] == future_x and item_snake[1] == future_y:
                    self.game_over()

    def game_over(self):
        self.game_is_running = False


class WindowLogic:
    def __init__(self):
        self.window_width = 500
        self.window_height = 500
        self.snake_item = 10

        self.world_size_width = int(self.window_width / self.snake_item)
        self.world_size_height = int(self.window_height / self.snake_item)

        self.snake_color_1 = "black"
        self.snake_color_2 = "red"

        self.food_color_1 = "blue"
        self.food_color_2 = "pink"

        self.tk = None
        self.canvas = None

    def create_window(self):
        self.tk = Tk()
        self.tk.title("Snake game")
        self.tk.resizable(False, False)
        self.tk.wm_attributes("-topmost", 1)
        self.canvas = Canvas(self.tk, width=self.window_width, height=self.window_height, bg='white', bd=0,
                             highlightthickness=0)
        self.canvas.pack()

    def snake_paint_item(self, snake_list, x, y):
        id_1 = self.canvas.create_rectangle(x * self.snake_item, y * self.snake_item,
                                            x * self.snake_item + self.snake_item,
                                            y * self.snake_item + self.snake_item,
                                            fill=self.snake_color_1)
        id_2 = self.canvas.create_rectangle(x * self.snake_item + 2, y * self.snake_item + 2,
                                            x * self.snake_item + self.snake_item - 2,
                                            y * self.snake_item + self.snake_item - 2,
                                            fill=self.snake_color_2)
        snake_list.append([x, y, id_1, id_2])
        return snake_list

    def generate_food(self, food_count):
        food_list = []
        for i in range(food_count):
            x = random.randrange(self.world_size_width)
            y = random.randrange(self.world_size_height)
            id_1 = self.canvas.create_oval(x * self.snake_item, y * self.snake_item,
                                           x * self.snake_item + self.snake_item,
                                           y * self.snake_item + self.snake_item,
                                           fill=self.food_color_1)
            id_2 = self.canvas.create_oval(x * self.snake_item + 2, y * self.snake_item + 2,
                                           x * self.snake_item + self.snake_item - 2,
                                           y * self.snake_item + self.snake_item - 2,
                                           fill=self.food_color_2)
            # todo: need conditions for unique positions
            food_list.append([x, y, id_1, id_2])
        return food_list

    def delete_snake_tail(self, temp_item):
        self.canvas.delete(temp_item[2])
        self.canvas.delete(temp_item[3])
