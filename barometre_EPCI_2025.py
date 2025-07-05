import contextlib
from io import StringIO

import sys
import EPCI
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as pl
import numpy as np
import pandas as pd
from matplotlib.offsetbox import (
    AnchoredOffsetbox,
    DrawingArea,
    HPacker,
    TextArea,
    VPacker,
)
from matplotlib.patches import Rectangle
from tqdm import tqdm

mpl.rcParams["text.color"] = "white"

pl.ion() # Enable interactive mode

epci = EPCI.all[sys.argv[1]] #Find EPCI by id
    
gdf_communes_shp = gpd.read_file("data/communes-20220101-shp")
gdf_2025 = gpd.read_file("data/barometre2025.json")
gdf_2025 = gdf_2025.drop("geometry", axis=1)

gdf_2025.rename(columns={"contributions": "contributions_2025"}, inplace=True)

gdf_2021 = gpd.read_file("data/barometre2021.json")
gdf_2021 = gdf_2021.drop("geometry", axis=1)

gdf_2021.rename(columns={"contributions": "contributions_2021"}, inplace=True)

gdf_communes = gdf_communes_shp.join(
    gdf_2021.set_index("insee"), on="insee", how="outer"
)
gdf_communes = gdf_communes.join(
    gdf_2025.set_index("insee").loc[:, ("contributions_2025","population")], on="insee", how="outer"
)


gdf_communes["contributions_2021"] = gdf_communes["contributions_2021"].fillna(0)
gdf_communes["contributions_2025"] = gdf_communes["contributions_2025"].fillna(0)


gdf_2025 = gdf_2025[gdf_2025["insee"].isin(epci.insee)]
gdf_2021 = gdf_2021[gdf_2021["insee"].isin(epci.insee)]


qualifs_2021= []
qualifs_2025 = []

qualifs = pd.DataFrame(
    columns=["qualifs_2021", "qualifs_2025", "diff"],
    dtype=float,
#    index=dep_ids,
)

lon_min, lat_min, lon_max, lat_max = [-5, 40.7, 10, 51.5]
ratio_dep = (lat_max - lat_min) / (lon_max - lon_min)


fig, ax = pl.subplots(
    1, 2, constrained_layout=True, figsize=(10, 10 * ratio_dep + 2)
)
fig.patch.set_facecolor((0.50, 0.51, 0.55))

gdf_communes[gdf_communes["contributions_2021"] == 0].plot(
    color=(0.58, 0.59, 0.63),
    ax=ax[0],
    edgecolor='none',
)
gdf_communes[
    (gdf_communes["contributions_2021"] > 0) & (gdf_communes["contributions_2021"] < 50)
].plot(
    color=(0.77, 0.18, 0.20),
    ax=ax[0],
    edgecolor='none',
)
gdf_communes[(gdf_communes["contributions_2021"] >= 50)].plot(
    color=(0.61, 0.87, 0.19),
    ax=ax[0],
    edgecolor='none',
)

gdf_communes[gdf_communes["contributions_2025"] == 0].plot(
    color=(0.58, 0.59, 0.63),
    ax=ax[1],
    edgecolor='none',
)
gdf_communes[
(( gdf_communes["contributions_2025"] < 50) & (gdf_communes["population"] > 5000)) | ((gdf_communes["contributions_2025"] < 30) & (gdf_communes["population"] <= 5000))
].plot(
    color=(0.77, 0.18, 0.20),
    ax=ax[1],
    edgecolor='none',
)
gdf_communes[(( gdf_communes["contributions_2025"] >= 50) & (gdf_communes["population"] > 5000)) | ((gdf_communes["contributions_2025"] >= 30) & (gdf_communes["population"] <= 5000))].plot(
        color=(0.61, 0.87, 0.19),
        ax=ax[1],
        edgecolor='none',
    )


ax[0].set_xlim([lon_min,lon_max])
ax[0].set_ylim([lat_min,lat_max])
ax[1].set_xlim([lon_min,lon_max])
ax[1].set_ylim([lat_min,lat_max])

ax[0].set_title(
    " Participation au Barometre Vélo \n\n  2021"
        # "Ile de France"
    ,
    loc="left",
    fontdict={"fontsize": "24"},
)
ax[1].set_title("\n\n  2025", loc="left", fontdict={"fontsize": "24"})

ax[0].set_axis_off()
ax[1].set_axis_off()
ax[0].set_aspect(1.3)
ax[1].set_aspect(1.3)
#pl.savefig("png/{}.png".format("France_metropolitaine"), dpi=300)

dep_id = 59

is_dep_59 = gdf_communes["insee"].isin(epci.insee)

gdf_dep = gdf_communes[is_dep_59]
    
lon_min, lat_min, lon_max, lat_max = gdf_dep.total_bounds
ratio_dep = (lat_max - lat_min) / (lon_max - lon_min)
fig, ax = pl.subplots(
    1, 2, constrained_layout=True, figsize=(10, 10 * ratio_dep + 2)
)
fig.patch.set_facecolor((0.50, 0.51, 0.55))

with contextlib.suppress(ValueError):
    gdf_dep[gdf_dep["contributions_2021"] == 0].plot(
        color=(0.58, 0.59, 0.63),
        ax=ax[0],
        edgecolor=(0.65, 0.67, 0.69),
    )
with contextlib.suppress(ValueError):
    gdf_dep[
        (gdf_dep["contributions_2021"] > 0) & (gdf_dep["contributions_2021"] < 50)
    ].plot(
        color=(0.77, 0.18, 0.20),
        ax=ax[0],
        edgecolor=(0.65, 0.67, 0.69),
    )
with contextlib.suppress(ValueError):
    gdf_dep[(gdf_dep["contributions_2021"] >= 50)].plot(
        color=(0.61, 0.87, 0.19),
        ax=ax[0],
        edgecolor=(0.65, 0.67, 0.69),
    )

with contextlib.suppress(ValueError):
    gdf_dep[gdf_dep["contributions_2025"] == 0].plot(
        color=(0.58, 0.59, 0.63),
        ax=ax[1],
        edgecolor=(0.65, 0.67, 0.69),
    )
with contextlib.suppress(ValueError):
    gdf_dep[
        (( gdf_dep["contributions_2025"] < 50) & (gdf_dep["population"] > 5000)) | ((gdf_dep["contributions_2025"] < 30) & (gdf_dep["population"] <= 5000))
    ].plot(
        color=(0.77, 0.18, 0.20),
        ax=ax[1],
        edgecolor=(0.65, 0.67, 0.69),
    )
with contextlib.suppress(ValueError):
    gdf_dep[(( gdf_dep["contributions_2025"] >= 50) & (gdf_dep["population"] > 5000)) | ((gdf_dep["contributions_2025"] >= 30) & (gdf_dep["population"] <= 5000))].plot(
        color=(0.61, 0.87, 0.19),
        ax=ax[1],
        edgecolor=(0.65, 0.67, 0.69),
    )

qualif_2021 = len(gdf_dep[(gdf_dep["contributions_2021"] >= 50)])
qualif_2025 = len(gdf_dep[(( gdf_dep["contributions_2025"] >= 50) & (gdf_dep["population"] > 5000)) | ((gdf_dep["contributions_2025"] >= 30) & (gdf_dep["population"] <= 5000))])
sup_zero_2021 = len(gdf_dep[(gdf_dep["contributions_2021"] > 0)])
sup_zero_2025 = len(gdf_dep[(gdf_dep["contributions_2025"] > 0)])

qualifs_2021.append(qualif_2021)
qualifs_2025.append(qualif_2025)

qualifs.loc[dep_id, 'qualifs_2021'] = qualif_2021
qualifs.loc[dep_id, 'qualifs_2025'] = qualif_2025
qualifs.loc[dep_id, 'diff'] = qualif_2025 - qualif_2021
ax[0].set_title(
    f" Barometre Vélo : {epci.name}\n\n  2021"
#    .format(
#        df_dep[df_dep["N° du dép."] == dep_id][
#            "Nom du département"
#        ].values[0]
#        # "Ile de France"
#    )
    ,
    loc="left",
    fontdict={"fontsize": "24"},
)
ax[1].set_title("\n\n  2025", loc="left", fontdict={"fontsize": "24"})

ax[0].set_axis_off()
ax[1].set_axis_off()

box_text_reponses = TextArea(
    f"Communes : {epci.nbr_communes} ", textprops=dict(color="w", size=16)
)
box_text_red = TextArea(
    f"   au moins une réponse : {sup_zero_2021} ",
    textprops=dict(color="w", size=16),
)
box_draw_red = DrawingArea(20, 20, 0, 0)
rect = Rectangle((2, 2), width=16, height=16, angle=0, fc=(0.77, 0.18, 0.20))
box_draw_red.add_artist(rect)
box_red = HPacker(
    children=[box_draw_red, box_text_red],
    align="center",
    pad=0,
    sep=0,
    mode="fixed",
)

box_text_green = TextArea(
    f"   qualifiées : {qualif_2021} ", textprops=dict(color="w", size=16)
)
box_draw_green = DrawingArea(20, 20, 0, 0)
rect = Rectangle((2, 2), width=16, height=16, angle=0, fc=(0.61, 0.87, 0.19))
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
    bbox_transform=ax[0].transAxes,
    borderpad=0.0,
)
ax[0].add_artist(anchored_box)

box_text_reponses = TextArea(
    f"Communes : {epci.nbr_communes} ", textprops=dict(color="w", size=16)
)

box_text_commune = TextArea(
    f"Communes : ", textprops=dict(color="w", size=16)
)

box_text_red = TextArea(
    f"   au moins une réponse : {sup_zero_2025} ",
    textprops=dict(color="w", size=16),
)
box_draw_red = DrawingArea(20, 20, 0, 0)
rect = Rectangle((2, 2), width=16, height=16, angle=0, fc=(0.77, 0.18, 0.20))
box_draw_red.add_artist(rect)
box_red = HPacker(
    children=[ box_draw_red, box_text_red],
    align="center",
    pad=0,
    sep=0,
    mode="fixed",
)

box_text_green = TextArea(
    f"   qualifiées : {qualif_2025} ", textprops=dict(color="w", size=16)
)
box_draw_green = DrawingArea(20, 20, 0, 0)
rect = Rectangle((2, 2), width=16, height=16, angle=0, fc=(0.61, 0.87, 0.19))
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
    bbox_transform=ax[1].transAxes,
    borderpad=0.0,
)
ax[1].add_artist(anchored_box)
pl.savefig(f"png/{epci.id}.png", dpi=300)

qualifs["diff"] = qualifs["qualifs_2025"] - qualifs["qualifs_2021"]
try:
    qualifs["relatif"] = qualifs["qualifs_2025"].divide(qualifs["qualifs_2021"])
except ZeroDivisionError:
    qualifs["relatif"] = np.nan
qualifs.to_csv('outputs/commune_qualif.csv')


