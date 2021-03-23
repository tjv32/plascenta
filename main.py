import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
from dash_extensions import Download
import plotly.graph_objects as go

from make_app import app

from tabs.tab_1 import tab_1
from tabs.tab_2 import tab_2


import pandas as pd
import numpy as np


server = app.server

app.layout = html.Div(
	children = [
		dcc.Store(id='view_1_meta'),
		dcc.Store(id='view_1_filter'),
		dcc.Store(id='view_2_meta'),
		dcc.Store(id='view_2_filter'),
		dcc.Store(id='view_3_meta'),
		dcc.Store(id='view_3_filter'),
		dcc.Tabs(
			[
				tab_1,
				tab_2
			]
		)
	]
)

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

if __name__ == '__main__':

    app.run_server(debug=True)




