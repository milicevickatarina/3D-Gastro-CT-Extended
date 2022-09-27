# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 00:22:10 2020

class for scrolling slices in matplotlib.pyplot
"""


class IndexTracker(object):
    def __init__(self, fig, ax, X, color_map, title):
        self.ax = ax
        # ax.set_title(title + '\nuse scroll wheel to navigate images')

        self.X = X
        self.fig = fig
        rows, cols, self.slices = X.shape
        self.ind = self.slices//2

        self.im = ax.imshow(self.X[:, :, self.ind], cmap = color_map)
        ax.set_axis_off()
        self.update()

    def onscroll(self, event):
        # print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.ind = (self.ind + 1) % self.slices
        else:
            self.ind = (self.ind - 1) % self.slices
        self.update()

    def update(self):
        self.im.set_data(self.X[:, :, self.ind])
        self.ax.set_ylabel('slice %s' % self.ind)
        self.fig.canvas.set_window_title('Series display: '+'slice %s' % self.ind)
        self.im.axes.figure.canvas.draw()
        
    def __del__(self):
        print("Destructor called")
        
    def on_close(self, event):
        print('Closed Figure!')
        self.__del__()