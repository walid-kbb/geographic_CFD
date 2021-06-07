import pyproj
from shapely.geometry import Point, Polygon
from geopy import distance as dis

class Cell_sector:

    def __init__(self,sector_cell_name,azimuth,lat,long,neighbors):

        self.sector_cell_name = sector_cell_name
        self.site_name = sector_cell_name[:-3]
        self.azimuth = int(azimuth)
        self.point = Point(float(lat),float(long))
        self.neighbors = neighbors.copy()
        self.farthest_distance = self.get_farthest_distance() * 1000
        self.polygon = self.get_polygon()

    def get_polygon(self):

        distance = self.farthest_distance * 1.3
        beam = 45
        az1 = self.azimuth - beam
        if az1 < 0: az1 = az1 + 360
        az2 = self.azimuth + beam
        if az2 < 0: az2 = az2 + 360
        long1, lat1, backAzimuth = pyproj.Geod(ellps='WGS84').fwd(self.point.y, self.point.x, az1, distance)
        long2, lat2, backAzimuth = pyproj.Geod(ellps='WGS84').fwd(self.point.y, self.point.x, az2, distance)

        lon_point_list = [self.point.y, long1, long2]
        lat_point_list = [self.point.x, lat1, lat2]

        return Polygon(list(zip(lat_point_list, lon_point_list)))

    def folium_polygon(self):
        distance = 100
        beam = 45
        az1 = self.azimuth - beam
        if az1 < 0: az1 = az1 + 360
        az2 = self.azimuth + beam
        if az2 < 0: az2 = az2 + 360
        long1, lat1, backAzimuth = pyproj.Geod(ellps='WGS84').fwd(self.point.y, self.point.x, az1, distance)
        long2, lat2, backAzimuth = pyproj.Geod(ellps='WGS84').fwd(self.point.y, self.point.x, az2, distance)

        lon_point_list = [self.point.y, long1, long2]
        lat_point_list = [self.point.x, lat1, lat2]

        return list(zip(lat_point_list, lon_point_list))

    def get_inverse_polygon(self,azimuth):

        distance = self.farthest_distance  * 1.3
        beam = 45
        az1 = azimuth - beam
        if az1 < 0: az1 = az1 + 360
        az2 = azimuth + beam
        if az2 < 0: az2 = az2 + 360
        long1, lat1, backAzimuth = pyproj.Geod(ellps='WGS84').fwd(self.point.y, self.point.x, az1, distance)
        long2, lat2, backAzimuth = pyproj.Geod(ellps='WGS84').fwd(self.point.y, self.point.x, az2, distance)

        lon_point_list = [self.point.y, long1, long2]
        lat_point_list = [self.point.x, lat1, lat2]

        return Polygon(list(zip(lat_point_list, lon_point_list)))

    def get_farthest_distance(self):
        farthest_distance = 0
        for key, value in self.neighbors.items():
            distance = dis.distance((self.point.x,self.point.y), (value[0].x,value[0].y)).km
            if distance > farthest_distance:
                farthest_distance = distance
        return  farthest_distance

    def cell_sector_infos(self):
        print("sector_cell_name =", self.sector_cell_name )
        print("site_name = ",self.site_name )
        print("azimuth = ", self.azimuth)
        print("point = ", self.point)
        print("neighbors =", self.neighbors)
        print("polygon =", self.polygon)
        print("farthest_distance =", self.farthest_distance,"\n")



















