from loguru import logger
import matplotlib as mpl
from matplotlib import animation
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from tqdm import tqdm

from src.model.model import BuffaloCommutingPatterns
from src.visualization.utils import plot_commuter_status_count, plot_commuters


def remove_duplicate_artist(
    artists: list[list[mpl.artist.Artist]],
) -> list[list[mpl.artist.Artist]]:
    new_artists = []
    artist_ids = set()
    for artist_list in artists:
        new_artist_list = []
        for artist in artist_list:
            if id(artist) not in artist_ids:
                new_artist_list.append(artist)
                artist_ids.add(id(artist))
        new_artists.append(new_artist_list)
    return new_artists


if __name__ == "__main__":

    road_file = "data/ub/shp_zip/ub_walkway_p.shp.zip"
    commuter_file = "data/ub/population/ub_population_full.shp.zip"

    logger.info("Starting model run...")
    logger.info(f"Road file: {road_file}")
    logger.info(f"Commuter file: {commuter_file}")

    model = BuffaloCommutingPatterns(
        data_crs="epsg:3857", #set crs here
        #data_crs= "epsg:4326",
        road_file=road_file,
        commuter_file=commuter_file,
        with_server=False,
    )

    population_filename = commuter_file.split("/")[-1].split(".")[0]
    fig, ax = plt.subplots(figsize=(7, 12))
    imgs = []
    imgs.append(plot_commuters(model, ax))
    for _ in tqdm(range(model.max_step), desc="Running model"):
        model.step()
        imgs.append(plot_commuters(model, ax))
    assert model.running == False
    logger.info("Model run completed.")
    plot_commuter_status_count(model)
    logger.info("Generating animation...")

    imgs = remove_duplicate_artist(imgs)
    ani = animation.ArtistAnimation(
        fig, imgs, interval=50, blit=True, repeat_delay=1000
    )
    ani.save(f"outputs/{population_filename}/commuters.gif", writer=PillowWriter(fps=5))
    logger.info(f"Plot and annimation saved to outputs/{population_filename}/")
