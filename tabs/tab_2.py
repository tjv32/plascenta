import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
import plotly.graph_objects as go

import pandas as pd
import numpy as np

from make_app import app
from tabs.helper_functions import *
from tabs.default_data import *

tab_title = html.H1(
    children='Select Subset of Data to View',
    style={
        'textAlign': 'center',
        'color': 'black'
    }
)

number_of_groups_labels = html.Label(
    children = 'Number of Views',
    style={
        'textAlign': 'center',
        'color': 'black',
    }
)
number_of_groups_dd = dcc.Dropdown(
    id='number_of_groups_dd',
    options=[{'label': i, 'value': i} for i in range(1, 4)],
    value=1,
    multi=False,
)

view_selection = []
for i in range(3):
    view_selection.append(
        html.Div(
            id = f'view_{i + 1}_selection',
            children = [
                html.Br(),
                html.Label(
                    children = f'Select View {i + 1} Samples:',
                    style={
                        'textAlign': 'center',
                        'color': 'black',
                    }
                ),
                html.Br(),
                html.Label(
                    children = f'Enter View Name:',
                    style={
                        'textAlign': 'center',
                        'color': 'black',
                    }
                ),
                html.Br(),
                dcc.Input(
                    id=f'name_{i + 1}',
                    type='text',
                    value=f'View {i+1}'
                ),
                html.Br(),
                html.Label(
                    children = f'Select Fetal Sex:',
                    style={
                        'textAlign': 'center',
                        'color': 'black',
                    }
                ),
                dcc.Dropdown(
                    id= f'sex_dd_{i + 1}',
                    options=sex_filters,
                    value=['M', 'F'],
                    multi=True,
                ),
                html.Br(),
                html.Label(
                    children = f'Select Clinical State of Pregnancy Filter:',
                    style={
                        'textAlign': 'center',
                        'color': 'black',
                    }
                ),
                dcc.Dropdown(
                    id= f'clinical_state_dd_{i + 1}',
                    options=clinical_state_filters,
                    value=clinical_states,
                    multi=True,
                ),
                html.Br(),
                html.Label(
                    children = f'Select Placenta Location Filter:',
                    style={
                        'textAlign': 'center',
                        'color': 'black',
                    }
                ),
                dcc.Dropdown(
                    id= f'plascenta_location_state_dd_{i + 1}',
                    options=placenta_location_filters,
                    value=[plascenta_locations[i]],
                    multi=True,
                ),
                html.Br(),
                html.Label(
                    children = f'Number of Samples in Selection: ',
                    id = f'count_label_{i+1}',
                    style={
                        'textAlign': 'center',
                        'color': 'black',
                    }
                ),
                html.Br(),
                html.Label(
                    children = f'Seconday UMAP Visualization: ',
                    id = f'fm_umap_{i+1}',
                    style={
                        'textAlign': 'center',
                        'color': 'black',
                    }
                ),
                dcc.Dropdown(
                    id= f'fm_umap_dd_{i + 1}',
                    options=gene_names,
                    value='PlaSCenta Assignment',
                    multi=False,
                ),
            ]
        )
    )


update_button = html.Button(
    'Update Views', 
    id='update_button_view',
)



body_2 = html.Div(
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
                                number_of_groups_dd,
                            ]
                        )
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                view_selection[0],
                            ]
                        ),
                        dbc.Col(
                            [
                                view_selection[1],
                            ]
                        ),
                        dbc.Col(
                            [
                                view_selection[2],
                            ]
                        )
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Br(),
                                update_button,
                            ]
                        )
                    ]
                ),

            ],
            fluid = True
        )
    ]
)




for i in range(1, 4):
    @app.callback(
        [
            Output(f'count_label_{i}', 'children'),
        ],
        [
            Input(f'sex_dd_{i}', 'value'),
            Input(f'clinical_state_dd_{i}', 'value'),
            Input(f'plascenta_location_state_dd_{i}', 'value')
        ]
    )
    def update_group_selection(sex, plascenta_loc, clinical):
        vals = [sex, clinical, plascenta_loc]
        if(not any(vals)):
            raise PreventUpdate
        adj_vals = []
        for val in vals:
            if(type(val) == str):
                adj_vals.append([val])
            else:
                adj_vals.append(val)

        samples = determine_filter_samples(group_info, adj_vals[0], adj_vals[1], adj_vals[2])   
        return_msg = f'Number of Samples in Selection: {len(samples)}',
        return return_msg




@app.callback(
    [
        Output('view_1_selection', 'style'),
        Output('view_2_selection', 'style'),
        Output('view_3_selection', 'style'),
    ],
    [
        Input('number_of_groups_dd', 'value'),
    ]
)
def update_group_selection(number_groups):
    if(number_groups is None):
        raise PreventUpdate

    return_styles = []
    for i in range(3):
        display='none'
        if i + 1 <= number_groups:
            display='inline-block'

        return_styles.append(
            {
                'display': display
            }
        )
    return return_styles


@app.callback(
    [
        Output('view_1_meta', 'data'),
        Output('view_2_meta', 'data'),
        Output('view_3_meta', 'data'),
    ],
    [
        Input('update_button_view', 'n_clicks'),
    ],
    [
        State('view_1_selection', 'children'),
        State('view_2_selection', 'children'),
        State('view_3_selection', 'children'),
        State('number_of_groups_dd', 'value'),
    ]
)
def update_views(n_clicks, view_1, view_2, view_3, dd_count):
    views = [view_1, view_2, view_3]
    dd_indices = [5, 8, 11, 14, -1]
    adj_views = []
    for view in views:
        adj_views.append([view[i] for i in dd_indices])


    current_views = []
    for i, adj_view in enumerate(adj_views[:dd_count]):
        samples = determine_filter_samples(group_info, adj_view[1]['props']['value'], adj_view[3]['props']['value'], adj_view[2]['props']['value'])
        current_views.append(generate_meta_view(i, dd_count, samples, adj_view[-1]['props']['value'], adj_view[0]['props']['value'])) 
    while(len(current_views) < 3):
        current_views.append(None)

    return current_views



tab_2 = dcc.Tab(
    label='View Selection', 
    children=[
        body_2
    ]
)