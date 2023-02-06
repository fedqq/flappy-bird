from tkinter import *
from tkextrafont import Font
from PIL import ImageTk
from random import randint

WIDTH = 600
HEIGHT = 800
SPEED = -2

class FlappyBird:

    def __init__(self):
        self.window = Tk()
        self.window.title("Flappy Bird")
        self.window.resizable(False, False)
        self.window.configure(bg = "#000000")

        self.font = Font(file = 'resources/upheavtt.ttf', family = 'Upheaval TT -BRK-', size = 50)

        self.canvas = Canvas(self.window, bg = "#000000", width = WIDTH, height = HEIGHT, bd = 0, relief = RAISED)
        self.canvas.pack()

        self.started = False
        self.paused = False
        self.first_start = True

        self.window.bind('<Button-1>', lambda event: self.click())

        self.ground_image = PhotoImage(file = 'resources/ground.png')
        self.background_image = PhotoImage(file = 'resources/background.png')
        self.top_pipe_image = PhotoImage(file = 'resources/top_pipe.png')
        self.bottom_pipe_image = PhotoImage(file = 'resources/bottom_pipe.png')
        self.start_image = PhotoImage(file = 'resources/start_img.png')
        self.bird_image = PhotoImage(file = 'resources/start_bird.png')
        self.icon_image = PhotoImage(file = 'resources\icon.png')

        self.window.iconphoto(False, self.icon_image)

        self.start_menu = self.canvas.create_image(0, 0, image = self.start_image, anchor = NW, tag = "start_image")
        self.start_bird = self.canvas.create_image(0, -100, image = self.bird_image, anchor = NW, tag = "start_bird")
        self.momentum = 0
        self.start_hover(True)

        self.window.mainloop()

    def start_hover(self, going_up):
        new_direction = False
        if going_up:
            if self.momentum != 4:
                self.momentum += 1
            else:
                new_direction = True
        else:
            if self.momentum != - 4:
                self.momentum -= 1
            else:
                new_direction = True
        self.canvas.move(self.start_bird, 0, self.momentum)
        
        if new_direction:
            self.hover_after = self.window.after(35, self.start_hover, not going_up)
        else:
            self.hover_after = self.window.after(35, self.start_hover, going_up)

    def click(self):
        if self.started:
            if self.dead:
                if self.restartable:
                    self.start()
            else:
                self.bird.jump(self)
        else:
            self.start()


    def start(self):
        self.window.after_cancel(self.hover_after)
        self.canvas.delete('all')

        self.font.configure(size = 50)

        self.started = True
        self.dead = False
        self.restartable = False

        self.score = 0
        self.counter = 0
        self.pipes = []

        self.canvas.create_image(0, 0, anchor = NW, image = self.background_image)
        self.canvas.create_image(0, 0, anchor = NW, image = self.ground_image, tag = 'ground')

        self.bird = Bird(self)
        self.bird.change_image(self)
        
        if self.first_start:
            self.window.bind('<space>', lambda event: self.space())
            self.window.bind('<Escape>', lambda event: self.pause())
            self.first_start = False
        
        self.score_text = self.canvas.create_text(WIDTH / 2, 100, text = "0", fill = "black", font = self.font, tag = 'label')
        self.score_text_shadow = self.canvas.create_text(WIDTH / 2 - 4, 96, text = "0", fill = "white", font = self.font, tag = 'label')

        self.pipes.append(Pipes(self))
        self.draw_loop()

    def space(self):
        if self.started and not self.dead:
            self.bird.jump(self)
        elif self.restartable:
            self.start()

    def draw_loop(self):
        self.counter += 1
        if self.counter % 15 == 0:
            self.bird.change_image(self)
        if self.counter % 125 == 0:
            self.pipes.append(Pipes(self))
        self.bird.refresh(self)
        for pipe in self.pipes:
            pipe.move(self)
            if pipe.x_countdown <= 0:
                self.pipes.remove(pipe)

        if not (self.dead or self.paused):
            self.draw_after = self.window.after(10, self.draw_loop)

    def lose_game(self):
        self.dead = True

        self.window.after_cancel(self.draw_after)

        self.canvas.delete('all')

        self.canvas.create_image(0, 0, anchor = NW, image = self.background_image)
        self.canvas.create_image(0, 0, anchor = NW, image = self.ground_image, tag = 'ground')

        self.font.configure(size = 30)
        self.canvas.create_text(WIDTH / 2, HEIGHT / 2 - 100, text = "Score: {}\nPress Space \nOr Click To Restart".format(self.score), fill = "black", font = self.font, justify = CENTER)
        self.canvas.create_text(WIDTH / 2 - 4, HEIGHT / 2 - 104, text = "Score: {}\nPress Space \nOr Click To Restart".format(self.score), fill = "white", font = self.font, justify = CENTER)

        self.window.after(1000, self.allow_restart)
        
    def pause(self):
        self.paused = not self.paused
        self.draw_loop()

    def allow_restart(self):
        self.restartable = True

class Bird:
    
    def __init__(self, game):
        self.bird_1 = PhotoImage(file = 'resources/bird_1.png')
        self.bird_2 = PhotoImage(file = 'resources/bird_2.png')
        self.bird_3 = PhotoImage(file = 'resources/bird_3.png')
        self.image = 1

        self.object = game.canvas.create_image(200, 15, image = self.bird_1, anchor = NW)
        self.y_position = 15
        self.momentum = 0

    def change_image(self, game):

        if self.image == 1:
            game.canvas.itemconfig(self.object, image = self.bird_2)
            self.image = 2
        elif self.image == 2:
            game.canvas.itemconfig(self.object, image = self.bird_3)
            self.image = 3
        else:
            self.image = 1
            game.canvas.itemconfig(self.object, image = self.bird_1)
    
    def refresh(self, game):
        if self.momentum != 20:
            self.momentum += 0.5
        
        if self.y_position + self.momentum > 710 or self.y_position + self.momentum < 0:
            game.lose_game()

        self.y_position += self.momentum
        taken = 0
        for index in range(len(game.pipes)):
            if game.pipes[-index].current:
                taken = game.pipes[-index].taken_area
                break
        if taken != 0 and (self.y_position in taken[0] or self.y_position in taken[1]):
                game.lose_game()
        game.canvas.move(self.object, 0, self.momentum)

    def jump(self, game):
        if game.dead:
            return
        self.momentum = -7
        self.y_position += self.momentum
        game.canvas.move(self.object, 0, self.momentum)

class Pipes:

    def __init__(self, game):
        self.x_countdown = WIDTH + 100
        self.number = randint(100, 400)
        self.current = False
        self.top_pipe = game.canvas.create_image(WIDTH, 0 - self.number, image = game.top_pipe_image, anchor = NW)
        self.bottom_pipe = game.canvas.create_image(WIDTH, 0 - self.number + 600, image = game.bottom_pipe_image, anchor = NW)
        self.taken_area = [range(0 - self.number, 500 - self.number), range(0 - self.number + 575, 0 - self.number + 1100)]
        game.canvas.tag_raise('label')
        game.canvas.tag_raise('ground')

    def move(self, game):
        game.canvas.move(self.top_pipe, SPEED, 0)
        game.canvas.move(self.bottom_pipe, SPEED, 0)
        self.x_countdown += SPEED
        if self.x_countdown in range(330-100, 330):
            self.current = True
        else:
            if self.current == True:
                game.score += 1
                game.canvas.itemconfig(game.score_text, text = '{}'.format(game.score))
                game.canvas.itemconfig(game.score_text_shadow, text = '{}'.format(game.score))
            self.current = False


if __name__ == '__main__':
    game = FlappyBird()