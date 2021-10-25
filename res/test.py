# class MyClass:
#     def __init__(self):
#         self.argA=''


# var = MyClass()
# MyClass.argA = 'salut'
# var2 = MyClass()

# print(var.argA, var2.argA)

# raise NameError('Coordinates do not fit the grid layout!')
# # class Person:

# #     def __init__(self, first, last):
# #         self.firstname = first
# #         self.lastname = last

# #     def Name(self):
# #         return self.firstname + " " + self.lastname

# # class Employee(Person):

# #     def __init__(self, first, last, staffnum):
# #         Person.__init__(self,first, last)
# #         self.staffnumber = staffnum

# #     def GetEmployee(self):
# #         return self.Name() + ", " +  self.staffnumber

# # x = Person("Marge", "Simpson")
# # y = Employee("Homer", "Simpson", "1007")

# # print(x.Name())
# # print(y.GetEmployee())

# import tkinter as tk
# import random

# class App(tk.Tk):
#     def __init__(self, *args, **kwargs):
#         tk.Tk.__init__(self, *args, **kwargs)
#         self.canvas = tk.Canvas(self, width=50, height=50, borderwidth=0, highlightthickness=0)
#         self.canvas.pack(side="top", fill="both", expand="true")
#         self.rows = 100
#         self.columns = 100
#         self.cellwidth = 25
#         self.cellheight = 25

#         self.rect = {}
#         self.oval = {}
#         for column in range(20):
#             for row in range(20):
#                 x1 = column*self.cellwidth
#                 y1 = row * self.cellheight
#                 x2 = x1 + self.cellwidth
#                 y2 = y1 + self.cellheight
#                 self.rect[row,column] = self.canvas.create_rectangle(x1,y1,x2,y2, fill="blue", tags="rect")
#                 self.oval[row,column] = self.canvas.create_oval(x1+2,y1+2,x2-2,y2-2, fill="blue", tags="oval")

#         self.redraw(10)

#     def redraw(self, delay):
#         self.canvas.itemconfig("rect", fill="blue")
#         self.canvas.itemconfig("oval", fill="blue")
#         for i in range(10):
#             row = random.randint(0,19)
#             col = random.randint(0,19)
#             item_id = self.oval[row,col]
#             self.canvas.itemconfig(item_id, fill="green")
#         self.after(delay, lambda: self.redraw(delay))

# if __name__ == "__main__":
#     app = App()
#     app.mainloop()


# -----------------------------------------------------------------
# from tkinter import (Frame, Label, Tk)

# class test():
#     def __init__(self, root, height, width, center):
#         grid = Frame(root); LabelGrid = [[[] for i in range(width)] for j in range(height)]
#         for i in range(height) :
#             for j in range(width) :
#                 l = Label(grid)
#                 LabelGrid[i][j] = l
#                 l.grid(row=i, column=j)

#         coeffs = [
#             [-1, -1], [-1, 1], [1, 1], [1, -1], # Diagonals
#             [0, 1], [0, -1], [-1, 0], [1, 0] # Vertical/Horizontal
#         ]
#         coords = [center]
#         for x, y in coords :
#             curCellDist = (len(coords)-1)//8
#             for cx, cy in coeffs :
#                 nx, ny = x+cx, y+cy
#                 if not [nx, ny] in coords and \
#                 not nx in range(height) and \
#                 not ny in range(width) :
#                     coords.append([nx, ny])
#             LabelGrid[x][y].configure(text=curCellDist)

#         root.update()

# root = Tk()
# app = test(root, 16, 16, [8,8])
# root.mainloop()

from math import (ceil, floor)

width = height = 16; center = [8,8]; counter = 1; bfr = 1
Grid = [[[] for i in range(width)] for j in range(height)]

coeffs = [
    [-1, -1], [-1, 0], [-1, 1], [0, -1], # Diagonals
    [0, 1], [1, -1], [1, 0], [1, 1] # Vertical/Horizontal
]
coords = [center]
for x, y in coords :
    # a = len(coords)-1; b = floor(a/8); print(a, b)
    for cx, cy in coeffs :
        nx, ny = x+cx, y+cy
        if not [nx, ny] in coords and \
        nx in range(height) and \
        ny in range(width) :
            coords.append([nx, ny])
            l = len(coords)-1
            Grid[nx][ny] = bfr
            if not l%8 :
                counter +=1
                if counter == bfr+1 : 
                    counter = 1; bfr +=1
            








# def spiral(X, Y):
#     cntr = 0
#     x = y = 0
#     dx = 0
#     dy = -1
#     for i in range(max(X, Y)**2):
#         if (-X/2 < x <= X/2) and (-Y/2 < y <= Y/2):
#             # print (x, y)
#             Grid[8+x][8+y] = cntr
#         if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
#             dx, dy = -dy, dx; cntr+=1
#         x, y = x+dx, y+dy

# spiral(height-2, width-2)
for row in Grid :
    print(row, '\n')