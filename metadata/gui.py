from tkinter import *
from PIL import Image, ImageTk

class Window(Frame):

    def __init__(self, main=None):
        
        Frame.__init__(self, main)
        self.load = Image.open('cover_page.jpg')
        
        self.main = main
        self.pack(fill=BOTH, expand=1)

    def dimensions(self, image):
        '''Gets the cover page image dimensions'''
        width, height = image.size
        return f'{width}x{height}'
    
    def resize_image(self):
        '''Resize cover page image for viewer window'''
        width, height = self.load.size
        new = (round(width * .75), round(height * .75))
        print(new)
        self.adjusted_image = self.load.resize(new)

    def render_image(self):
        '''Renders image in main window'''
        render = ImageTk.PhotoImage(self.adjusted_image)
        img = Label(self, image=render, borderwidth=0)
        img.image = render
        img.place(x=0, y=0)

def deploy_window():
    '''Deploys the preview image window'''
    root = Tk()
    root.resizable(False, False)

    app = Window(root)
    app.resize_image()
    app.render_image()
    
    dim = app.dimensions(app.adjusted_image)
    
    root.geometry(dim)
    root.mainloop()
