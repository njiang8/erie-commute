import uuid
from functools import partial

import pandas as pd
import geopandas as gpd
import mesa
import mesa_geo as mg
import ast
from shapely.geometry import Point

from src.agent.commuter import Commuter
#from src.agent.building import Building
from src.space.road_network import CampusWalkway
#from src.agent.geo_agents import Driveway, LakeAndRiver, Walkway
from src.space.create_erie_county import Build_Erie_County
from src.space.utils import _to_gpd

def get_time(model) -> pd.Timedelta:
    return pd.Timedelta(days=model.day, hours=model.hour, minutes=model.minute)


def get_num_commuters_by_status(model, status: str) -> int:
    commuters = [
        commuter for commuter in model.schedule.agents if commuter.status == status
    ]
    return len(commuters)


class ErieCommuteModel(mesa.Model):

    def __init__(self,
                data_crs: str,
                population_file: str,
                #buildings_file: str,
                #walkway_file:str,
                #lakes_file:str,
                #rivers_file:str,
                driveway_file:str,
                commuter_speed=1.0,
                #model_crs="epsg:3857",
                model_crs='epsg:4326',
                #show_walkway = False,
                #show_lakes_and_rivers = False,
                #show_driveway = False,
    ) -> None:
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        #agent
        Commuter.SPEED = 300.0

        #time space
        self.day = 0
        self.hour = 5
        self.minute = 55

        #geo space
        self.data_crs = data_crs
        self.space = Build_Erie_County(crs=model_crs)

        # load shapefiles
        #self._load_buildings_from_file(buildings_file, crs=model_crs) #buildings

        #show other shapefiles?
        #self.show_walkway = show_walkway
        #self._load_road_vertices_from_file(walkway_file, crs=model_crs)  #walkways

        #self.show_driveway = show_driveway
        #self.show_lakes_and_rivers = show_lakes_and_rivers
        #if show_driveway:
            #self._load_driveway_from_file(driveway_file, crs=model_crs)#driveways
        #if show_lakes_and_rivers:
            #self._load_lakes_and_rivers_from_file(lakes_file, crs=model_crs)#water
            #self._load_lakes_and_rivers_from_file(rivers_file, crs=model_crs)

        #load population
        self._load_population_from_file(population_file)

        #Stat
        #self.got_to_destination = 0
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "time": get_time,
                "status_home": partial(get_num_commuters_by_status, status= "at-home"),
                "status_work": partial(get_num_commuters_by_status, status= "at-daytime-location"),
                "status_traveling": partial(get_num_commuters_by_status, status="commuting"),
            }
        )

        self.datacollector.collect(self)

    def _load_buildings_from_file(self, buildings_file: str, crs: str) -> None:
        print("model->load_building...")
        buildings_df = gpd.read_file(buildings_file)
        #buildings_df.drop("Id", axis=1, inplace=True)
        buildings_df.index.name = "unique_id"
        buildings_df = buildings_df.set_crs(self.data_crs, allow_override=True).to_crs(crs)
        buildings_df["centroid"] = [
            (x, y) for x, y in zip(buildings_df.centroid.x, buildings_df.centroid.y)
        ]
        building_creator = mg.AgentCreator(Building, model=self)
        buildings = building_creator.from_GeoDataFrame(buildings_df)

        self.space.add_buildings(buildings)

    def _load_road_vertices_from_file(self, walkway_file: str, crs: str) -> None:
        print("model->load_walkway-vertices...")
        walkway_df = (
            gpd.read_file(walkway_file)
            .set_crs(self.data_crs, allow_override=True)
            .to_crs(crs)
        )
        #self.walkway = CampusWalkway(lines=walkway_df["geometry"]) #what doese this function do?
        if self.show_walkway:
            walkway_creator = mg.AgentCreator(Walkway, model=self)
            walkway = walkway_creator.from_GeoDataFrame(walkway_df)
            self.space.add_agents(walkway)

    def _load_driveway_from_file(self, driveway_file: str, crs: str) -> None:
        print("model->load_driveway...")
        driveway_df = (
            gpd.read_file(driveway_file)
            .set_index("Id")
            .set_crs(self.data_crs, allow_override=True)
            .to_crs(crs)
        )
        driveway_creator = mg.AgentCreator(Driveway, model=self)
        driveway = driveway_creator.from_GeoDataFrame(driveway_df)
        self.space.add_agents(driveway)

    def _load_lakes_and_rivers_from_file(self, lake_river_file: str, crs: str) -> None:
        print("model->load_water_line_area..")
        lake_river_df = (
            gpd.read_file(lake_river_file)
            .set_crs(self.data_crs, allow_override=True)
            .to_crs(crs)
        )
        lake_river_df.index.names = ["Id"]
        lake_river_creator = mg.AgentCreator(LakeAndRiver, model=self)
        gmu_lake_river = lake_river_creator.from_GeoDataFrame(lake_river_df)
        self.space.add_agents(gmu_lake_river)

    def _load_population_from_file(self, population_file: str) -> None:
        import timeit
        start_time = timeit.default_timer()
        print("model->load_population..")
        pop_gdf = _to_gpd(pd.read_csv(population_file).iloc[:,1:])
        #print(pop_gdf.head())
        for row in range(len(pop_gdf)):#create agents (commuters)
            #print(type(pop_gdf.geometry[row]))
            #print(pop_gdf.commute_path[row])
            commuter = Commuter(
                unique_id = str(pop_gdf.index[row]),
                model= self,
                geometry = pop_gdf.geometry[row],
                crs = self.space.crs,
            )
            #print("id",commuter.unique_id)
            commuter.my_home = ast.literal_eval(pop_gdf.from_node[row])

            if pop_gdf.to_node[row] ==0:
                commuter.my_work = ast.literal_eval(pop_gdf.from_node[row])
            else:
                commuter.my_work = ast.literal_eval(pop_gdf.to_node[row])

            commuter.my_path = ast.literal_eval(pop_gdf.commute_path[row])

            if commuter.my_work == commuter.my_home:
                commuter.status = "work-from-home"
            else:
                commuter.status = "at-home"

            self.space.add_commuter(commuter)
            #print(self.space._commuter_id_map.keys())
            self.schedule.add(commuter)
        # return time
        elapsed = timeit.default_timer() - start_time
        print("Total Time(s) for population loading:", elapsed)

    def step(self) -> None:
        self.__update_clock()
        self.schedule.step()
        self.datacollector.collect(self)
        #TODO Collect data to csv call get number, history append or concat, if not runiing export csv
        #self.running

    def __update_clock(self) -> None:
        self.minute += 5
        if self.minute == 60:
            if self.hour == 23:
                self.hour = 0
                self.day += 1
            else:
                self.hour += 1
            self.minute = 0