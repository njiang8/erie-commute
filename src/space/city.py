import mesa
import mesa_geo as mg
from shapely.geometry import Point

from src.agent.commuter import Commuter


class City(mg.GeoSpace):
    def __init__(self, crs: str) -> None:
        super().__init__(crs=crs)

    def move_commuter(
        self, commuter: Commuter, pos: mesa.space.FloatCoordinate
    ) -> None:
        super().remove_agent(commuter)
        commuter.geometry = Point(pos)
        super().add_agents([commuter])
