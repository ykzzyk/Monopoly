from kivy.uix.image import Image

def DynamicImage(Image):

    def __init__(self, *args, **kwargs):

        # Extracting the unique keywords
        self.ratio_size = kwargs.pop('ratio_size')
        self.ratio_pos = kwargs.pop('ratio_pos')
        self.root = kwargs.pop('root')

        # Calculate the pixel size and pos
        size = (self.ratio_size[0]*self.root.width, self.ratio_size[1]*self.root.height)
        pos = (self.ratio_pos[0]*self.root.width, self.ratio_pos[1]*self.root.height)

        # Addint the new size and pos to kwargs
        kwargs['size'] = size
        kwargs['pos'] = pos

        # Inhereting the parent class's attributes
        super(self).__init__(*args, **kwargs)

        # Creating the binding function
        self.root.bind(size=self.update_size_pos, pos=self.update_size_pos)

    def update_size_pos(self, instance, _):
        self.size = (self.ratio_size[0]*instance.width, self.ratio_size[1]*instance.height)
        self.pos = (self.ratio_pos[0]*instance.width, self.ratio_pos[1]*instance.height)