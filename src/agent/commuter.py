from __future__ import annotations

import mesa
import mesa_geo as mg
import numpy as np
import pyproj
from shapely.geometry import LineString, Point

from src.space.utils import UnitTransformer, redistribute_vertices


class Commuter(mg.GeoAgent):
    unique_id: int  # commuter_id, used to link commuters and nodes
    model: mesa.Model
    geometry: Point
    crs: pyproj.CRS
    origin: mesa.space.FloatCoordinate  # where he begins his trip
    destination: mesa.space.FloatCoordinate  # the destination he wants to arrive at
    my_path: list[
        mesa.space.FloatCoordinate
    ]  # a set containing nodes to visit in the shortest path
    location_history: list[
        mesa.space.FloatCoordinate
    ]  # a set containing all the nodes the commuter has visited
    status_history: list[str]  # a set containing all the status the commuter has had
    step_in_path: int  # the number of step taking in the walk
    my_home: mesa.space.FloatCoordinate
    my_work: mesa.space.FloatCoordinate
    start_time_h: int  # time to start going to work, hour and minute
    start_time_m: int
    end_time_h: int  # time to leave work, hour and minute
    end_time_m: int
    status: str  # work, home, or transport
    SPEED: float

    def __init__(self, unique_id, model, geometry, crs) -> None:
        super().__init__(unique_id, model, geometry, crs)
        self.my_home = None
        self.start_time_h = round(np.random.normal(6.5, 1))
        while self.start_time_h < 6 or self.start_time_h > 9:
            self.start_time_h = round(np.random.normal(6.5, 1))
        self.start_time_m = np.random.randint(0, 12) * 5
        self.end_time_h = self.start_time_h + 8  # will work for 8 hours
        self.end_time_m = self.start_time_m
        self.location_history = []
        self.status_history = []

    def __repr__(self) -> str:
        return (
            f"Commuter(unique_id={self.unique_id}, geometry={self.geometry}, "
            f"status={self.status}"
        )

    def step(self) -> None:
        self._prepare_to_move()
        self._move()

        self.location_history.append((self.geometry.x, self.geometry.y))
        self.status_history.append(self.status)

    def _prepare_to_move(self) -> None:
        # start going to work
        if (
            self.status == "home"
            and self.model.hour == self.start_time_h
            and self.model.minute == self.start_time_m
        ):
            self.origin = self.my_home
            if self.model.with_server:
                self.model.space.move_commuter(self, pos=self.origin)
            else:
                self.geometry = Point(self.origin)
            self.destination = self.my_work
            self._path_select()
            self.status = "transport"
        # start going home
        elif (
            self.status == "work"
            and self.model.hour == self.end_time_h
            and self.model.minute == self.end_time_m
        ):
            self.origin = self.my_work
            if self.model.with_server:
                self.model.space.move_commuter(self, pos=self.origin)
            else:
                self.geometry = Point(self.origin)
            self.destination = self.my_home
            self._path_select()
            self.status = "transport"

    def _move(self) -> None:
        if self.status == "transport":
            if self.step_in_path < len(self.my_path):
                next_position = self.my_path[self.step_in_path]
                if self.model.with_server:
                    self.model.space.move_commuter(self, next_position)
                else:
                    self.geometry = Point(next_position)
                self.step_in_path += 1
            else:
                if self.model.with_server:
                    self.model.space.move_commuter(self, self.destination)
                else:
                    self.geometry = Point(self.destination)
                if self.destination == self.my_home:
                    self.status = "home"
                if self.destination == self.my_work:
                    self.status = "work"

    def _path_select(self) -> None:
        self.step_in_path = 0
        if (
            cached_path := self.model.road.get_cached_path(
                source=self.origin, target=self.destination
            )
        ) is not None:
            self.my_path = cached_path
        else:
            self.my_path = self.model.road.get_shortest_path(
                source=self.origin, target=self.destination
            )
            self.model.road.cache_path(
                source=self.origin,
                target=self.destination,
                path=self.my_path,
            )
        self._redistribute_path_vertices()

    def _redistribute_path_vertices(self) -> None:
        # if origin and destination share the same entrance, then self.my_path
        # will contain only this entrance node,
        # and len(self.path) == 1. There is no need to redistribute path vertices.
        if len(self.my_path) > 1:
            original_path = LineString([Point(p) for p in self.my_path])
            redistributed_path = redistribute_vertices(original_path, self.SPEED)
            self.my_path = list(redistributed_path.coords)
