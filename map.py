# import plotly.express as px
# import geopandas as gpd
# from geopandas import GeoDataFrame as geodf


# import geopandas as gpd

# shapefile = gpd.read_file("C:\\Users\\putos\\Documents\\Data Visualization\\jira_dash_board_app_2\\moz_adm_20190607b_shp\\moz_admbnda_adm1_ine_20190607.shp")
# #print(shapefile)
# shapefile_=shapefile[["ADM1_PT","geometry"]]
# #print(shapefile_)
# shapefile_["numero"]= 0

# df= geodf(shapefile_)
# #print(df)

# df.plot(color="blue", linewidth=0.1, edgecolor="0.01")



# # df = px.data.election()
# # geo_df = gpd.GeoDataFrame.from_features(
# #     px.data.election_geojson()["features"]
# # ).merge(df, on="district").set_index("district")

# fig = px.choropleth_mapbox(df,
#                            geojson=df.geometry,
#                            locations=df['ADM1_PT'],
#                            #color="Joly",
#                            center={"lat": 45.5517, "lon": -73.7073},
#                            mapbox_style="open-street-map",
#                            zoom=2.5)
# fig.show()


import plotly.express as px

df = px.data.election()
geojson = px.data.election_geojson()
print(df)


fig = px.choropleth_mapbox(df, geojson=geojson, #color="Bergeron",
                           locations="district", featureidkey="properties.district",
                           center={"lat": 45.5517, "lon": -73.7073},
                           locations="district",
                           mapbox_style="carto-positron", zoom=9)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()