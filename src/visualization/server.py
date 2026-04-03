import mesa
import mesa_geo as mg

from src.agent.commuter import Commuter
from src.agent.geo_agents import Road
from src.model.model import BuffaloCommutingPatterns


class ClockElement(mesa.visualization.TextElement):
    def __init__(self):
        super().__init__()
        pass

    def render(self, model):
        return f"Day {model.day}, {model.hour:02d}:{model.minute:02d}"


model_params = {
    "data_crs": "epsg:3857",
    "commuter_file": "data/erie/population/work_population_sample_1.shp.zip",
    "road_file": "data/erie/shp_zip/erie_road_p.shp.zip",
    "show_road": mesa.visualization.Checkbox("Show Road", value=False),
    "commuter_speed": mesa.visualization.Slider(
        "Commuter Moving Speed (multiples of 12km/h)",
        value=1.0,
        min_value=0.1,
        max_value=3.0,
        step=0.1,
    ),
}


def agent_draw(agent):
    portrayal = {}
    portrayal["color"] = "White"
    if isinstance(agent, Road):
        portrayal["color"] = "Brown"
    elif isinstance(agent, Commuter):
        if agent.status == "home":
            portrayal["color"] = "Green"
        elif agent.status == "work":
            portrayal["color"] = "Blue"
        elif agent.status == "transport":
            portrayal["color"] = "Red"
        else:
            portrayal["color"] = "Grey"
        portrayal["radius"] = "5"
        portrayal["fillOpacity"] = 1
    return portrayal


clock_element = ClockElement()
status_chart = mesa.visualization.ChartModule(
    [
        {"Label": "status_home", "Color": "Green"},
        {"Label": "status_work", "Color": "Blue"},
        {"Label": "status_traveling", "Color": "Red"},
    ],
    data_collector_name="datacollector",
)

map_element = mg.visualization.MapModule(agent_draw, map_height=600, map_width=600)
server = mesa.visualization.ModularServer(
    BuffaloCommutingPatterns,
    [map_element, clock_element, status_chart],
    "Urban Commuting in Buffalo",
    model_params,
)
