from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Line
from kivy.properties import StringProperty

class DynamicWidget():

    def __init__(self, **kwargs):

        # Extracting the unique keywords
        self.ratio_size = kwargs.pop('ratio_size')
        self.ratio_pos = kwargs.pop('ratio_pos')
        self.root = kwargs.pop('root')

        # Calculate the pixel size and pos
        size = (self.ratio_size[0]*self.root.width, self.ratio_size[1]*self.root.height)
        pos = (self.ratio_pos[0]*self.root.width-size[0]/4, self.ratio_pos[1]*self.root.height-size[1]/4)

        # Addint the new size and pos to kwargs
        kwargs['size'] = size
        kwargs['pos'] = pos

        # Saving modified kwargs to account for the next inheritance
        self.new_kwargs = kwargs

    def create_binding(self):
        # Creating the binding function
        self.root.bind(size=self.update_size_pos, pos=self.update_size_pos)

    def update_size_pos(self, instance, _):
        self.size = (self.ratio_size[0]*instance.width, self.ratio_size[1]*instance.height)
        self.pos = (self.ratio_pos[0]*instance.width-self.size[0]/4, self.ratio_pos[1]*instance.height-self.size[1]/4)
        
class DynamicImage(DynamicWidget, Image):

    def __init__(self, **kwargs):

        DynamicWidget.__init__(self, **kwargs)
        Image.__init__(self, **self.new_kwargs)
        self.create_binding()

class PlayerIcon(Label):

    image_source = StringProperty('None')
