import contextlib
from io import StringIO

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as pl
import numpy as np
import pandas as pd
import requests  # library to handle requests
from bs4 import BeautifulSoup  # library to parse HTML documents
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

pl.ion()

wikiurl = "https://fr.wikipedia.org/wiki/Nombre_de_communes_par_département_en_France_au_1er_janvier_2014"
table_class = "wikitable sortable jquery-tablesorter"
response = requests.get(wikiurl)
soup = BeautifulSoup(response.text, "html.parser")
dep_table = soup.find("table", {"class": "wikitable"})
df_dep = pd.read_html(StringIO(str(dep_table)))
# convert list to dataframe
df_dep = pd.DataFrame(df_dep[0])
df_dep = df_dep.drop(
    [ "Rang", "Population municipale en 2011[2],[3]", "Moyenne d'habitants par commune"], axis=1
)
# Nettoyage trailing [4] pour Mayotte
df_dep.loc[df_dep["N° du dép."] == "976", "Nom du département"] = "Mayotte"

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

#dep_ids = [str(idep).zfill(2) for idep in range(1, 20)]
#dep_ids.append("2A")
#dep_ids.append("2B")
#for idep in range(21, 96):
#    dep_ids.append(str(idep).zfill(2))
#dep_ids.append("971")
#dep_ids.append("972")
#dep_ids.append("973")
#dep_ids.append("974")
#dep_ids.append("976")
dep_ids = list()
dep_ids.append("59")
dep_ids.append("62")

qualifs_2021= []
qualifs_2025 = []

qualifs = pd.DataFrame(
    columns=["qualifs_2021", "qualifs_2025", "diff"],
    dtype=float,
    index=dep_ids,
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
pl.savefig("png/{}.png".format("France_metropolitaine"), dpi=300)

dep_id = 59
#for idep in tqdm(dep_ids):
#    dep_id = idep
#    print("idep", idep)
#    print("dep_id", dep_id)
is_dep_59 = gdf_communes["insee"].str.startswith(str("59"))
is_dep_62 = gdf_communes["insee"].str.startswith(str("62"))
    #is_dep = gdf_communes["insee"].str.startswith("59")
    #print("is_dep", type(is_dep))
gdf_dep_59 = gdf_communes[is_dep_59]
gdf_dep_62 = gdf_communes[is_dep_62]
#print("gdf_dep", type(gdf_dep_59)) 
gdf_dep = pd.concat([gdf_dep_59, gdf_dep_62])

print("gdf_dep", gdf_dep)
    
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
    " Participation au Barometre Vélo : Nord & Pas-de-Calais\n\n  2021"
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
    f"Nombre de réponses : 11 318 \nCommunes : ", textprops=dict(color="w", size=16)
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
    f"Nombre de réponses : 16 942  \nCommunes : ", textprops=dict(color="w", size=16)
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
pl.savefig(f"png/{dep_id}.png", dpi=300)

qualifs["diff"] = qualifs["qualifs_2025"] - qualifs["qualifs_2021"]
try:
    qualifs["relatif"] = qualifs["qualifs_2025"].divide(qualifs["qualifs_2021"])
except ZeroDivisionError:
    qualifs["relatif"] = np.nan
qualifs.to_csv('outputs/commune_qualif.csv')


#with open("outputs/tweets.txt", "w") as f:
#    for idep in tqdm(dep_ids):
#        dep_id = idep
#        is_dep = gdf_communes["insee"].str.startswith(str(dep_id))
#        gdf_dep = gdf_communes[is_dep]
#        f.write(
#            "Évolution de la participation 2019-2021 au Baromètre Vélo organisé par @FUB_fr\n\n"
#        )
#
#
#        qualif_2025 = qualifs.loc[dep_id, "qualifs_2025"]
#        qualif_2021 = qualifs.loc[dep_id, "qualifs_2021"]
#
#        if (qualif_2025 - qualif_2021) < -1:
#            f.write(
#                "{:}: {:0.0f} communes qualifiées en moins".format(
#                    df_dep[df_dep["N° du dép."] == dep_id][
#                        "Nom du département"
#                    ].values[0],
#                    -(qualif_2025 - qualif_2021),
#                )
#            )
#
#        elif (qualif_2025 - qualif_2021) == -1:
#            f.write(
#                "{:}: {:0.0f} commune qualifiée en moins".format(
#                    df_dep[df_dep["N° du dép."] == dep_id][
#                        "Nom du département"
#                    ].values[0],
#                    -(qualif_2025 - qualif_2021),
#                )
#            )
#
#        elif (qualif_2025 - qualif_2021) == 0:
#            f.write(
#                "{:}: pas de commune qualifiée en plus".format(
#                    df_dep[df_dep["N° du dép."] == dep_id][
#                        "Nom du département"
#                    ].values[0]
#                )
#            )
#
#        elif (qualif_2025 - qualif_2021) == 1:
#            f.write(
#                "{:}: {:0.0f} commune qualifiée en plus".format(
#                    df_dep[df_dep["N° du dép."] == dep_id][
#                        "Nom du département"
#                    ].values[0],
#                    (qualif_2025 - qualif_2021),
#                )
#            )
#        else:
#            f.write(
#                "{:}: {:0.0f} communes qualifiées en plus".format(
#                    df_dep[df_dep["N° du dép."] == dep_id][
#                        "Nom du département"
#                    ].values[0],
#                    (qualif_2025 - qualif_2021),
#                )
#            )
#
#        if (qualif_2025 - qualif_2021)<0:
#            emoji = "☹️"
#        if (qualif_2025 - qualif_2021)==0:
#            emoji = "😕"
#        if ((qualif_2025 - qualif_2021)>0) and ((qualif_2025 - qualif_2021)<=6):
#            emoji = "🙌"
#        if ((qualif_2025 - qualif_2021)>6) and ((qualif_2025 - qualif_2021)<=11):
#            emoji = "🥳😊"
#        if ((qualif_2025 - qualif_2021)>11) and ((qualif_2025 - qualif_2021)<=21):
#            emoji = "👍🎊"
#        if ((qualif_2025 - qualif_2021)>21) and ((qualif_2025 - qualif_2021)<=51):
#            emoji = "🎉🤩"
#        if ((qualif_2025 - qualif_2021)>51):
#            emoji = "👈👏🤯"
#
#        qualifs.sort_values(by='diff', ascending=False, inplace=True)
#        medaille = ''
#        if (qualif_2025 - qualif_2021) == qualifs.iloc[0]['diff']:
#            medaille = 'Meilleure progression 🥇'
#        elif (qualif_2025 - qualif_2021) == qualifs.iloc[1]['diff']:
#            medaille = '2ème meilleure progression 🥈'
#        elif (qualif_2025 - qualif_2021) == qualifs.iloc[2]['diff']:
#            medaille = '3ème meilleure progression 🥉'
#        elif (qualif_2025 - qualif_2021) == qualifs.iloc[3]['diff']:
#            medaille = '4ème meilleure progression 🍫'
#
#        f.write(f" {emoji}")
#        if medaille:
#            f.write(f"\n\n{medaille}")
#
#        f.write("\n\n\n")
#
#        pl.close()
