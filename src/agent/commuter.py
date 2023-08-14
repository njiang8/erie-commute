from __future__ import annotations

import random
from typing import List

import pyproj
import numpy as np
import mesa
import mesa_geo as mg
from shapely.geometry import Point, LineString

from src.agent.building import Building
from src.space.utils import redistribute_vertices, UnitTransformer


class Commuter(mg.GeoAgent):
    unique_id: str
    my_path: list[mesa.space.FloatCoordinate]
    status : str

    def __init__(self,
                 unique_id,
                 model,
                 geometry,
                 crs,
    ) -> None:
        super().__init__(unique_id,
                         model,
                         geometry,
                         crs,
                         )
        # TODO 1 ask boyu how to set time add starting and ending time to dataframe
        self.start_time_h = round(np.random.normal(6.5, 1))
        while self.start_time_h < 6 or self.start_time_h > 9:
            self.start_time_h = round(np.random.normal(6.5, 1))

        self.start_time_m = np.random.randint(0, 12) * 5
        self.end_time_h = self.start_time_h + 8  # will work for 8 hours
        self.end_time_m = self.start_time_m

    def __repr__(self) -> str:
        return (
            #f"Commuter(unique_id={self.unique_id}, geometry={self.geometry}, status={self.status}, "
            f"Commuter(unique_id={self.unique_id}, geometry={self.geometry}"
        )

    def _prepare_to_move(self) -> None:
        # start going to work
        if (
            self.status == "at-home"
            and self.model.hour == self.start_time_h
            and self.model.minute == self.start_time_m
            and len(self.my_path) > 1
        ):
            self.origin = self.my_home
            self.model.space.move_commuter(self, pos=self.origin)
            self.destination = self.my_work
            self._path_select()
            self.status = "commuting"

        # start going home
        elif (
            self.status == "at-daytime-location"
            and self.model.hour == self.end_time_h
            and self.model.minute == self.end_time_m
            and len(self.my_path) > 1
        ):
            self.origin = self.my_work
            self.model.space.move_commuter(self, pos=self.origin)
            self.destination = self.my_home
            self._path_select()
            self.status = "commuting"
    def _path_select(self) -> None:
        self.step_in_path = 0
        self._redistribute_path_vertices()

    def _redistribute_path_vertices(self) -> None:
        # if origin and destination share the same entrance, then self.my_path
        # will contain only this entrance node,
        # and len(self.path) == 1. There is no need to redistribute path vertices.
        if len(self.my_path) > 1:
            #print("commuter->redis", self.unique_id, self.my_path)
            unit_transformer = UnitTransformer(degree_crs='epsg:4326')
            original_path = LineString([Point(p) for p in self.my_path])
            # from degree unit to meter
            path_in_meters = unit_transformer.degree2meter(original_path)
            redistributed_path_in_meters = redistribute_vertices(
                path_in_meters, self.SPEED
            )
            # meter back to degree
            redistributed_path_in_degree = unit_transformer.meter2degree(
                redistributed_path_in_meters
            )
            self.my_path = list(redistributed_path_in_degree.coords)

    def _move(self):
        if self.status == "commuting":
            if self.step_in_path < len(self.my_path):
                next_position = self.my_path[self.step_in_path]
                self.model.space.move_commuter(self, next_position)
                self.step_in_path += 1
            else:
                #self.model.space.move_commuter(self, self.destination.centroid)
                self.model.space.move_commuter(self, self.destination)
                #print(self.destination)
                #print(self.my_home)
                #print(self.my_work)
                #print(self.destination == self.my_work)
                #print(self.destination == self.my_home)
                if self.destination == self.my_work:
                    #print("at work")
                    self.status = "at-daytime-location"
                elif self.destination == self.my_home:
                    #print("back home")
                    self.status = "at-home"

                #self.model.got_to_destination += 1

    def step(self) -> None:
        self._prepare_to_move()
        self._move()
