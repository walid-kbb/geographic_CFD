from shapely.geometry import Point

class Cell_site:

    def __init__(self,cell_name,az,x,y):

        self.cell_name=cell_name
        self.azimut = az
        self.point = Point(float(x),float(y))



