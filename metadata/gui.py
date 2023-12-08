from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

class Window(Frame):

    def __init__(self, main=None):
        
        Frame.__init__(self, main)
        self.load = Image.open('cover_page.jpg')
        self.main = main
        self.pack(fill=BOTH, expand=1)
        self.rarrow = PhotoImage(file='arrow-right-solid.png')
        self.larrow = PhotoImage(file='arrow-left-solid.png')

    def dimensions(self, image):
        '''Gets the cover page image dimensions'''
        width, height = image.size
        return f'{width}x{height + 46}'
    
    def resize_image(self):
        '''Resize cover page image for viewer window'''
        width, height = self.load.size
        new = (round(width * .75), round(height * .75))
        self.adjusted_image = self.load.resize(new)

    def render_image(self):
        '''Renders image in main window'''
        render = ImageTk.PhotoImage(self.adjusted_image)
        img = Label(self, image=render, borderwidth=0)
        img.image = render
        img.pack(side=TOP)

        style = ttk.Style()
        style.configure('TButton', background='#333333')

        button_frame = Frame(self, bg='#333333')
        button_frame.pack(side=BOTTOM, fill=X, expand=True)

        button1 = ttk.Button(button_frame, text='Previous', 
            image=self.larrow, compound='image')
        button2 = ttk.Button(button_frame, text='Next',
            image=self.rarrow, compound='image')

        button1.grid(row=0, column=0, padx=10, pady=10)
        button2.grid(row=0, column=1, padx=10, pady=10)

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

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

if __name__ == '__main__':
    deploy_window()