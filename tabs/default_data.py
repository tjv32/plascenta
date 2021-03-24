import pandas as pd
import numpy as np

cmap_dict = {
	'NK': 'teal',
	 'B': 'orange',
	 'CD4 T': 'brown',
	 'CD14 Monocytes': 'yellow',
	 'CD8 T': 'green',
	 'FCGR3A Monocytes': 'purple',
	 'Dendritic': 'black',
	 'Megakaryocytes': 'pink'
}
fm_colors = ['blue', 'red']

sc_df = pd.read_csv('data/pbmc_adata/clusters.csv')
if('sample_num' not in sc_df):
	sc_df['sample_num'] = [1] * len(sc_df)
group_info = pd.read_csv('data/group_info.csv')
sex_vals = ['M', 'F']
clinical_states = ['TIL', 'TNL', 'PTL']
plascenta_locations = ['BP', 'PV', 'CAM']
map_dict = {
	'Basal Plate' : 'BP',
	'Membranes' : 'CAM',
	'Placenta' : 'PV',
}

group_info = group_info.replace({'SampleLoc' : map_dict})

sex_filters = [{'label': i, 'value': i} for i in sex_vals]
clinical_state_filters = [{'label': i, 'value': i} for i in clinical_states]
placenta_location_filters = [{'label': i, 'value': i} for i in plascenta_locations]

r_arr = np.array([1]*len(sc_df) + [2]*len(sc_df) +[3]*len(sc_df))
np.random.shuffle(r_arr)
sc_df['sample_num'] = r_arr[:len(sc_df)]

custom_dict = {
	'all' : [i for i in list(set(sc_df['sample_num']))],
}
individual_filters = [{i for i in range(5)}]
#custom_filters = [{key for i in range(5)}]
#combined_filters = custom_filters + individual_filters


current_data_test = {
    'view_1' : 
    {
        'sample_selection' : None,
        'name' : 'All Samples'
    },
        'view_2' : None,
        'view_3' : None,
    }
figure_sizes = {
	1: {
		'fig_width' : 1600,
		'style_width' : '100%',
		'title_center' : 0.445

	},
	2: {
		'fig_width' : 800,
		'style_width' : '50%',
		'title_center' : 0.41

	},
	3: {
		'fig_width' : 550,
		'style_width' : '33%',
		'title_center' : 0.39

	}
}