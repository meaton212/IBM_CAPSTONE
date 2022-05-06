# -*- coding: utf-8 -*-
"""
Created on Sun May  1 14:51:46 2022

@author: matte
"""

# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
from funcy import project
# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


spacex_df['Booster Version Category']=spacex_df['Booster Version'].str.split(' ',expand=True)[1]
c=['blue','red','green','violet','orange']
c1={}
for i,v in enumerate(spacex_df['Booster Version Category'].unique()):
    c1[v]=c[i]
    
def success(row):
    if row['class']==1:
        return 'Success'
    else:
        return 'Fail'
spacex_df['Success Label']=spacex_df.apply(success, axis=1)
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',options=[{'label':'All sites','value':'ALL'},
                                {'label':'CCAFS LC-40','value':'CCAFS LC-40'},
                                {'label':'VAFB SLC-4E','value':'VAFB SLC-4E'},
                                {'label':'KSC LC-39A','value':'KSC LC-39A'},
                                {'label':'CCAFS SLC-40','value':'CCAFS SLC-40'}],
                                   value='ALL',placeholder="Select a Launch Site here",
                                   searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=0,max=10000,
                                                step=1000,value=[min(spacex_df['Payload Mass (kg)']),max(spacex_df['Payload Mass (kg)'])]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df , values='class', 
        names='Launch Site', 
        title='Total Successful Launches By Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site].groupby(['Launch Site','class','Success Label']).\
                        size().reset_index(name='class count')
                        

        fig = px.pie(filtered_df, values='class count',names='Success Label',color='Success Label',
                     color_discrete_map= {"Fail": "red","Success":"blue"},  #Make it so "Fail is always red and "Success" is always Blue
                     title='Ratio of Successful to Failed Launches for '+entered_site)
        return fig



# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id="payload-slider", component_property="value")])


def get_scatter(entered_site,payload_range):
    
    spacex_df2=spacex_df[np.logical_and(spacex_df['Payload Mass (kg)']>=payload_range[0], spacex_df['Payload Mass (kg)']<=payload_range[1])==1]
    keys1 = spacex_df2['Booster Version Category'].unique()
    c2=project(c1,keys1)
    print(c2['FT'])
    if entered_site == 'ALL':
        fig = px.scatter(spacex_df2 ,x='Payload Mass (kg)', y='class', 
                      color='Booster Version Category',     color_discrete_map= c2,                
                      title='Correlation between Payload and Success for All Sites')
        return fig
    else:
        filtered_df = spacex_df2[spacex_df2['Launch Site']==entered_site]
                       
        fig = px.scatter(filtered_df ,x='Payload Mass (kg)', y='class', 
                                      color='Booster Version Category',         color_discrete_map= c2,                      
                                      title='Correlation between Payload and Success for '+entered_site)
 
        
        return fig




# Run the app
if __name__ == '__main__':
    app.run_server()
