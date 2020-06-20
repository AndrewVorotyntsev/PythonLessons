# -*- coding: utf-8 -*-
import copy
from PIL import Image
import re
import math
from tkinter import *
from PIL import ImageTk, Image

scr_x = 800  # Ширина картинки
scr_y = scr_x  # Высота картинки


def turn(a, x, z):  # умножение координат на матрицу поворота
    angle = math.radians(a)
    first = x * math.cos(angle) - z * math.sin(angle)
    second = x * math.sin(angle) + z * math.cos(angle)
    return first, second


class Screen(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.img = Image.new('RGB', (width, height), 'black')
        self.canvas = self.img.load()
        self.z_buffer = [[0] * width for i in range(height)]

    def point(self, *coords):
        return TexturePoint(self, *coords)

    @staticmethod
    def triangle(coords, texture):
        a, b, c = sorted(coords, key=lambda p: p.y)
        p1, p2 = a.copy(), a.copy()
        height = c.y - a.y
        delta_x2 = float(c.x - a.x) / height
        deltas = lambda i, j, divider: [float(i.z - j.z) / divider, float(i.u - j.u) / divider,
                                        float(i.v - j.v) / divider]
        delta_z2, delta_u2, delta_v2 = deltas(c, a, height)
        for p in (b, c):
            height = (p.y - p1.y) or 1
            delta_x1 = float(p.x - p1.x) / height
            delta_z1, delta_u1, delta_v1 = deltas(p, p1, height)
            while p1.y < p.y:
                p3, p4 = (p2.copy(), p1) if p1.x > p2.x else (p1.copy(), p2)
                delta_z3, delta_u3, delta_v3 = deltas(p4, p3, (p4.x - p3.x) or 1)
                while p3.x < p4.x:
                    p3.show(texture[p3.u, p3.v])
                    p3.add(x=1, z=delta_z3, u=delta_u3, v=delta_v3)
                p1.add(x=delta_x1, y=1, z=delta_z1, u=delta_u1, v=delta_v1)
                p2.add(x=delta_x2, y=1, z=delta_z2, u=delta_u2, v=delta_v2)
            p1 = b.copy()


class Point(object):
    def __init__(self, screen, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.screen = screen

    def show(self, color=None):
        screen = self.screen
        x = int(self.x)
        y = int(self.y)
        if self.z <= screen.z_buffer[y][x]:
            return
        screen.z_buffer[y][x] = self.z
        screen.canvas[x, screen.height - y] = color or (255, 255, 255)

    def copy(self):
        return copy.copy(self)


class TexturePoint(Point):
    def __init__(self, screen, x, y, z, u, v):
        super(TexturePoint, self).__init__(screen, x, y, z)
        self.u = u
        self.v = v

    def add(self, x=0, y=0, z=0, u=0, v=0):
        self.x += x
        self.y += y
        self.z += z
        self.u += u
        self.v += v


root = Tk()
root.geometry('500x500')
my_canvas = Canvas(root, width=800, height=700)
my_canvas.pack()
global r
r = 60
print("Для поворота объекта зажмите правую кнопку мыши. \nНажмите левую кнопку мыши ,чтобы получить координаты точки. \n"
          "Нажмите среднюю кнопку мыши ,чтобы нарисовать круг , с центром в точке с координатами полученными ранее.")


def show_face():
    half_scr_x = int(scr_x / 2)
    half_scr_y = int(scr_y / 2)
    texture_img = Image.open('african_head_diffuse.tga')
    texture = texture_img.load()
    f = open('face.obj', 'r')
    lines = f.read()
    points = []
    textures = []
    screen = Screen(scr_x, scr_y)

    for line in lines.split('\n'):
        try:
            v, x, y, z = re.split('\s+', line)
        except ValueError:
            continue
        if v == 'v':
            x, z = turn(r, float(x), float(z))  # вызов функции умножения координат на матрицу поворота\
            x = int((float(x) + 1) * half_scr_x)
            y = int((float(y) + 1) * half_scr_y)
            z = float(z) + 1
            points.append((x, y, z))
        if v == 'vt':
            u = float(x) * texture_img.width
            v = (1 - float(y)) * texture_img.height
            textures.append((u, v))
        if v == 'f':
            indexes = [[int(j) - 1 for j in i.split('/')] for i in (x, y, z)]
            tr_points = []
            for i in range(3):
                params = points[indexes[i][0]] + textures[indexes[i][1]]
                tr_points.append(screen.point(*params))
            screen.triangle(tr_points, texture)

    # Задаем функцию , которая будет показывать координаты
    def display_coordinates(event):
        my_label['text'] = f'x={event.x} y={event.y}'
        global x_circle
        x_circle = event.x
        global y_circle
        y_circle = event.y

    # Задем функцию рисования круга в точке с координатами ,полученными из предидущей функции
    def draw_circle(event):
        my_canvas.delete(ALL)
        my_canvas.create_oval(x_circle - 35, y_circle - 35, x_circle + 35, y_circle + 35, fill='red')

    # Задаем две функции , отвечающие за поворот текстуры
    # При нажатии правой кнопки мыши получаем координаты точки , в которой произошло нажатие
    def add_angle_start(event):
        global start
        start = event.x

    # Получаем координаты точки , в которой мышка была отжата.
    # В зависимости от разности этих координат получаем угол поворота
    def add_angle_stop(event):
        global end
        end = event.x
        global r
        r = r + (start - end)/2.22
        print("Угол поворота равен = ", r)
        my_canvas.delete(ALL)
        show_face()

    pilImage = screen.img
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = my_canvas.create_image(400, 450, image=image)
    my_label = Label(bd=4, relief="solid", font="Times 22 bold", bg="white", fg="black")

    # Назначаем действия соответсвующим кнопкам
    my_canvas.bind('<Button-1>', display_coordinates)
    my_canvas.bind('<ButtonPress-3>', add_angle_start)
    my_canvas.bind('<ButtonRelease-3>', add_angle_stop)
    my_canvas.bind('<Button-2>', draw_circle)

    my_canvas.grid(row=0, column=0)
    my_label.grid(row=1, column=0)

    root.mainloop()


show_face()
