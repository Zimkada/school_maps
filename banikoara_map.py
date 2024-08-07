# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 00:21:45 2024

@author: ok
"""

#Importation des bibliothèques
import pandas as pd
import matplotlib.pyplot as plt
import folium
from geopy.distance import geodesic
import geopandas as gpd
import base64
from io import BytesIO
from ipywidgets import widgets, interact
from IPython.display import display, HTML
import streamlit as st
from streamlit_folium import st_folium


#Chargement des coordonnées géo

df = pd.read_excel("geo_data.xlsx")
print("Coordonnées géo chargées avec succès")

#Création d'une carte centrée sur la commune de Banikoara
map_center = [11.3000, 2.4333]
map_bnk = folium.Map(location = map_center,zoom_start = 8)#,tiles='CartoDB positron')

#Coordonnées des limites de la carte
bounds = [[11.2500, 2.3800], [11.3500, 2.4800]]

# Ajouter des tuiles Google Maps
folium.TileLayer(
    tiles='http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attr='Google',
    name='Google Maps',
    max_zoom=20,
    subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
).add_to(map_bnk)


# Définir les limites de la carte
map_bnk.fit_bounds(bounds)

def create_graph(row):
    labels = ['EFF_M', 'EFF_F']
    sizes = [row['EFF_M'], row['EFF_F']]
    colors = ['#ff9999','#66b3ff']
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(f"Effectifs de {row['NOM']}")
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return f'data:image/png;base64,{img_base64}'



# Placement des collèges sur la carte
for index, row in df.iterrows():
    # Marqueur avec icône en forme de goutte d'eau
    folium.Marker(
        location=[row['Y'], row['X']],
        tooltip=row['NOM'],
        icon=folium.Icon(icon='user-graduate', prefix='fa')
    ).add_to(map_bnk)
    
    # Label avec les effectifs et le nom du collège
    folium.Marker(
        location=[row['Y'], row['X']],
        icon=folium.DivIcon(
            html=f'<div style = "font-family: Arial, sans-serif; font-size:12px; front-weight = bold; front-style = italic; color: red; background-color: white; opacity = 0.8; text-decoration = underline; text-align: left; border: 1px solid black;"> {row["EFF"]}<br>{row["NOM"]}</div>',
            icon_size=(100, 30)
        )
    ).add_to(map_bnk)


    # Graphique des effectifs
#    graph_data = create_graph(row)
#    folium.Marker(
#        location=[row['Y'], row['X']],
#        icon=folium.DivIcon(
#            html=f'<img src="{graph_data}" style="width: 100px; height: 100px;">'
#        )
#    ).add_to(map_bnk)


    #Création de la zone de couverture de chaque collège (rayon de 5km)
    folium.Circle(location=[row['Y'],row['X']],radius=5000, color ='blue', 
                  fill_opacity=0.1).add_to(map_bnk)
                   
# Chargement des données du shapefile
shapefile_path = "C:/Users/ok/school_maps/couches/ecole.shp"
gdf = gpd.read_file(shapefile_path)

# Vérification du système de coordonnées (CRS)
print(gdf.crs)

# Reprojection vers WGS84 (EPSG:4326)
gdf = gdf.to_crs(epsg=4326)


# Ajout des écoles primaires sur la carte

for idx, row in gdf.iterrows():
    point = row.geometry
    folium.Marker(location=[point.y, point.x],
                  tooltip = row['FID'],
                  icon=folium.DivIcon(html='<div style="font-size:24px; color: yellow;">&#9679;</div>')
                  ).add_to(map_bnk)

    
#Enregistrer la carte
map_bnk.save("Carto_Banikoara.html")

# Interface Streamlit
st.title("Carte des collèges de Banikoara et calcul de distance")

# Affichage de la carte
st_data = st_folium(map_bnk, width=700, height=500)

# Ajout de la fonctionnalité de calcul de distance
college_options = df['NOM'].tolist()

depart = st.selectbox('Collège de départ:', college_options)
arrivee = st.selectbox('Collège d\'arrivée:', college_options)

if st.button('Calculer la distance'):
    if depart and arrivee:
        coord_depart = df[df['NOM'] == depart][['Y', 'X']].values[0]
        coord_arrivee = df[df['NOM'] == arrivee][['Y', 'X']].values[0]
        distance = geodesic(coord_depart, coord_arrivee).km
        st.write(f"Distance entre {depart} et {arrivee} : {distance:.2f} km")
    else:
        st.warning("Sélectionnez deux collèges")
