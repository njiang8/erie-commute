Buffalo Commuting Patterns Model
================================

## Introduction
In this simple example we demonstrate how we can utilize both agents' home and work locations as input parameters to initialize a model of commuting stylized on Erie County, NY. In the sense, agents start their day at home and if they have a workplace assigned to them they will travel to their work in the morning and return home in the evening along a road network by taking the shortest path which is shown in the Figure below. As such, the model collects results on agents' locational changes and captures basic daily routine (e.g., from home to work, work to home) along with basic traffic dynamics. This simple model could be extended to have more activities such as going for lunch, shopping etc., informed by surveys (e.g., the [National Household travel survey](https://nhts.ornl.gov/)),

![A simple example of agents driving to and from work, stylized on Erie County, NY.
](buffalo_commute.png "A simple example of agents driving to and from work, stylized on Erie County, NY.
")


## How to run

First install the dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Then run the model:

```bash
mesa runserver
```

Open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press `Start`.

To run the model with no visualization, run the following command:

```bash
python3 run_without_server.py
```

Resulting plots will be saved in the `outputs` folder.
