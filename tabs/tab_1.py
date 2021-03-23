import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
from dash_extensions import Download
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import os

from make_app import app
from tabs.default_data import *
from tabs.helper_functions import *

tab_title = html.H1(
    children='plaSCenta',
    style={
        'textAlign': 'center',
        'color': 'black'
    }
)

obj = go.Figure()

view_1 = dcc.Graph(
    id = 'view_1',
    figure = obj,
    style = {
        'width':'100%',
        'display': 'inline-block'
    }
)
view_2 = dcc.Graph(
    id = 'view_2',
    figure = obj,
    style = {
        'width':'50%',
        'display': 'none'
    }
)
view_3 = dcc.Graph(
    id = 'view_3',
    figure = obj,
    style = {
        'width':'50%',
        'display': 'none'
    }
)

all_views = html.Div(
    id = 'all_views',
    children = [
        view_1,
        view_2,
        view_3
    ]
)


body_1 = html.Div(
	[
		dbc.Container(
 			[
            	dbc.Row(
                	[
                    	dbc.Col(
                        	[
                            	tab_title
                        	]
                    	)
                	]
            	),
            	dbc.Row(
                	[

                        dbc.Col(
                            [
                                all_views
                            ],
                            width=12
                        ),
                	]
            	),
            ],
        	fluid = True
    	)
    ]
)

tab_1 = dcc.Tab(
	label='Visualizations', 
	children=[
        body_1
    ]
)
'''
@app.callback(
    [
        Output('umap', 'figure'),
    ],
    [
        Input('cell_type', 'restyleData')
    ],
    [
        State('umap', 'figure'),
        State('cell_type', 'figure'),
    ]
)

def cross_filter_cell_type_legend(restyle_data, previous_umap, previous_cell_type):
    
    visibilities = {trace.get('name'): trace.get('visible') for trace in previous_cell_type['data']}
    for i, trace in enumerate(previous_umap['data']):
        previous_umap['data'][i]['visible'] = visibilities[previous_cell_type['data'][i]['name']]
    return [previous_umap]

'''
for i in range(1, 4):
    @app.callback(
        [
            Output(f'view_{i}_filter', 'data'),
        ],
        [
            Input(f'view_{i}', 'restyleData'),
            Input(f'view_{i}', 'selectedData'),
        ],
        [
            State(f'view_{i}_filter', 'data'),
            State(f'view_{i}_meta', 'data'),
        ]
    )
    def cross_filter(restyle_data, point_selection, view_filter, view_meta):

        ctx = dash.callback_context

        input_trigger = ctx.triggered[0]['prop_id'].split('.')[1]

        if(input_trigger == 'restyleData'):
            view_filter['selection_data'] = adjust_restyle_data(view_filter['selection_data'], restyle_data)

        elif(input_trigger == 'selectedData'):
            if(point_selection and point_selection['points']):
                view_filter['umap_filter'] = adjust_point_selection_data(view_filter['umap_filter'], point_selection)
            else:
                view_filter['umap_filter'] = generate_filter_view()['umap_filter']
        else:
            view_filter = generate_filter_view()

        return [view_filter]

    @app.callback(
        [
            Output(f'view_{i}', 'figure'),
            Output(f'view_{i}', 'style'),
        ],
        [
            Input(f'view_{i}_filter', 'data'),
            Input(f'view_{i}_meta', 'data'),
        ],
    )
    def create_view_figure(view_filter, view_meta):

        if(not all([view_filter, view_meta])):
            return [go.Figure(), {'display': 'none'}]
        fig = generate_view_plot(sc_df, view_filter, view_meta)
        style = {
            'width':view_meta['style_width'],
            'display': 'inline-block'
        }

        return [fig, style]

'''
@app.callback(
    [
        Output('umap', 'figure'),
        Output('fm_umap', 'figure'),
        Output('cell_type', 'figure'),
        Output('fm_cell_type', 'figure'),
        Output('current_data', 'data'),
    ],
    [
        Input('umap', 'selectedData'),
        Input('fm_umap', 'selectedData'),
        Input('cell_type', 'restyleData'),
        Input('fm_cell_type', 'restyleData')
    ],
    [
        State('umap', 'figure'),
        State('cell_type', 'figure'),
        State('fm_umap', 'figure'),
        State('fm_cell_type', 'figure'),
        State('current_data', 'data')
    ]
)
def crossfilter_points(selection1, selection2, cell_type_restyle, fm_cell_type_restyle, prev_umap, prev_cell_type, prev_fm_umap, prev_fm_cell_type, current_data):

    if(not any([selection1, selection2, cell_type_restyle, fm_cell_type_restyle])):
        raise PreventUpdate

    current_data = adjust_current_data(current_data, cell_type_restyle) 
    current_data = adjust_current_data(current_data, fm_cell_type_restyle)    

    x_max, y_max = 1000, 1000
    x_min, y_min = -1000, -1000

    for selected_data in [selection1, selection2]:
        if selected_data and selected_data['points']:
            x_min = max(x_min, selected_data['range']['x'][0])
            x_max = min(x_max, selected_data['range']['x'][1])
            y_min = max(y_min, selected_data['range']['y'][0])
            y_max = min(y_max, selected_data['range']['y'][1])


    group_present = list(set([trace.get('name') for trace in prev_cell_type['data'] if trace.get('visible') != 'legendonly']))
    fm_present = list(set([trace.get('name') for trace in prev_fm_cell_type['data'] if trace.get('visible') != 'legendonly']))

    

    filter_vals = sc_df.annotated_clusters.isin(group_present) & sc_df.fetal_maternal_origin.isin(fm_present) & (sc_df.umap_1 > x_min) & (sc_df.umap_1 < x_max) & (sc_df.umap_2 > y_min)& (sc_df.umap_2 < y_max)

    select_sc_df = sc_df[filter_vals]
    non_sc_df = sc_df[~filter_vals]


    return create_figures(select_sc_df, non_sc_df, current_data) + [current_data]
'''
def adjust_restyle_data(current_data, restyle):

    if(current_data is None):
        current_data = [True] * len(cmap_dict.keys()) * 2
    if(restyle is None):
        return current_data
    for i, index in enumerate(restyle[1]):
        current_data[index] = restyle[0].get('visible')[i]

    return current_data

def adjust_point_selection_data(current_data, point_selection):

    x_max, y_max = 100, 100
    x_min, y_min = -100, -100

    if(point_selection['range'].get('x') is not None):
        x_val, y_val = 'x', 'y'
    else:
        x_val, y_val = 'x3', 'y3'

    if point_selection and point_selection['points']:
        x_min = max(x_min, point_selection['range'][x_val][0])
        x_max = min(x_max, point_selection['range'][x_val][1])
        y_min = max(y_min, point_selection['range'][y_val][0])
        y_max = min(y_max, point_selection['range'][y_val][1])

    umap_filter = {}
    umap_filter['x'] = [x_min, x_max]
    umap_filter['y'] = [y_min, y_max]

    return umap_filter