# importing lybraries
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime as dt
import calendar
from dash_extensions import Lottie
from dash.dependencies import Input, Output
import plotly.express as px


# creating a dash application
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX], 
           meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.5, minimum-scale=0.5'}])
server = app.server

# function that breaks line if string is longer than 8 chr
def insert_break_after_40(text):
            if len(text) <= 8:
                return text
            # If the text is longer, find the first space after the 40th character
            else:
                space_index = text.find(' ', 8)
                if space_index == -1:
                    return text
                return text[:space_index] + '<br>' + text[space_index+1:]
            
def insert_break_after_2(text):
            if len(text) <= 3:
                return text
            # If the text is longer, find the first space after the 40th character
            else:
                space_index = text.find(' ', 3)
                if space_index == -1:
                    return text
                return text[:space_index] + '<br>' + text[space_index+1:]


# import data from csv sheets **********************************************************
#agency_type_immap_id_labels_df_2 = pd.read_csv('agency_type_immap_id_labels_df_2.csv', low_memory=False, encoding="iso-8859-1")
IM_service_request_df = pd.read_csv('IM_service_request_df.csv', low_memory=False, encoding="iso-8859-1")
capacity_building_df = pd.read_csv('capacity_building_df.csv', low_memory=False, encoding="iso-8859-1")
coordination_meetings = pd.read_csv('coordination meetings.csv', low_memory=False, encoding="iso-8859-1")
dfIssues = pd.read_csv('dfIssues.csv', low_memory=False, encoding="iso-8859-1")

# temporary
summary_list = ["IM Service Request", "Capacity Building" ]
dfIssues = dfIssues[dfIssues['Summary'].isin(summary_list)]

# Craetind data registration data frame
df_registration = dfIssues.copy()
df_registration["created_date"] = pd.to_datetime(df_registration["created_date"])
df_registration = df_registration.sort_values(by="created_date")

# Calculate the timestamps for each year
start_date = dt(2024, 1, 1)
end_date = dt.now()
years_range = range(start_date.year, end_date.year + 1)  # Include the current year
timestamps = [int(dt(year, 1, 1).timestamp()) for year in years_range]

# Calculate the timestamps for each year
start_month = df_registration["created_date"].min()
end_month = dt.now()
months_range = range(start_date.month, end_date.month + 1)  # Include the current month
monthstamps = [calendar.month_abbr[month] for month in months_range]

# creating a copy of dfIssues dataframe
df_issues = dfIssues.copy()
df_issues["created_date"] = pd.to_datetime(list(df_issues["created_date"]))
df_issues["month"] = df_issues["created_date"].dt.month
df_issues["year"] = df_issues["created_date"].dt.year
df_issues["month_abbr"] = df_issues["month"].apply(lambda x: calendar.month_abbr[x])

# Calculating the number of received requests
requests_number = len(dfIssues)

# # Calculating the number of closed requests
# requests_closed = len(dfIssues[dfIssues["Status"] == "Done"])

# # Calculating the number of opened requests
# requests_opened = requests_number-len(dfIssues[dfIssues["Status"] == "Done"])

# Creating agency_type dataframe.
df_agency_type_sr= IM_service_request_df[["Key",'agency_type.choices0']].copy()
df_agency_type_cb= capacity_building_df[["Key",'agency_type.choices0']].copy()
df_agency_type_df = pd.concat([df_agency_type_sr, df_agency_type_cb], ignore_index=True)
df_issues_agency_type = pd.merge(df_agency_type_df, df_issues, on='Key', how='outer')

# Creating locations dataframe.
# locations in IM_service_request_df
list_columns_IM= [col for col in IM_service_request_df.columns if 'locations.choices' in col]
locations_IM_df = IM_service_request_df[["Key"]+list_columns_IM]

# melting locations_IM_df
locations_IM_df = pd.melt(locations_IM_df, id_vars =['Key'], value_vars =list_columns_IM, var_name ='locations', value_name ='province')

#print(list(capacity_building_df[ 'locations.text']))


# locations in capacity_building_df
capacity_building_df["locations.choices0"]= ["Cabo Delgado", None, 'Cabo Delgado', "Maputo", "Maputo"]
capacity_building_df["locations.choices1"]= [None, None, None, "Cabo Delgado", "Cabo Delgado"]
capacity_building_df["locations.choices2"]= [None, None, None, None, "Nampula"]
capacity_building_df["locations.choices3"]= [None, None, None, None, "Niassa"]
capacity_building_df["locations.choices4"]= [None, None, None, None, "Zambezia"]
capacity_building_df["locations.choices5"]= [None, None, None, None, "Sofala"]
list_columns_CB= [col for col in capacity_building_df.columns if 'locations.choices' in col]
locations_CB_df= capacity_building_df[["Key"]+list_columns_CB]

# melting locations_CB_df
locations_CB_df = pd.melt(locations_CB_df, id_vars =['Key'], value_vars =list_columns_CB, var_name ='locations', value_name ='province')

# Concatinating locations_IM_df and locations_CB_df
locations_df = pd.concat([locations_IM_df, locations_CB_df], ignore_index=True)

# Concatinating locations_df and df_issues
df_issues_locations = pd.merge(locations_df, df_issues, on='Key', how='outer')

# Applying groupby on provinve
df_issues_locations = df_issues_locations.groupby(["province", "year", "month", "month_abbr"] )["Key"].count().reset_index()
df_issues_locations = df_issues_locations.sort_values(by="Key", ascending=False)#.head(10)
df_issues_locations = df_issues_locations[df_issues_locations["province"]!="Other..."]

#requested provinces/locations must this request cover
df_issues_locations.rename(columns={"Key": "Total requested number"}, inplace=True)

# # Concatinating locations_df and df_issues
# df_issues_locations = pd.merge(locations_df, df_issues, on='Key', how='outer')

# Creating products dataframe.
# products in IM_service_request_df
products_columns_IM= [col for col in IM_service_request_df.columns if 'products.choices' in col]
products_IM_df = IM_service_request_df[["Key"]+products_columns_IM]

# melting products_IM_df
products_IM_df = pd.melt(products_IM_df, id_vars =['Key'], value_vars =products_columns_IM, var_name ='products.choices', value_name ='products')

# products in capacity_building_df
products_columns_CB= [col for col in capacity_building_df.columns if 'requirements.choices' in col]
products_CB_df= capacity_building_df[["Key"]+products_columns_CB]

# melting locations_CB_df
products_CB_df = pd.melt(products_CB_df, id_vars =['Key'], value_vars = products_columns_CB, var_name ='products.choices', value_name ='products')

# Concatinating products_IM_df and products_CB_df
products_df = pd.concat([products_IM_df, products_CB_df], ignore_index=True)


# Concatinating products_df and df_issues
df_issues_products = pd.merge(products_df, df_issues, on='Key', how='outer')

# Applying groupby on products
df_issues_products = df_issues_products.groupby(["products", "year", "month", "month_abbr"] )["Key"].count().reset_index()
df_issues_products = df_issues_products.sort_values(by="Key", ascending=False)#.head(10)

#requested products/training must this request cover
df_issues_products.rename(columns={"Key": "Total products"}, inplace=True)

# Creating sectors of work dataframe.
# products in IM_service_request_df
sectors_columns_IM= [col for col in IM_service_request_df.columns if 'sector_aor_wg.choices' in col]
sectors_IM_df = IM_service_request_df[["Key"]+sectors_columns_IM]

# melting products_IM_df
sectors_IM_df = pd.melt(sectors_IM_df, id_vars =['Key'], value_vars = sectors_columns_IM, var_name ='sector_aor_wg.choices', value_name ='sectors_of_work')

# products in capacity_building_df
####################################################################################
####################################################################################
####################################################################################


# Concatinating products_df and df_issues
df_issues_sectors = pd.merge(sectors_IM_df, df_issues, on='Key', how='outer')

#print(df_issues_sectors)
# Applying groupby on products
df_issues_sectors = df_issues_sectors.groupby(["sectors_of_work","year", "month", "month_abbr"] )["Key"].count().reset_index()
df_issues_sectors = df_issues_sectors.sort_values(by="Key", ascending=False)#.head(10)

#requested products/training must this request cover
df_issues_sectors.rename(columns={"Key": "Total sectors"}, inplace=True)
#print(df_issues_sectors)

# Lottie configuration and links
options= dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio= "xMidYMid slice"))
# Lottie links
#url_requests="https://lottie.host/4a6b010f-4491-45b0-bf6e-68d50468cd33/Rvqi4Y7NQs.json"
url_requests="src\assets\All-Icons-OL_Advise.png"

url_closed = "https://lottie.host/3a5ea5b7-850a-426a-bdb9-44add947c729/tKGsMKpp6x.json"
url_opened = "https://lottie.host/f8f7dff5-c23d-4698-973c-a8d5b5d549d2/qCgO410bHU.json"
url_organizations = "https://lottie.host/f7cf21e3-9654-4bfd-937e-f5c50e6cebf0/xi4PnpesG1.json"
url_reactions = "https://lottie.host/bd42d6a9-8df3-4417-8e12-f226405b5078/tFWFHVr2KC.json"
url_adsv_clicked= "https://lottie.host/b69a8eb1-bf27-4ccc-8c0d-11fcc8f65967/T56YbMD0DY.json"

app.layout = dbc.Container([
# first row 
		dbc.Row(dbc.Col(html.Hr(style={'borderWidth': "0.4vh", "width": "100%", "borderColor": "#6d6e71", "borderStyle":"double"}),width={'size':13, 'offset':0}),), 


    # defining the first row
    dbc.Row([

        # column with card 1_2
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src='/assets/USAID-iMMAP-Log.png', style={'height':'90%','width':'90%', "float": "center"}, className = 'align-self-right'),
            ],style = {"textAlign": "left"}, className="mb-0 border-0 bg-transparent"),

        ], className = 'align-self-center',  width=5, xs=10, sm=10, md=5, lg=5, xl=5),

        # column with card 1_2
        dbc.Col([
            dbc.Card([
                 
                dbc.CardHeader(["Year filter"],className='text-center', ),
                dbc.CardBody([

                dcc.RangeSlider(
                    id='date-range-slider',
                    marks={timestamp: str(dt.fromtimestamp(timestamp).year) for timestamp in timestamps},
                    min=timestamps[0],
                    max=timestamps[-1],
                    value=[timestamps[0], timestamps[-1]],
                    step=None,             
                    className='sliderRed',
                    dots=True,)
                ])
            ],className="mb-0 border-1 bg-transparent" ), #color="white"

        ],style={'height':'100px', "font-family": "Arial", "font-weight": "bold", 'font-size': '12px'},\
              className = 'align-self-center', width=3, xs=10, sm=10, md=5, lg=3, xl=3),

        
        # column with card 1_2
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(["Month filter"],className='text-center', ),
                dbc.CardBody([
                dcc.RangeSlider(
                    id='month-range-slider',
                    marks={month: calendar.month_abbr[month] for month in months_range},
                    min=months_range[0],
                    max=months_range[-1],
                    value=[months_range[0], months_range[-1]],
                    step=None,
                    className='sliderRed',
                    dots=True,
                    allowCross=True,
                    updatemode='mouseup', )
                ])
            ],className="mb-0 border-1 bg-transparent" ),#), #color="white"

        ], style={'height':'100px', "font-family": "Arial", "font-weight": "bold", 'font-size': '12px'},\
            className = 'align-self-center', width=3, xs=10, sm=10, md=5, lg=3, xl=3),#


        
        # column with card 1_1 #https://immapmoz.org/catalog/
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src='/assets/iMMAP_mo_z_.png', style={'height':'100%','width':'100%'}, className = 'align-self-center'),
                            dbc.CardLink("Moz catalog", target="_blank", href=""),
            ], style = {"textAlign": "center"}, className="mb-0 border-0 bg-transparent text-center", ),

        ],  style={"font-family": "Arial", "font-weight": "bold", 'font-size': '9.5px'},\
              className = 'align-self-center', width=1, xs=3, sm=3, md=3, lg=1, xl=1),

    ], className='mb-0'),


    # Last row
    dbc.Row(dbc.Col(html.Hr(style={'borderWidth': "0.1vh", "width": "100%", "borderColor": "#6d6e71", "borderStyle":"dashed"}),width={'size':12, 'offset':0}),), 

    # defining the second row
    dbc.Row([
        # column 2_1
        dbc.Col([
            dbc.Card([
                    #dbc.CardHeader(Lottie(options=options, width="35%", height="35%", url=url_requests)),
                    dbc.CardHeader([dbc.CardImg(src='/assets/All-Icons-OL_Advise.png', style={'height':'40%','width':'40%', "float": "center"})],  className = 'text-center'),
                    dbc.CardBody([
						html.H4(id ="total_requests", children=0),
                        html.P("Total requests") 
                        
                    ], style={"textAlign": "center", 'height':'70px', "font-family": "Arial", "font-weight": "bold", 'font-size': '12px'})

                ]),
            
        ], className='m-0', width=2, xs=8, sm=8, md=8, lg=2, xl=2 ),
		
        # column 2_2
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([dbc.CardImg(src='/assets/All-Icons-OL-41.png', style={'height':'100%','width':'91%', "float": "center"})],  className = 'text-center'),
                dbc.CardBody([
					html.H4(id="resolved_requests", children=0),
                    html.P("Resolved"),
                ], style={"textAlign": "center", 'height':'70px', "font-family": "Arial", "font-weight": "bold", 'font-size': '12px'})
            ]),
            
        ], className='m-0', width=2,  xs=8, sm=8, md=8, lg=2, xl=2),

        # column 2_3
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([dbc.CardImg(src='/assets/All-Icons-OL_dialogue.png', style={"textAlign": "center", 'height':'57%','width':'56%', "float": "center"})], className='text-center'),
                dbc.CardBody([
					html.H4(id="unresolved_requests", children=0),
                    html.P("In process"),
                ],style={"textAlign": "center", 'height':'70px', "font-family": "Arial", "font-weight": "bold", 'font-size': '12px'})
            ],  ),
            
        ], className='text-center m-0', width=2,  xs=8, sm=8, md=8, lg=2, xl=2),

        # column 2_4
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([dbc.CardImg(src='/assets/All-Icons-OL_COUNTRY-OFFICES.png', style={'height':'45%','width':'24%', "float": "center"})],  className = 'text-center'),
                dbc.CardBody([
					html.H4(id="organizations_assisted", children=0),
                    html.P("Organizations assisted"),
                ], style={"textAlign": "center", 'height':'70px', "font-family": "Arial", "font-weight": "bold", 'font-size': '12px'})
            ]),
            
        ], className='m-0', width=3,  xs=8, sm=8, md=8, lg=3, xl=3),

        # column 2_3
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([dbc.CardImg(src='/assets/All-Icons-OL_Outreach-And-Dialogue.png', style={"textAlign": "center", 'height':'45%','width':'35%', "float": "center"})], className = 'text-center' ),
                dbc.CardBody([
					html.H4(id="coordination_meetings", children=0),
                    html.P("Coordination meetings"),
                ],style={"textAlign": "center", 'height':'70px', "font-family": "Arial", "font-weight": "bold", 'font-size': '12px'})
            ],  ),
            
        ], className='m-0', width=3,  xs=8, sm=8, md=8, lg=3, xl=3),


    ], justify="center", className='mb-0'),

    # Last row
dbc.Row(dbc.Col(html.Hr(style={'borderWidth': "0.1vh", "width": "100%", "borderColor": "#6d6e71", "borderStyle":"dashed"}),width={'size':12, 'offset':0}),), 


    # defining the third row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="line_chart", figure={})
                ])
            ], ), #className="border-0 bg-transparent"
        ], width=6, xs=10, sm=10, md=10, lg=6, xl=6),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="locations_bar_chart", figure={})

                ])
            ], ), #className="border-0 bg-transparent"
        ], width=6, xs=10, sm=10, md=10, lg=6, xl=6)
    ], className='text-center mb-3'),

        # defining the fourth row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="status_chart", figure={})

                ])
            ], ), #className="border-0 bg-transparent"
        ], width=5, xs=10, sm=10, md=10, lg=5, xl=5),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="products_chart", figure={})

                ])
            ], ), #className="border-0 bg-transparent"
        ], width=7, xs=10, sm=10, md=10, lg=7, xl=7)
    ], className='mb-3'),


    # defining the fourth row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="vertical_bar_chart", figure={})

                ])
            ],), # className="border-0 bg-transparent"
        ], width=3, xs=10, sm=10, md=10, lg=3, xl=3),


        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="pie_chart", figure={})

                ])
            ], ), # className="border-0 bg-transparent"
        ], width=3, xs=10, sm=10, md=10, lg=3, xl=3),

        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="pie_chart_donor", figure={})

                ])
            ], ), # className="border-2 bg-transparent"
        ], width=3, xs=10, sm=10, md=10, lg=3, xl=3),


        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="sector_chart", figure={})

                ])
            ], ), #className="border-0 bg-transparent"
        ], width=3, xs=10, sm=10, md=10, lg=3, xl=3)
    ], className='mb-1'),

# Last row
dbc.Row(dbc.Col(html.Hr(style={'borderWidth': "0.4vh", "width": "100%", "borderColor": "#6d6e71", "borderStyle":"double"}), className="mb-0", width={'size':12, 'offset':0}),),


    # defining the first row
    dbc.Row([

        # column with card 1_2
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src='/assets/network.png', style={'height':'30%','width':'30%', "float": "right"}, className = 'align-self-center'),
            ],style = {"textAlign": "center"}, className="mb-0 border-0 bg-transparent"),

        ], className = 'align-self-center',  width=1),


        # column with card 1_2 #www.immap.org #https://www.immap.org
        dbc.Col([
            dbc.Card([
                dbc.CardLink("", target="_blank", href=""),
            ],style={'height':'100%','width':'100%', "float": "center", "textAlign": "left"}, className = "mb-0 border-0 bg-transparent"),

        ], style={"font-family": "Arial", "font-weight": "bold", 'font-size': '9.5px'}, className = 'align-self-center', width=3),


        
        # column with card 1_1
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src='/assets/mail_ico.png', style={'height':'20%','width':'20%'}, className = 'align-self-center'),
            ], style = {"textAlign": "center"}, className="mb-0 border-0 bg-transparent"),
        ],  style={"font-family": "Arial", "font-weight": "bold", 'font-size': '9.5px'}, className = 'align-self-center', width=1),


        # column with card 1_1#rep-mozambique@immap.org #rep-mozambique@immap.org
        dbc.Col([
            dbc.Card([

            dbc.CardLink("", target="_blank", href=""),
            ],style={'height':'100%','width':'100%', "float": "center", "textAlign": "left"}, className = "mb-0 border-0 bg-transparent"),

        ],  style={"font-family": "Arial", "font-weight": "bold", 'font-size': '9.5px'}, className = 'align-self-center', width=3),


    # column with card 1_1
        dbc.Col([
            dbc.Card([
            dbc.CardImg(src='/assets/positionicon.png', style={'height':'10%','width':'10%'}, className = 'align-self-center'),
            ], style = {"textAlign": "center"}, className="mb-0 border-0 bg-transparent"),

        ],  style={"font-family": "Arial", "font-weight": "bold", 'font-size': '9.5px'}, className = 'align-self-center', width=1),


    # column with card 1_1 #https://www.immap.org
        dbc.Col([
            dbc.Card([
            dbc.CardLink("Maputo, Mozambique", target="_blank", href=""),]
            ,style={'height':'100%','width':'100%', "float": "left", "textAlign": "left"}, className = "mb-0 border-0 bg-transparent"),
        ],  style={"font-family": "Arial", "font-weight": "bold", 'font-size': '9.5px'}, className = 'align-self-center', width=3),

    ], className='mb-1'),

], fluid= False)



# Updating the 6 number cards
@app.callback(
    Output("total_requests", "children"),
    Output("resolved_requests", "children"),
    Output("unresolved_requests", "children"),
    Output("organizations_assisted", "children"),
    Output("coordination_meetings", "children"),
    Input("date-range-slider", "value"),
    Input('month-range-slider', "value")
)

def update_cards(date_range, month_range):

    # coping the original dataframes
    df_connections_copy = df_issues.copy()


    # Picking the years from the date slicer
    start_date = dt.fromtimestamp(date_range[0]).year
    end_date = dt.fromtimestamp(date_range[1]).year

    # Picking the months from the date slicer
    start_month = month_range[0]
    end_month = month_range[1]
	
   
    # Filtering the Connections dataframe
    df_connections_copy = df_connections_copy[(df_connections_copy["year"] >= start_date) & (df_connections_copy["year"] <= end_date)]
    df_connections_copy = df_connections_copy[(df_connections_copy["month"] >= start_month) & (df_connections_copy["month"] <= end_month)]
    requests_number = len(df_connections_copy)

    # Companies dataframe
    requests_closed = len(df_connections_copy[df_connections_copy["Status"] == "Done"])
	
    # Invitations dataframe
    requests_opened = requests_number - requests_closed

    # Calculating the number of organizations assisted
    # creating a copy of IM_service_request_df and capacity_building_df dataframe
    df_forms_sr= pd.merge(IM_service_request_df, df_connections_copy[['Key']], on='Key', how='inner')
    df_forms_cb= pd.merge(capacity_building_df, df_connections_copy[['Key']], on='Key', how='inner')
    list_organizations_assisted = list(df_forms_cb["agency_name.text"].unique()) + list(df_forms_sr["agency_name.text"].unique())
    organizations_assisted = len(set(list_organizations_assisted))

    # Copying the coordination meetings dataframe
    coordination_meetings_copy =coordination_meetings.copy()
    
    # Filtering the Connections dataframe
    coordination_meetings_copy = coordination_meetings_copy[(coordination_meetings_copy["year"] >= start_date) & (coordination_meetings_copy["year"] <= end_date)]
    coordination_meetings_copy = coordination_meetings_copy[(coordination_meetings_copy["month"] >= start_month) & (coordination_meetings_copy["month"] <= end_month)]

    # Calculating the number of coordination meetings
    coordination_meetings_number = coordination_meetings_copy["number of meetings"].sum()

    #print(list(df_connections_copy.columns))
    return requests_number, requests_closed, requests_opened, organizations_assisted, coordination_meetings_number


# line chart *******************************************************************
@app.callback(
    Output("line_chart", "figure"),
    Input("date-range-slider", "value"),
    Input('month-range-slider', "value")
)

def update_line_chart(date_range, month_range ):

    # Picking the years from the date slicer
    start_date = dt.fromtimestamp(date_range[0]).year
    end_date = dt.fromtimestamp(date_range[1]).year

    # Picking the months from the date slicer
    start_month = month_range[0]
    end_month = month_range[1]

    # coping the original dataframes
    df_connections_copy = df_issues.copy()

    # filtering the dataframe using the picked years and months from the date slicer
    df_connections_copy = df_connections_copy[(df_connections_copy["year"] >= start_date) & (df_connections_copy["year"] <= end_date)]
    df_connections_copy = df_connections_copy[(df_connections_copy["month"] >= start_month) & (df_connections_copy["month"] <= end_month)]

    df_month= df_connections_copy.groupby(["month","month_abbr"] )["ID"].count().reset_index()
    df_month.rename(columns={"ID": "Total requested"}, inplace=True)

    # building the bar chart
    line_chart = px.line(df_month, x="month_abbr", y="Total requested", text="Total requested", title="Total requests by month", template="ggplot2")
    line_chart.update_traces(mode="markers+lines+text",fill="tozeroy", line=dict(color="#be2126"),\
                             marker=dict(size=df_month["Total requested"]+10, color="#be2126"))
        
    # update the position or align of the graphic
    line_chart.update_layout(margin=dict(l=10, r=10, t=23, b=20))


    # Change background color 
    line_chart.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)","paper_bgcolor": "rgba(0, 0, 0, 0)",})
    
    # Change grid color and axis colors and xaxis and yaxis title
    line_chart.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='white')
    line_chart.update_yaxes(showline=True, linewidth=1, linecolor='white', gridcolor='#bcbec0')

    # Update title, color for xaxis and yaxis.
    line_chart.update_layout(xaxis_title="Month", yaxis_title="Number of requests", font=dict(family='Arial', size=10, color="black"))

    # Update the style of xaxis values
    line_chart.update_xaxes(tickangle=0, ticklen=0, tickfont=dict(color='black', size=10, family='Arial'))

    # Update Update the style of yaxis values
    line_chart.update_yaxes(ticklen=0, tickfont=dict(color='black', size=10, family='Arial'))

    # update title
    line_chart.update_layout(title=dict(text="<b>Requests by month</b>",\
                                       font=dict(family='Arial', size=12, color="black",), yref='paper'), title_x=0,)
    
    line_chart.update_layout(barmode='stack')

    # Update hover template
    line_chart.update_traces(hovertemplate="In %{x} iMMAP Moz received %{y} requests",)

    return line_chart


# tbd chart *******************************************************************
@app.callback(
    Output("locations_bar_chart", "figure"),
    Input("date-range-slider", "value"),
    Input('month-range-slider', "value")

)

def update_vertical_bar_chart(date_range, month_range):

    # Picking the years from the date slicer
    start_date = dt.fromtimestamp(date_range[0]).year
    end_date = dt.fromtimestamp(date_range[1]).year

    # Picking the months from the date slicer
    start_month = month_range[0]
    end_month = month_range[1]

    # coping the original dataframes
    df_reactions_copy = df_issues_locations.copy()
    
    # filtering the dataframe using the picked years and months from the date slicer
    df_reactions_copy = df_reactions_copy[(df_reactions_copy["year"] >= start_date) & (df_reactions_copy["year"] <= end_date)]
    df_reactions_copy = df_reactions_copy[(df_reactions_copy["month"] >= start_month) & (df_reactions_copy["month"] <= end_month)]

    # Applying group by province
    df_reactions_copy= df_reactions_copy.groupby(["province"] )["Total requested number"].sum().reset_index().sort_values(by="Total requested number", ascending=False)

    # calculating percentage impacted by province
    df_reactions_copy["percentage"] = round(df_reactions_copy["Total requested number"] / requests_number * 100,0)

    # breaks string values if string is longer than 8 chr
    df_reactions_copy["province"] = df_reactions_copy["province"].apply(insert_break_after_2)

    # building the bar chart
    bar_chart= px.bar(df_reactions_copy, x="province", y="percentage", text="percentage", template="ggplot2")#

    # update the position or align of the graphic
    bar_chart.update_layout(margin=dict(l=10, r=10, t=23, b=20))
    
    # color of the graphic 
    bar_chart.update_traces(marker_color="#be2126", marker_line_color="#be2126", marker_line_width=1, opacity=1)
    
    # Change background color 
    bar_chart.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)","paper_bgcolor": "rgba(0, 0, 0, 0)",})
    
    # Change grid color and axis colors and xaxis and yaxis title
    bar_chart.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='white')
    bar_chart.update_yaxes(showline=True, linewidth=1, linecolor='white', gridcolor='white')

    # Update title, color for xaxis and yaxis.
    bar_chart.update_layout(xaxis_title="Provinces",  yaxis_title="Percentage(%)", font=dict(family='Arial', size=10, color="black"))

    # Update the style of xaxis values
    bar_chart.update_xaxes(tickangle=90, ticklen=0, showline=True, tickfont=dict(color='black', size=10, family='Arial'))

    # Update Update the style of yaxis values
    bar_chart.update_yaxes(tickangle=90, ticklen=0, showticklabels=False, tickfont=dict(color='black', size=10, family='Arial'))

    # update title
    bar_chart.update_layout(title=dict(text="<b>Province impacted by the requested service</b>",\
                                       font=dict(family='Arial', size=12, color="black",), yref='paper'), title_x=0,)

    # Update hover template
    bar_chart.update_traces( textposition='inside', hovertemplate="%{y}% of the requests have impacted %{x}",)

    return bar_chart
    

    # bar chart *******************************************************************
@app.callback(
    Output("status_chart", "figure"),
    Input("date-range-slider", "value"),
    Input('month-range-slider', "value")    
)

def update_horizontal_bar_chart(date_range, month_range):

    # Picking the years from the date slicer
    start_date = dt.fromtimestamp(date_range[0]).year
    end_date = dt.fromtimestamp(date_range[1]).year

    # Picking the months from the date slicer
    start_month = month_range[0]
    end_month = month_range[1]

    # coping the original dataframes
    df_connections_copy = df_issues.copy()

    # filtering the dataframe using the picked years and months from the date slicer
    df_connections_copy = df_connections_copy[(df_connections_copy["year"] >= start_date) & (df_connections_copy["year"] <= end_date)]
    df_connections_copy = df_connections_copy[(df_connections_copy["month"] >= start_month) & (df_connections_copy["month"] <= end_month)]

    # Applying group by
    df_companies = df_connections_copy.groupby(["Status"])["ID"].count().reset_index().sort_values(by="ID", ascending=True)
    df_companies.rename(columns={"ID": "Total requested"}, inplace=True)
    
    # breaks string values if string is longer than 8 chr
    df_companies["Status"] = df_companies["Status"].apply(insert_break_after_40)

    # building the bar chart
    bar_chart= px.bar(df_companies, x="Total requested", y="Status", text="Total requested", template="ggplot2", orientation="h")#
    
    #bar_chart.update_layout(title_x=0.5, xaxis_title="Number of requests", yaxis_title="Status", font=dict(family="Arial", size=11, color="black"))
    # update the position or align of the graphic
    bar_chart.update_layout(margin=dict(l=10, r=10, t=23, b=20))

    # color of the graphic 
    bar_chart.update_traces(marker_color="#be2126", marker_line_color="#be2126", marker_line_width=1.5, opacity=1)
    
    # Change background color 
    bar_chart.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)","paper_bgcolor": "rgba(0, 0, 0, 0)",})
    
    # Change grid color and axis colors and xaxis and yaxis title
    bar_chart.update_xaxes(showline=False, linewidth=1, linecolor='black', gridcolor='white')
    bar_chart.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='white')

    # Update title, color for xaxis and yaxis.
    bar_chart.update_layout(xaxis_title="Number of requests", yaxis_title="Status", font=dict(family='Arial', size=10, color="black"))

    # Update the style of xaxis values
    bar_chart.update_xaxes(tickangle=0, ticklen=0, showticklabels=True, tickfont=dict(color='white', size=10, family='Arial'))

    # Update Update the style of yaxis values
    bar_chart.update_yaxes(tickangle=0, ticklen=0,  tickfont=dict(color='black', size=10, family='Arial'))

    # Update Update the style of yaxis values
    bar_chart.update_yaxes(tickfont=dict(color='black', size=10, family='Arial'))

    # update title
    bar_chart.update_layout(title=dict(text="<b>Requets status</b>",\
                                       font=dict(family='Arial', size=12, color="black",), yref='paper'), title_x=0,)

    # Update hover template
    bar_chart.update_traces( textposition='inside', hovertemplate="%{x} request(s) is(are) in <b>%{y}</b> situation",)

    bar_chart.update_layout(barmode='stack')

    return bar_chart

# tbd chart *******************************************************************
@app.callback(
    Output("products_chart", "figure"),
    Input("date-range-slider", "value"),
    Input('month-range-slider', "value") 
)

def update_products_chart(date_range, month_range):

    # Picking the years from the date slicer
    start_date = dt.fromtimestamp(date_range[0]).year
    end_date = dt.fromtimestamp(date_range[1]).year

    # Picking the months from the date slicer
    start_month = month_range[0]
    end_month = month_range[1]

    # coping the original dataframes
    df_products_copy = df_issues_products.copy()
    
    # filtering the dataframe using the picked years from the date slicer
    df_products_copy = df_products_copy[(df_products_copy["year"] >= start_date) & (df_products_copy["year"] <= end_date)]
    df_products_copy = df_products_copy[(df_products_copy["month"] >= start_month) & (df_products_copy["month"] <= end_month)]

    # Applying group by province
    df_products_copy= df_products_copy.groupby(["products"] )["Total products"].sum().reset_index()

    # calculating percentage of the products requested
    df_products_copy["percentage"] = round(df_products_copy["Total products"] / requests_number * 100,1)

    df_products_copy = df_products_copy.sort_values(by="Total products", ascending=False)
    df_products_copy.rename(columns={"Total products": "Total requested"}, inplace=True)

    df_products_copy["products"]= ["Surveys" if v == 'Surveys (XLS Form, Kobo, ODK, etc.)' \
							  else 'Training' if v=='Training' else 'Assessment' if v=='Assessment'\
                              else 'Data Analysis' if v=='Data Analysis' else 'Interactive Dashboard' if v=='Interactive Dashboard - Including Maps'\
                              else 'Maps' if v=='Maps' else 'Training Materials' if v=='Training Materials'\
                              else 'Data Management' if v=='Data Management' else 'Geoinformatics' if v=='Geoinformatics'\
                              else 'Information System Development' if v=='Information System Development' else 'Monitoring and Evaluation' if v=='Monitoring and Evaluation (Third Party Monitoring)'\
                              else 'Reports' if v=='Reports' else 'Training Reports' if v=='Training Reports'\
                              else 'Web Application/Website' if v=='Web Application/Website'\
							  else None\
							  for v in list(df_products_copy["products"])]

    # breaks string values if string is longer than 8 chr
    df_products_copy["products"] = df_products_copy["products"].apply(insert_break_after_2)

    # building the bar chart
    bar_chart= px.bar(df_products_copy, x="products", y="Total requested", text="Total requested", template="ggplot2")

    # update the position or align of the graphic
    bar_chart.update_layout(margin=dict(l=10, r=10, t=23, b=20))

    # color of the graphic 
    bar_chart.update_traces(marker_color="#be2126", marker_line_color="#be2126", marker_line_width=1.5, opacity=1)
    
    # Change background color 
    bar_chart.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)","paper_bgcolor": "rgba(0, 0, 0, 0)",})
    
    # Change grid color and axis colors and xaxis and yaxis title
    bar_chart.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='white')
    bar_chart.update_yaxes(showline=True, linewidth=1, linecolor='white', gridcolor='white')

    # Update title, color for xaxis and yaxis.
    bar_chart.update_layout(xaxis_title="Products", yaxis_title="Number", font=dict(family='Arial', size=10, color="black"))

    # Update the style of xaxis values
    bar_chart.update_xaxes(tickangle=90, ticklen=0, tickfont=dict(color='black', size=10, family='Arial'))

    # Update Update the style of yaxis values
    bar_chart.update_yaxes(tickangle=0, ticklen=0, showticklabels=False, tickfont=dict(color='black', size=10, family='Arial'))

    # Update Update the style of yaxis values
    bar_chart.update_yaxes(tickfont=dict(color='black', size=10, family='Arial'))

    # update title
    bar_chart.update_layout(title=dict(text="<b>Products/services requested</b>",\
                                       font=dict(family='Arial', size=12, color="black",), yref='paper'), title_x=0,)

    # Update hover template
    bar_chart.update_traces( textposition='inside', hovertemplate="%{x} have <b>%{y}</b> request(s)",)

    return bar_chart


# tbd chart *******************************************************************
@app.callback(
    Output("vertical_bar_chart", "figure"),
    Input("date-range-slider", "value"),
    Input('month-range-slider', "value")     
)

def update_vertical_bar_chart(date_range, month_range):

    # Picking the years from the date slicer
    start_date = dt.fromtimestamp(date_range[0]).year
    end_date = dt.fromtimestamp(date_range[1]).year

    # Picking the months from the date slicer
    start_month = month_range[0]
    end_month = month_range[1]

    # coping the original dataframes
    df_reactions_copy = df_issues.copy()

    # filtering the dataframe using the picked years and months from the date slicer
    df_reactions_copy = df_reactions_copy[(df_reactions_copy["year"] >= start_date) & (df_reactions_copy["year"] <= end_date)]
    df_reactions_copy = df_reactions_copy[(df_reactions_copy["month"] >= start_month) & (df_reactions_copy["month"] <= end_month)]

    df_reactions_copy = df_reactions_copy.groupby(["Summary"] )["ID"].count().reset_index().sort_values(by="ID", ascending=False)
    df_reactions_copy.rename(columns={"ID": "Total requested", "Summary": "Service requested"}, inplace=True)

    # building the bar chart
    bar_chart= px.bar(df_reactions_copy, x="Service requested", y="Total requested", text="Total requested", title="Total service requested by type", template="ggplot2")
    
    # update the position or align of the graphic
    bar_chart.update_layout(margin=dict(l=10, r=10, t=23, b=20))

    # color of the graphic 
    bar_chart.update_traces(marker_color="#be2126", marker_line_color="#be2126", marker_line_width=1.5, opacity=1)
    
    # Change background color 
    bar_chart.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)","paper_bgcolor": "rgba(0, 0, 0, 0)",})
    
    # Change grid color and axis colors and xaxis and yaxis title
    bar_chart.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='white')
    bar_chart.update_yaxes(showline=True, linewidth=1, linecolor='white', gridcolor='white')

    # Update title, color for xaxis and yaxis.
    bar_chart.update_layout(xaxis_title="Services", yaxis_title="Number", font=dict(family='Arial', size=10, color="black"))

    # Update the style of xaxis values
    bar_chart.update_xaxes(tickangle=0, ticklen=0, tickfont=dict(color='black', size=10, family='Arial'))

    # Update Update the style of yaxis values
    bar_chart.update_yaxes(tickangle=0, ticklen=0, showticklabels=False, tickfont=dict(color='black', size=10, family='Arial'))

    # Update Update the style of yaxis values
    bar_chart.update_yaxes(tickfont=dict(color='black', size=10, family='Arial'))

    # update title
    bar_chart.update_layout(title=dict(text="<b>Type of service requested</b>",\
                                       font=dict(family='Arial', size=12, color="black",), yref='paper'), title_x=0,)

    # Update hover template
    bar_chart.update_traces( textposition='inside', hovertemplate="%{x} have <b>%{y}</b> requests",)

    return bar_chart


# # Pie chart *******************************************************************
@app.callback(
    Output("pie_chart", "figure"),
    Input("date-range-slider", "value"),
    Input('month-range-slider', "value") 
)

def update_pie_chart(date_range, month_range):
	

    # Picking the years from the date slicer
    start_date = dt.fromtimestamp(date_range[0]).year
    end_date = dt.fromtimestamp(date_range[1]).year

    # Picking the months from the date slicer
    start_month = month_range[0]
    end_month = month_range[1]
	
    df_issues_agency_type_copy= df_issues_agency_type.copy()
	
    # filtering the dataframe using the picked years from the date slicer df_issues_agency_type_copy
    df_issues_agency_type_copy = df_issues_agency_type_copy[(df_issues_agency_type_copy["year"] >= start_date) & (df_issues_agency_type_copy["year"] <= end_date)]
    df_issues_agency_type_copy = df_issues_agency_type_copy[(df_issues_agency_type_copy["month"] >= start_month) & (df_issues_agency_type_copy["month"] <= end_month)]

    # grouping by agency type
    df_issues_agency_type_copy = df_issues_agency_type_copy.groupby(['agency_type.choices0'] )["Key"].count().reset_index().sort_values(by="Key", ascending=False)
    
    # building the bar chart and the chosing the color of the graphic
    pie_chart = px.pie(names=df_issues_agency_type_copy['agency_type.choices0'], values = df_issues_agency_type_copy["Key"],\
                       template="ggplot2", color_discrete_sequence=px.colors.sequential.Reds_r, hole=.5)

    # update the position or align of the graphic
    pie_chart.update_layout(margin=dict(l=10, r=10, t=23, b=20))
    
    # update the place where the legend are going to apear
    pie_chart.update_legends(dict(orientation="h" , yanchor="bottom",  y=-0.05,   xanchor="right",  font=dict(color='black', size=10, family='Arial'), x=0.9))

    # Change background color 
    pie_chart.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)","paper_bgcolor": "rgba(0, 0, 0, 0)",})

    # update title
    pie_chart.update_layout(title=dict(text="<b>Agency type</b>",\
                                       font=dict(family='Arial', size=12, color="black",), yref='paper'), title_x=0,)
    
    # Update hover template
    pie_chart.update_traces(hovertemplate="%{value} agencies that asked for service" + " are: <b> %{label} </b><br>")
    
    return pie_chart
    

# # Pie chart donnors *******************************************************************
@app.callback(
    Output("pie_chart_donor", "figure"),
    Input("date-range-slider", "value"),
    Input('month-range-slider', "value") 
)

def update_pie_chart(date_range, month_range):
	

    # Picking the years from the date slicer
    start_date = dt.fromtimestamp(date_range[0]).year
    end_date = dt.fromtimestamp(date_range[1]).year

    # Picking the months from the date slicer
    start_month = month_range[0]
    end_month = month_range[1]
	
    # IM_service_request_df_copy= IM_service_request_df[["Key", "agency_type.choices0" ]].copy()
    # df_issues_copy =df_issues[["Key", "year", "month", "month_abbr"]].copy()

    df_usaid_funded= pd.merge(IM_service_request_df[["Key", "usaid_funded.choices0" ]], df_issues[["Key", "year", "month", "month_abbr"]], on='Key', how='inner')
	
    # filtering the dataframe using the picked years from the date slicer df_issues_agency_type_copy
    df_usaid_funded = df_usaid_funded[(df_usaid_funded["year"] >= start_date) & (df_usaid_funded["year"] <= end_date)]
    df_usaid_funded = df_usaid_funded[(df_usaid_funded["month"] >= start_month) & (df_usaid_funded["month"] <= end_month)]

    # grouping by agency type
    df_usaid_funded = df_usaid_funded.groupby(['usaid_funded.choices0'] )["Key"].count().reset_index().sort_values(by="Key", ascending=False)
    
    # building the bar chart and the chosing the color of the graphic
    pie_chart = px.pie(names=df_usaid_funded['usaid_funded.choices0'], values = df_usaid_funded["Key"],\
                       template="ggplot2", color_discrete_sequence=px.colors.sequential.Reds_r, hole=.5)

    # update the position or align of the graphic
    pie_chart.update_layout(margin=dict(l=10, r=10, t=23, b=20))
    
    # update the place where the legend are going to apear
    pie_chart.update_legends(dict(orientation="h" , yanchor="bottom",  y=-0.05,   xanchor="right",  font=dict(color='black', size=10, family='Arial'), x=0.8))

    # Change background color 
    pie_chart.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)","paper_bgcolor": "rgba(0, 0, 0, 0)",})

    # update title
    pie_chart.update_layout(title=dict(text="<b>Agencies funded by USAID</b>",\
                                       font=dict(family='Arial', size=12, color="black",), yref='paper'), title_x=0,)
    
    # Update hover template
    pie_chart.update_traces(hovertemplate="%{value} agencies are: <b> %{label} </b><br> funded by USAID")
    
    return pie_chart

# tbd chart *******************************************************************
@app.callback(
    Output("sector_chart", "figure"),
    Input("date-range-slider", "value"),
    Input('month-range-slider', "value") 
)

def update_products_chart(date_range, month_range):

    # Picking the years from the date slicer
    start_date = dt.fromtimestamp(date_range[0]).year
    end_date = dt.fromtimestamp(date_range[1]).year

    # Picking the months from the date slicer
    start_month = month_range[0]
    end_month = month_range[1]

    # coping the original dataframes
    df_issues_sectors_copy = df_issues_sectors.copy()

     # filtering the dataframe using the picked years from the date slicer
    df_issues_sectors_copy = df_issues_sectors_copy[(df_issues_sectors_copy["year"] >= start_date) & (df_issues_sectors_copy["year"] <= end_date)]
    df_issues_sectors_copy = df_issues_sectors_copy[(df_issues_sectors_copy["month"] >= start_month) & (df_issues_sectors_copy["month"] <= end_month)]

    df_issues_sectors_copy = df_issues_sectors_copy.groupby(["sectors_of_work"] )["Total sectors"].sum().reset_index().sort_values(by="Total sectors", ascending=False)
    df_issues_sectors_copy.rename(columns={"Total sectors": "Total agencies"}, inplace=True)

    # building the bar chart
    bar_chart= px.bar(df_issues_sectors_copy, x="sectors_of_work", y="Total agencies", text="Total agencies", template="ggplot2")
    
    # update the position or align of the graphic
    bar_chart.update_layout(margin=dict(l=10, r=10, t=23, b=20))

    # color of the graphic 
    bar_chart.update_traces(marker_color="#be2126", marker_line_color="#be2126", marker_line_width=1.5, opacity=1)
    
    # Change background color 
    bar_chart.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)","paper_bgcolor": "rgba(0, 0, 0, 0)",})
    
    # Change grid color and axis colors and xaxis and yaxis title
    bar_chart.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='white')
    bar_chart.update_yaxes(showline=True, linewidth=1, linecolor='white', gridcolor='white')

    # Update title, color for xaxis and yaxis.
    bar_chart.update_layout(xaxis_title="Sectors", yaxis_title="Number", font=dict(family='Arial', size=10, color="black"))

    # Update the style of xaxis values
    bar_chart.update_xaxes(tickangle=90, ticklen=0, tickfont=dict(color='black', size=10, family='Arial'))

    # Update Update the style of yaxis values
    bar_chart.update_yaxes(tickangle=0, ticklen=0, showticklabels=False, tickfont=dict(color='black', size=10, family='Arial'))

    # Update Update the style of yaxis values
    bar_chart.update_yaxes(tickfont=dict(color='black', size=10, family='Arial'))

    # update title
    bar_chart.update_layout(title=dict(text="<b>Partners by sector</b>",\
                                       font=dict(family='Arial', size=12, color="black",), yref='paper'), title_x=0,)

    # Update hover template
    bar_chart.update_traces(textposition='inside', hovertemplate="%{y} agencies are working in <b>%{x}</b>",)

    return bar_chart


# # Word Cloud *******************************************************************
# @app.callback(
#     Output("word_cloud", "figure"),
#     Input("date-range-slider", "value")
# )

# def update_word_cloud(date_range):

#     # Picking the years from the date slicer
#     start_date = dt.fromtimestamp(date_range[0]).year
#     end_date = dt.fromtimestamp(date_range[1]).year

#     # coping the original dataframes   
#     df_connections_copy = df_connections.copy()
#     df_connections_copy = df_connections_copy[(df_connections_copy["year"] >= start_date) & (df_connections_copy["year"] <= end_date)]
#     df_connections_copy["Position"].astype(str)

#     my_world_cloud = WordCloud(width=800, height=600, background_color="white", max_words=100).generate(" ".join(df_connections_copy["Position"].astype(str)))
#     fig_worldcloud = px.imshow(my_world_cloud, template="ggplot2", title="Total connections by position")
#     fig_worldcloud.update_layout(title_x=0.5, font=dict(family="Arial", size=12, color="black"))
#     fig_worldcloud.update_layout(margin=dict(l=10, r=10, t=23, b=20))
#     fig_worldcloud.update_xaxes(visible=False)
#     fig_worldcloud.update_yaxes(visible=False)

#     return fig_worldcloud



if __name__ == "__main__":
    app.run(debug=True)
