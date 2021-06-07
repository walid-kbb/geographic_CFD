import sys

import branca
import cx_Oracle
import folium
import pandas as pd
from folium import plugins
from shapely.geometry import Point, Polygon
import Reports
from Cell_sector import Cell_sector
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pathlib
import time
import json

folder_path = str(pathlib.Path().absolute())
get_cells_details = """select  a.tx_id, REPLACE(a.azimut, ',', '.') as "azimut", REPLACE(b.latitude, ',' ,'.') as "latitude",
                    REPLACE(b.longitude, ',' ,'.') as "longitude"
                    from atoll_mrat.ltransmitters a
                    left join atoll_mrat.sites b
                    on a.site_name = b.name
                    where length(a.tx_id)= 12 and b.fieldchar2 = 'INT'
                    order by a.tx_id"""


def get_neighbors(report,sector_cell_name):
    neighbors = {}
    for index, row in report.iterrows():
        target_cell_name = row['Target name']
        for cell_detail in cells_detail:
            if cell_detail[0] == target_cell_name and cell_detail[0][:-3] != sector_cell_name[:-3]:
                neighbors[cell_detail[0]] = [Point(float(cell_detail[2]),float(cell_detail[3])),row['Total eNB neighbor HO: Att']]
    return neighbors


def check_invertions(site_name):

    sector1_cell,sector2_cell,sector3_cell = None,None,None
    n_empty_reports = 0
    for cell in cells_detail:
        if cell[0] == str(site_name+'1'):

            report1 = report.loc[report['Source LNCEL name'] == cell[0]]
            print(len(report1.index))
            if len(report1.index) < 5: n_empty_reports = n_empty_reports + 1
            neighbors = get_neighbors(report1,cell[0]).copy()
            print("len neighbors = ", len(neighbors))
            sector1_cell = Cell_sector(cell[0],cell[1],cell[2],cell[3],neighbors)
            sectors_cells[sector1_cell.sector_cell_name] = sector1_cell

        if cell[0] == str(site_name+'2'):
            report2 = report.loc[report['Source LNCEL name'] == cell[0]]
            print(len(report2.index))
            if len(report2.index) < 5: n_empty_reports = n_empty_reports + 1
            neighbors = get_neighbors(report2, cell[0]).copy()
            print("len neighbors = ", len(neighbors))
            sector2_cell = Cell_sector(cell[0], cell[1], cell[2], cell[3], neighbors)
            sectors_cells[sector2_cell.sector_cell_name] = sector2_cell

        if cell[0] == str(site_name+'3'):
            report3 = report.loc[report['Source LNCEL name'] == cell[0]]
            print(len(report3.index))
            if len(report3.index) < 5 : n_empty_reports = n_empty_reports + 1
            neighbors = get_neighbors(report3, cell[0]).copy()
            print("len neighbors = ",len(neighbors))
            sector3_cell = Cell_sector(cell[0], cell[1], cell[2], cell[3], neighbors)
            sectors_cells[sector3_cell.sector_cell_name] = sector3_cell

    if sector1_cell is not None and sector2_cell is not None and sector3_cell is not None and n_empty_reports <= 1:
        sites = {}
        site = {}
        site['localisaiton'] = {'latitude':sector1_cell.point.x,'longitude':sector1_cell.point.y}
        sectors={}
        m = folium.Map(location=[sector1_cell.point.x, sector1_cell.point.y], zoom_start=15)
        draw = plugins.Draw(export=True)

        draw.add_to(m)

        folium.Marker(
            location=[sector1_cell.point.x, sector1_cell.point.y],
            popup=sector1_cell.sector_cell_name[:-3],
            icon=folium.Icon(color='red'),
        ).add_to(m)

        html = """
            <h1> This is a big popup</h1><br>
            With a few lines of code...
            <p>
            blabla bla
            </p>
            """

        iframe = branca.element.IFrame(html=html, width=500, height=300)
        popup = folium.Popup(iframe, max_width=2650)


        folium.Polygon(locations=Polygon(sector1_cell.folium_polygon()).exterior.coords,
                       color="#ff3388",
                       fill_color="#ff3388", fill_opacity=0.8, popup=popup).add_to(m)

        folium.Polygon(locations=Polygon(sector2_cell.folium_polygon()).exterior.coords,
                       color="#40B600",
                       fill_color="#40B600", fill_opacity=0.8,popup=sector2_cell.sector_cell_name).add_to(m)

        folium.Polygon(locations=Polygon(sector3_cell.folium_polygon()).exterior.coords,
                       color="#0C98D5",
                       fill_color="#0C98D5", fill_opacity=0.8,popup=sector3_cell.sector_cell_name).add_to(m)

        neighbors_sectore1={}
        neighbors_sectore2 = {}
        neighbors_sectore3 = {}

        for key,value in sector1_cell.neighbors.items():
            folium.Marker(
                location=[value[0].x, value[0].y],
                popup=key,
                icon=folium.Icon(color='red'),
            ).add_to(m)
            neighbors_sectore1[key]={'localisation':{'latitude':value[0].x,'longitude':value[0].y},'tho_att':value[1]}
            print(key)
            print(value[0])
            print(value[1])
            locations = [[sector1_cell.point.x,sector1_cell.point.y],[value[0].x, value[0].y]]
            folium.PolyLine(locations=locations,color="#ff3388").add_to(m)

        for key,value in sector2_cell.neighbors.items():
            folium.Marker(
                location=[value[0].x, value[0].y],
                popup=key,
                icon=folium.Icon(color='red'),
            ).add_to(m)
            neighbors_sectore2[key] = {'localisation': {'latitude': value[0].x, 'longitude': value[0].y},
                                       'tho_att': value[1]}
            print(key)
            print(value[0])
            print(value[1])
            locations = [[sector2_cell.point.x,sector2_cell.point.y],[value[0].x, value[0].y]]
            folium.PolyLine(locations=locations,color="#40B600").add_to(m)

            for key, value in sector3_cell.neighbors.items():
                folium.Marker(
                    location=[value[0].x, value[0].y],
                    popup=key,
                    icon=folium.Icon(color='red'),
                ).add_to(m)
                neighbors_sectore3[key] = {'localisation': {'latitude': value[0].x, 'longitude': value[0].y},
                                           'tho_att': value[1]}
                print(key)
                print(value[0])
                print(value[1])
                locations = [[sector3_cell.point.x, sector3_cell.point.y], [value[0].x, value[0].y]]
                folium.PolyLine(locations=locations, color="#0C98D5").add_to(m)
        print("sector1_cell.folium_polygon()")
        print( sector1_cell.folium_polygon())
        sectors[sector1_cell.sector_cell_name] = {'polygon':sector1_cell.folium_polygon(),'neighbors':neighbors_sectore1}
        sectors[sector2_cell.sector_cell_name] = {'polygon':sector2_cell.folium_polygon(),'neighbors':neighbors_sectore2}
        sectors[sector3_cell.sector_cell_name] = {'polygon':sector3_cell.folium_polygon(),'neighbors':neighbors_sectore3}
        site['sectors']=sectors
        sites['site_name'] = {sector1_cell.sector_cell_name[:-1]:site}
        print(site)
        json_object=json.dumps(sites,indent=4)
        print(json_object)
        m.save(folder_path + "\geo_analyse\{}.html".format(site_name))
    else:
        print("Untreated site ({}) ".format(site_name))


if __name__ == '__main__':

    cross_sectors = []
    output = []
    sectors_cells = {}
    cx_Oracle.init_oracle_client(lib_dir=r"C:\app\wkebbab\product\19.0.0\client_1")
    pathlib.Path(folder_path + "\geo_analyse").mkdir(parents=True, exist_ok=True)
    report = pd.read_csv(folder_path + "\merged_reports.csv", sep=';')
    source_cells = pd.read_csv(folder_path + "\cells_st.csv", sep=';')

    try:
        print("reports preparation")
        Reports.prepare_reports()
        print("DB connexion ")
        con = cx_Oracle.connect('ailloul','password5',"atoll")
        cursor = con.cursor()
        print("fetch cells data")
        cursor.execute(get_cells_details)
        cells_detail = cursor.fetchall()
        print("data fetched")
        # sites list
        sites= set()
        for index, row in source_cells.iterrows():
            sites.add(row['Source LNCEL name'][:-1])
        nb_sites = len(sites)
        print("check_invertions")

        start_time = time.time()
        i=1
        for site in sites:
            print("\n Site = ",site+"x    | {} of {}".format(i,nb_sites))
            check_invertions(site)
            i=i+1
            break
        print("--- %s seconds ---" % (time.time() - start_time))
        if cursor:
            cursor.close()
        if con:
            con.close()

    except cx_Oracle.DatabaseError as e:
        print("Problem connecting to Oracle", e)

    # Saving outputs

    cross_sectors_df = pd.DataFrame(cross_sectors, columns=["sector_cell", "cosite_cell"])
    print("Crossed sectors =")
    print(cross_sectors_df)
    cross_sectors_df.to_csv(folder_path+"\cross_sectors.csv", index=False, sep=";")

    output_df = pd.DataFrame(output, columns=["sector_cell", "cosite_cell","cross","distance_score","cross_possibility"])
    print("output =")
    print(output_df)
    output_df.to_csv(folder_path + "\output.csv", index=False, sep=";")
    sys.exit()