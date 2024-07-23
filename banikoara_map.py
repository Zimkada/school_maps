# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 00:21:45 2024

@author: ok
"""

#Importation des bibliothèques
import pandas as pd
import folium
from geopy.distance import geodesic
import geopandas as gpd

#Chargement des coordonnées géo

df = pd.read_excel("geo_data.xlsx")
print("Coordonnées géo chargées avec succès")

#Création d'une carte centrée sur la commune de Banikoara
map_center = [11.3000, 2.4333]
map_bnk = folium.Map(location = map_center,zoom_start = 8)#,tiles='CartoDB positron')

#Coordonnées des limites de la carte
bounds = [[11.2500, 2.3800], [11.3500, 2.4800]]

# Définir les limites de la carte
map_bnk.fit_bounds(bounds)

# Placement des collèges sur la carte
for index, row in df.iterrows():
    folium.Marker(location = [row['Y'], row['X']],
                  tooltip=row['NOM'],
                  icon=folium.Icon(icon='user-graduate', prefix='fa')).add_to((map_bnk))
    

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
                  icon=folium.DivIcon(html='<div style="font-size:24px; color: red;">&#9679;</div>')
                  ).add_to(map_bnk)

    
#Enregistrer la carte
map_bnk.save("Carto_Banikoara.html")