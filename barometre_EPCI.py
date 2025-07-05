import contextlib
from io import StringIO
from PIL import Image
import os
import sys
import EPCI
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as pl
import numpy as np
import matplotlib.image as mpimg
import pandas as pd
import numpy as np
import matplotlib.cbook as cbook
from matplotlib.offsetbox import (
    AnchoredOffsetbox,
    DrawingArea,
    HPacker,
    TextArea,
    VPacker,
)
from matplotlib.patches import Rectangle
from tqdm import tqdm


mpl.rcParams["text.color"] = "black"   # default lebel color

pl.ion() # Enable interactive mode

epci = EPCI.all[sys.argv[1]] #Find EPCI by id
year = sys.argv[2] if len(sys.argv) > 2 else "2025"
kind = sys.argv[3] if len(sys.argv) > 3 else "reponses"
    
gdf_communes_shp = gpd.read_file("data/communes-20220101-shp")
if(year == "2021"):
    gdf = gpd.read_file("data/barometre2021.json")
else:
    gdf = gpd.read_file("data/barometre2025.json")

gdf.rename(columns={"geometry": "coords"}, inplace=True)

if(year == "2021"):
    gdf_communes = gdf_communes_shp.join(
        gdf.set_index("insee").loc[:, ("contributions", "coords", "per_cent")], on="insee", how="outer"
    )
else:    
    gdf_communes = gdf_communes_shp.join(
        gdf.set_index("insee").loc[:, ("contributions","population", "coords", "per_cent")], on="insee", how="outer"
    )

gdf_communes["contributions"] = gdf_communes["contributions"].fillna(0)

NO_RESPONSE = (1.0, 0.98, 0.98)
AT_LEAST_ONE= (0.77, 0.18, 0.20)
QUALIFIED = (0.61, 0.87, 0.19)
BACKGROUNG = (1.0, 0.98, 0.98)
TITLE = "#000000"
SUB_TITLE = "mediumblue"
EDGE_COLOR = (0.0, 0.0, 0.0)

gdf = gdf[gdf["insee"].isin(epci.insee)]


lon_min, lat_min, lon_max, lat_max = [-5, 40.7, 10, 51.5]
ratio_dep = (lat_max - lat_min) / (lon_max - lon_min)

is_epci = gdf_communes["insee"].isin(epci.insee)

gdf_dep = gdf_communes[is_epci]
    
lon_min, lat_min, lon_max, lat_max = gdf_dep.total_bounds
ratio_dep = (lat_max - lat_min) / (lon_max - lon_min)
fig, ax = pl.subplots(
    1, 1, constrained_layout=True, figsize=(11.7, 8.3)
)

fig.patch.set_facecolor(BACKGROUNG)

with contextlib.suppress(ValueError):
    gdf_dep[gdf_dep["contributions"] == 0].plot(
        color=(NO_RESPONSE),
        ax=ax,
        edgecolor=(EDGE_COLOR),
    )
if(year == "2021"):
    pas_qualifiees = gdf_dep[
            (gdf_dep["contributions"] > 0) & (gdf_dep["contributions"] < 50)
        ]   
    qualifiees = gdf_dep[
        (gdf_dep["contributions"] >= 50 )
    ]
else: 
    pas_qualifiees = gdf_dep[
            (( gdf_dep["contributions"] < 50) & (gdf_dep["population"] > 5000)) | ((gdf_dep["contributions"] < 30) & (gdf_dep["population"] <= 5000))
        ]   
    qualifiees = gdf_dep[
        (( gdf_dep["contributions"] >= 50) & (gdf_dep["population"] > 5000)) | ((gdf_dep["contributions"] >= 30) & (gdf_dep["population"] <= 5000))
    ]

with contextlib.suppress(ValueError):
    pas_qualifiees.plot(
        color=(AT_LEAST_ONE),
        ax=ax,
        edgecolor=(EDGE_COLOR),
        alpha=0.7
    )

with contextlib.suppress(ValueError):
    qualifiees.plot(
        color=(QUALIFIED),
        ax=ax,
        edgecolor=(EDGE_COLOR),
        alpha=0.7
    )

au_moins_une = pd.concat([pas_qualifiees, qualifiees])

for idx, row in au_moins_une.iterrows():
    if row['coords'] is not None:
       numvar = row['per_cent']
       if kind == "taux":
           numvar = row['per_cent']
           texte = row['nom']+"\n"+  f'{numvar:.3f} %'
       else:
           texte = row['nom']+"\n" + str(int(row['contributions']))
       ax.annotate(text=texte,xy=(row['coords'].x,row['coords'].y),horizontalalignment='center',
            verticalalignment='center', fontsize=6, color="mediumblue")

ax.set_title(
    f"Participation Baromètre Vélo : {epci.name}\n\n  {year}",
    loc="center",
    fontdict={"fontsize": "22", "color": TITLE},
)

ax.set_axis_off()

box_text_reponses = TextArea(
    f"Communes : {len(epci.insee)} ", textprops=dict(color=SUB_TITLE, size=16)
)

box_text_red = TextArea(
    f"   au moins une réponse : {len(au_moins_une)} ",
    textprops=dict(color=SUB_TITLE, size=16),
)
box_draw_red = DrawingArea(20, 20, 0, 0)
rect = Rectangle((2, 2), width=16, height=16, angle=0, fc=(AT_LEAST_ONE))
box_draw_red.add_artist(rect)
box_red = HPacker(
    children=[ box_draw_red, box_text_red],
    align="center",
    pad=0,
    sep=0,
    mode="fixed",
)

box_text_green = TextArea(
    f"   qualifiées : {len(qualifiees)} ", textprops=dict(color=SUB_TITLE, size=16)
)
box_draw_green = DrawingArea(20, 20, 0, 0)
rect = Rectangle((2, 2), width=16, height=16, angle=0, fc=(QUALIFIED))
box_draw_green.add_artist(rect)
box_green = HPacker(
    children=[box_draw_green, box_text_green],
    align="center",
    pad=0,
    sep=0,
    mode="fixed",
)

box = VPacker(
    children=[box_text_reponses, box_green, box_red],
    align="left",
    pad=0,
    sep=4,
    mode="fixed",
)
anchored_box = AnchoredOffsetbox(
    loc="upper center",
    child=box,
    pad=0.0,
    frameon=False,
    bbox_to_anchor=(0.4, 0),
    bbox_transform=ax.transAxes,
    borderpad=0.0,
)
ax.add_artist(anchored_box)

if not os.path.isdir(f"png/{epci.id}"):
    os.makedirs(f"png/{epci.id}")

pl.savefig(f"png/{epci.id}/{kind}_{year}.png", dpi=300)



