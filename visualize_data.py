import json
import re
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

shape_file = gpd.read_file("ne_110m_populated_places/ne_110m_populated_places.shp")

marker_data = []
locations = []

def read_json():
    with open('two_review_data_old.json') as file:
        data = json.load(file)
    return data

def create_map():
    fig = px.choropleth_mapbox(
        shape_file,
        geojson = shape_file.geometry,
        locations = shape_file.index,
        featureidkey = "properties.index",
        center={"lat": 46.94809, "lon": 7.44744},
        mapbox_style = "carto-positron",
        zoom = 12,
        title = "Map of Bern"
    )

    for marker in marker_data:
        fig.add_trace(go.Scattermapbox(
            lat = [marker["lat"]],
            lon = [marker["lon"]],
            mode = 'markers',
            marker = dict(size = 10, color = 'red'),
            name = marker["name"]
        ))

    fig.update_geos(fitbounds="locations")
    fig.show()

def review_amount_plot(df):
    sns.set_theme(style="darkgrid")
    
    g = sns.jointplot(x="rating", y="votes", data=df,
                      kind="reg", truncate=False,
                      color="m", height=7)
    plt.show()

def review_rate_plot(has_rateing, has_no_rating):
    data = {
        'Category': ['Has Rating', 'No Rating'],
        'Amount': [has_rateing, has_no_rating]
    }
    df = pd.DataFrame(data)

    g = sns.barplot(x='Category', y='Amount', data=df)
    plt.show()

def location_rating_plot(df):
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="rating",
        size="rating",
        hover_name="name",
        color_continuous_scale=px.colors.sequential.Reds,
        mapbox_style="carto-positron",
        title="Location vs Rating"
    )
    fig.show()

def main():
    data = read_json()
    for item in data:
        name = item.get('name')
        rating_str = item.get('rating')
        lat = item.get('lat')
        lon = item.get('lon')

        if lat and lon:
            marker_data.append({"name": name, "lat": lat, "lon": lon})
            if rating_str:
                rating_match = re.search(r'([\d.]+) \((\d+)\)', rating_str)
                if rating_match:
                    rating = float(rating_match.group(1))
                    locations.append({"name": name, "lat": lat, "lon": lon, "rating": rating})

    df = pd.DataFrame(locations)
    create_map()
    location_rating_plot(df)

    rate = read_json()
    ratings = []
    votes = []

    for item in rate:
        rating_str = item.get('rating')
        if rating_str:
            rating_match = re.search(r'([\d.]+) \((\d+)\)', rating_str)
            if rating_match:
                ratings.append(float(rating_match.group(1)))
                votes.append(int(rating_match.group(2)))

    if ratings and votes:
        review_data = {
            'rating': ratings,
            'votes': votes
        }
        df = pd.DataFrame(review_data)
        review_amount_plot(df)

    location_rating_plot()

    has_rateing = 0
    has_no_rating = 0
    for item in data:
        rating_str = item.get('rating')
        if rating_str == 'null':
            has_no_rating += 1
        else:
            has_rateing += 1
    review_rate_plot(has_rateing, has_no_rating)

if __name__ == "__main__":
    main()
