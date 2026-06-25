import datetime
import os

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as cx

from src.model.model import BuffaloCommutingPatterns


def plot_commuter_status_count(model: BuffaloCommutingPatterns) -> None:
    #from pathlib import Path
    import os

    commuter_status_df = model.datacollector.get_model_vars_dataframe()
    population_filename = model.commuter_file.split("/")[-1].split(".")[0]
    #print("in plot_commuter_status_count", population_filename)

    # Save PDF and CSV files
    directory_path = f"outputs/{population_filename}"
    # Ensure the directory exists
    os.makedirs(directory_path, exist_ok=True)  # `exist_ok=True` avoids error if directory already exists

    # Define file paths
    #pdf_file_path = os.path.join(directory_path, "commuter_status_count.pdf")
    csv_file_path = os.path.join(directory_path, "commuter_status.csv")
    commuter_status_df.to_csv(csv_file_path, index=False)

    output_file = f"outputs/{population_filename}/commuter_status_count.pdf"

    # Save PDF and CSV files
    # Assuming the code to generate the PDF file goes here and saves the PDF to `pdf_file_path`
    #commuter_status_df.to_csv(csv_file_path, index=False)  # Save CSV, ensuring no extra spaces in the path

    # directory_path = f"outputs/{population_filename}"
    # if not os.path.exists(directory_path):
    #     # If the directory does not exist, create it
    #     os.makedirs(directory_path)
    #     output_file = f"outputs/{population_filename}/commuter_status_count.pdf"
    #     commuter_status_df.to_csv(f"outputs/{population_filename}/ commuter_status.csv", index=False)
    #
    # else:
    #     output_file = f"outputs/{population_filename}/commuter_status_count.pdf"
    #     commuter_status_df.to_csv(f"outputs/{population_filename}/ commuter_status.csv", index=False)


    commuter_status_df = commuter_status_df.rename(
        columns=lambda x: x.replace("status_", "")
    )
    commuter_status_df["time"] = commuter_status_df["time"] / pd.Timedelta(minutes=1)
    commuter_status_df = commuter_status_df.melt(
        id_vars=["time"],
        value_vars=["home", "traveling", "work"],
        var_name="Status",
        value_name="Count",
    )
    commuter_status_df.rename(columns={"time": "Time"}, inplace=True)

    sns.relplot(
        x="Time",
        y="Count",
        data=commuter_status_df,
        kind="line",
        hue="Status",
        aspect=1.5,
    )
    plt.xticks(np.arange(360.0, 1440.0, 120.0))
    plt.gca().xaxis.set_major_formatter(
        lambda x, pos: ":".join(str(datetime.timedelta(minutes=x)).split(":")[:2])
    )
    plt.gca().yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
    plt.title("Number of Commuters by Status")

    output_dir = "/".join(output_file.split("/")[:-1])
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(output_file, bbox_inches="tight")


def plot_commuters(
    model: BuffaloCommutingPatterns, ax: mpl.axes
    ) -> list[mpl.artist.Artist]:

    commuters_gdf = model.get_agents_as_GeoDataFrame()#todo add road water, buiding here
    commuters_gdf = commuters_gdf[["geometry", "status"]]

    #commuters_gdf.to_file("commuters_gdf_test.shp")

    color_map = dict(zip(["home", "transport", "work"], plt.cm.Set2.colors[:3]))
    commuters_gdf["color"] = commuters_gdf["status"].map(color_map)

    #to crs is due to the iput file is in WGS84, but the based map is requier to use 3857
    #commuters_gdf.crs = "epsg:4326"
    #commuters_gdf.to_crs(epsg=3857).plot(
    commuters_gdf.plot(
        color=commuters_gdf["color"],
        marker="o",
        markersize=1,
        alpha=0.7,
        aspect="equal",
        ax=ax,
    )
    ax.set_axis_off()
    title = ax.text(
        0.01,
        1.01,
        f"Number of Commuters: {len(commuters_gdf):,}\n\nTime: {model.hour:02d}:{model.minute:02d}",
        ha="left",
        va="bottom",
        size=12,
        transform=ax.transAxes,
    )
    cx.add_basemap(ax, source=cx.providers.CartoDB.Positron)
    return [*ax.get_children(), title]
