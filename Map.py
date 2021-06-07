import folium
import pyproj
from folium import plugins
from shapely.geometry import Polygon
from Cell_site import Cell_site
import pathlib
from pathlib import Path

folder_path = str(pathlib.Path().absolute())

def creat_polygon(source_cell):

    distance = 50000
    beam = 35
    az1 = source_cell.azimut - beam
    if az1 < 0: az1 = az1 + 360
    az2 = source_cell.azimut + beam
    if az2 < 0: az2 = az2 + 360

    long1, lat1, backAzimuth = pyproj.Geod(ellps='WGS84').fwd(source_cell.point.y, source_cell.point.x, az1, distance)
    long2, lat2, backAzimuth = (pyproj.Geod(ellps='WGS84')
                                .fwd(source_cell.point.y, source_cell.point.x, az2, distance))

    lon_point_list = [source_cell.point.y, long1, long2]
    lat_point_list = [source_cell.point.x, lat1, lat2]

    return Polygon(list(zip(lat_point_list, lon_point_list)))

def creat_map(source_cell,target_cell,cells_detail,report):

    report = report.loc[report['Source LNCEL name'] == source_cell.cell_name]
    m = folium.Map(location=[source_cell.point.x, source_cell.point.y], zoom_start=15)

    draw = plugins.Draw(export=True)

    draw.add_to(m)

    folium.Marker(
        location=[source_cell.point.x, source_cell.point.y],
        popup="source_cell",
        icon=folium.Icon(color='red'),
    ).add_to(m)

    for index, row in report.iterrows():
        target_cell_name = row['Target name']
        for cell_detail in cells_detail:
            if cell_detail[0] == target_cell_name and cell_detail[0][:-3] != source_cell.cell_name[:-3]:
                # Cell_site( cell_name , azimut, lat , long )
                folium.Marker(
                    location=[cell_detail[2], cell_detail[3]],
                    popup= cell_detail[0][:-3],
                ).add_to(m)
                break
    polygon = creat_polygon(source_cell)
    folium.Polygon(locations=polygon.exterior.coords, color="#3388ff",
                   fill_color="#3388ff", fill_opacity=0.2).add_to(m)

    folium.Polygon(locations=creat_polygon(target_cell).exterior.coords,
                   color="#FFA500",
                   fill_color="#FFA500", fill_opacity=0.2).add_to(m)

    for x in range(3):

        if x+1 != int(source_cell.cell_name[-1]) and x+1 != int(target_cell.cell_name[-1]):
            cell3_name =  source_cell.cell_name[:-1]+str(x+1)

    for cell_detail in cells_detail:
        if cell_detail[0] == cell3_name:
            cell3 = Cell_site(cell_detail[0], int(cell_detail[1]), cell_detail[2], cell_detail[3])
            folium.Polygon(locations=creat_polygon(cell3).exterior.coords,
                           color="#ff3388",
                           fill_color="#ff3388", fill_opacity=0.2).add_to(m)

    Path(folder_path+"\geo_analyse").mkdir(parents=True,exist_ok=True)

    m.save(folder_path+"\geo_analyse\{} - {}.html".format(source_cell.cell_name,target_cell.cell_name))


