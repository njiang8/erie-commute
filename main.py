# This is a sample Python script.
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from tqdm.auto import tqdm
import mesa
import mesa_geo as mg
from src.model.model import ErieCommuteModel

from src.visualization.server import (
    agent_draw,
    clock_element,
    status_chart,
)

LUCH = False

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("main->running...")
    model_params = {
        #"population_file": 'data/population/small_test_pop_with_path.csv',
        "population_file" : 'data/population/test_pop_with_path.csv',
        "data_crs": 'epsg:4326',
        #"buildings_file": f"data/shp_zip/single_bldings.zip",
        #"buildings_file": f"data/shp/UB_bld.zip",
        #"walkway_file":   f"data/shp_zip/ub_walkway_clean.zip",
        #"lakes_file":     f"data/shp_zip/hydrop.zip",
        #"rivers_file":    f"data/shp_zip/hydrol.zip",
        "driveway_file":  f"data/shp/Road_Clean.zip",
        #"show_walkway": False,
        #"show_driveway": True,
        #"show_lakes_and_rivers": False,
        "commuter_speed": mesa.visualization.Slider(
            "Commuter Walking Speed (m/s)",
            value=0.5,
            min_value=0.1,
            max_value=1.5,
            step=0.1,
        ),
    }

    if LUCH == True:
        map_element = mg.visualization.MapModule(agent_draw, map_height=800, map_width=600)
        server = mesa.visualization.ModularServer(
            ErieCommuteModel,
            [clock_element, status_chart],
            # [map_element, clock_element, status_chart],
            "Erie Commute Model",
            model_params,
        )
        server.launch()
    else:
        print("No server~")
        model = ErieCommuteModel(**model_params)

        for _ in tqdm(range(240)):
            model.step()

        model_results = model.datacollector.get_model_vars_dataframe()
        model_results.to_csv('test_output_1.csv')
        print(model_results.head())
        print("Done!")
