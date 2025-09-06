# dashboard
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

# data management
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely import wkt
from shapely.geometry import Polygon
import json

# graphing
from matplotlib import use
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.tools as tls 
import plotly.graph_objects as go 


#utils
from utils.dropdown import clean_data
from utils.dropdown import get_colors
from scipy.stats import pearsonr

use('agg')

data = pd.read_csv('./data/processed/CA_Fara_500_2019.csv')

# print(clean_data(data))

tracts = pd.read_csv('./data/processed/ca_tract_geo_data.csv')
tracts['geometry'] = wkt.loads(tracts['geometry'])

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def get_header():
    return html.Div(
        [
            html.H1(
                "California Food Access and Health Outcomes (2019)", 
                style={
                    "textAlign": "center",
                    "padding": "10px",
                    "margin-top": "10px"
                }
            )
        ],
        style={"height": "10%"}
    )

def get_selectors():
    return html.Div(
        [
            html.Div(
                [
                    html.H6(
                        "County",
                        style={
                            "text-align": "center"
                        }
                    ),
                    dcc.Dropdown(
                        data["CountyName"].unique(), 
                        'Los Angeles', 
                        id='county',
                        style={
                            "align-self": "center",
                            "width": "100%"
                        }
                    )
                ], 
                style={
                    "flex-grow": "0.33",
                }
            ), 
            html.Div(
                [
                    html.H6(
                        "Variable",
                        style={
                            "text-align": "center"
                        }
                    ),
                    dcc.Dropdown(
                        clean_data(data),
                        'TotalPopulation',
                        id='column', 
                        style={
                            "align-self": "center", 
                            "width": "100%",
                        }
                    ),
                ], 
                style={
                    "flex-grow": "0.33",
                }
            ),
            html.Div(
                [
                    html.H6(
                        "Indicator Variable",
                        style={
                            "text-align": "center"
                        }
                    ),
                    dcc.Dropdown(
                        get_colors(),
                        "LILATracts_halfAnd10",
                        id='color', 
                    ),
                ], 
                style={
                    "flex-grow": "0.33"
                }
            )
        ], 
        style={
            "display": "flex",
            "flex-direction": "row"
        }
    )

def get_left():
    return html.Div(
        [
            get_selectors(),
            html.Div(
                [
                    html.H4(
                        "Statistics",
                        style={
                            "text-align": "center",
                            "margin-top": "30px"
                        }
                        ),
                    html.Div(
                        children=[], 
                        id="stats",
                        style={
                            "diplay": "flex",
                            "flex-direction": "column",
                            "justify-content": "center" 
                        }
                    )
                ]
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(
                                id='stats-graph',
                                style={
                                    "align-self": "center"
                                }
                            ),
                        ],
                        style={
                            "display": "flex",
                            "flex-direction": "column",
                            "justify-content": "center",
                            "align-self": "center"
                        }
                    ),
                ], 
                style={
                    "display": "flex", 
                    "align-self": "center", 
                    "flex-direction": "column",
                    "justify-content": "center"
                }
            )
        ],
        style={
            "display": "flex",
            "flex-direction": "column",
            'flex': 1,
            'padding': '30px',
            "align-self": "flex-start",
            "justify-content": "space-between"
        }
    )

def get_right():
    return html.Div(
        [
            dcc.Graph(
                id='county-graph',
                style={
                    'border-radius': '15px', 
                    'background-color': 'white'
                }
                )
        ], 
        style={
            'flex': 0.9,
            'padding': '5px',
            # "align-self": "flex-start", 
        }
    )
    
def get_layout():
    return html.Div(
        [
            get_header(),
            html.Div(
                [
                    get_left(),
                    get_right(),
                ],
                style={
                    "display": "flex", 
                    "width": "100vw",
                    "height": "80vh"
                }
            )
        ], 
        style={
            "width": "100vw",
            "height": "100vh", 
            "display": "flex", 
            "flex-direction": "column",
        }
    )

app.layout = get_layout()

@callback(
    Output('county-graph', 'figure'),
    Input('county', 'value'),
    Input('column', 'value')
)
def update_graph(value, col): 
    county = data[data["CountyName"] == value].loc[:, ['GEOID', col]]
    county_geo = tracts.merge(right=county, how='inner', on='GEOID')
    county_geo = gpd.GeoDataFrame(county_geo, geometry='geometry', crs='EPSG:4326')
    centroid = county_geo.geometry.union_all("unary").centroid
    center_x = centroid.x
    center_y = centroid.y
      
    geo_json = json.loads(county_geo.loc[:, ["geometry", "GEOID"]].to_json())

    fig = px.choropleth_map(
        county_geo, 
        geojson=geo_json, 
        color=col, 
        featureidkey="properties.GEOID", 
        locations="GEOID", 
        center={"lat": center_y, "lon": center_x},
    )
    
    fig = fig.update_geos(
        fitbounds='locations', 
        visible=False, 
        center={"lat": center_y, "lon": center_x},
    )
    
    fig = fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        title=value
    )
    
    return fig

@callback(
    Output('stats-graph', 'figure'),
    Input('county', 'value'), 
    Input('column', 'value'),
    Input('color', 'value')
)
def update_stats_graph(value, col, color):
    
    df: pd.DataFrame = data[data["CountyName"] == value]
    
    # sns implementation
    
    # plt.figure()
    # sns.histplot(
    #     data=df,
    #     x=col,
    #     multiple="layer",
    #     hue=color,
    #     common_norm=False,
    #     common_bins=True,
    #     stat="percent",
    #     # binwidth=0.01
    # )
    # plt.tight_layout()
    
    # fig = tls.mpl_to_plotly(plt.gcf())
    # plt.close()
    
    # px implementation
    
    # fig = px.histogram(
    #     df, x=col, color=color, nbins=40
    # )
    
    # go implementation
    
    lila_1 = df[df["LILATracts_1And10"] == 1].loc[:, col]
    lila_0 = df[df["LILATracts_1And10"] == 0].loc[:, col]
    
    data_min = data[col].min()
    data_max = data[col].max()
    bin_width = (data_max - data_min) / 40
    bins = dict(
        start=data[col].min(),
        end=data[col].max(),
        size= bin_width
    )
    fig = go.Figure()
    
    fig.add_trace(
        go.Histogram(
            x=lila_0,
            histnorm="percent",
            name=f"Not {color}",
            xbins=bins,
        )
    )
    fig.add_trace(
        go.Histogram(
            x=lila_1,
            histnorm="percent",
            name=f'{color}',
            xbins=bins,            
        )
    )
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.75)
    
    return fig

@callback(
    Output('stats', 'children'), 
    Input('county', 'value'),
    Input('column', 'value'), 
    Input('color', 'value')
)
def update_stats(county, col, color):
    df = data[data["CountyName"] == county]
    
    not_color = df[df[color] == 0]
    is_color = df[df[color] == 1]
        
    county_div = html.Div(
        [
            html.P(
                [
                    f"{county}",
                    html.Br(),
                    f"Count: {len(df)}",
                    html.Br(),
                    f"Mean: {round(df[col].mean(), 2)}",
                    html.Br(),
                    f"std: {round(df[col].std(), 2)}",
                ]
            ),
        ],
        style={
            # "flex-grow": "0.2"
        }
    )
    
    color_div = html.Div(
        [
            html.P(
                [
                    f"Indicator",
                    html.Br(),
                    f"Count: {round(len(is_color), 2)}",
                    html.Br(),
                    f"Mean: {round(is_color[col].mean(), 2)}",
                    html.Br(),
                    f"std: {round(is_color[col].std(), 2)}",
                ]
            )
        ],
        style={
            # "flex-grow": "0.2"
        }
    )
    
    not_color_div = html.Div(
        [
            html.P(
                [
                    f"Not Indicator",
                    html.Br(),
                    f"Count: {round(len(not_color), 2)}",
                    html.Br(),
                    f"Mean: {round(not_color[col].mean(), 2)}",
                    html.Br(),
                    f"std: {round(not_color[col].std(), 2)}",
                ]
            )
        ],
        style={
            # "flex-grow": "0.2"
        }
    )
    corr, p = pearsonr(x=df[color], y=df[col])
    corr_div = html.Div(
        [
            html.P(
                [
                    "Correlation",
                    html.Br(),
                    f"corr: {round(corr, 2)}",
                    html.Br(),
                    f"p-value: {round(p, 3)}"
                ]
            )
        ],
        style={
            # "flex-grow": "0.2"
        }
    )
    
    info = [
        county_div,
        color_div,
        not_color_div,
        corr_div
    ]
    
    return html.Div(
        children=info, 
        style={
            "display": "flex",
            "flex-direction": "row",
            "justify-content": "space-between", 
            "padding": "20px"
        }
    )

if __name__ == '__main__':
    app.run(debug=True)