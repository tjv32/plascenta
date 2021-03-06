import pandas as pd
import numpy as np
import colorsys
import scanpy as sc
import os

def get_N_HexCol(N=5):
    HSV_tuples = [(x * 1.0 / N, 0.75, 0.75) for x in range(N)]
    hex_out = []
    for rgb in HSV_tuples:
        rgb = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*rgb))
        hex_out.append('#%02x%02x%02x' % tuple(rgb))
    hex_out = np.array(hex_out)
    np.random.shuffle(hex_out)
    return hex_out

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

if(os.path.exists('/home/thomas')):
	sc_df = pd.read_csv('data/pbmc_adata/clusters.csv')
	adata = sc.read_h5ad('data/pbmc.h5ad')
else:
	sc_df = pd.read_csv('/home/tjv32/research/Python Notebooks/data/dash_data/sc_df.csv')
	adata = sc.read_h5ad('/home/tjv32/research/Python Notebooks/data/filtered_together/adata.h5ad')
	adata = adata[list(sc_df.iloc[:, 0]), :].copy()
if('sample_num' not in sc_df.columns):
	sc_df['sample_num'] = [1] * len(sc_df)

groups = list(sc_df['annotated_clusters'].unique())
if(len(groups) > 10):
	groups = ['STB','CTB','npiCTB','EVT',
		'Stromal-1','Stromal-2','Stromal-3',
		'Fibroblast','Endometrial','Decidual','LED','HSC',
		'Monocyte','Macrophage-1','Macrophage-2',
		'T-Cell-Activated','T-Cell-Resting','NK-cell','B-cell']
N = len(groups)
RGB_tuples = get_N_HexCol(N=N)
cmap_dict = {}
for i in range(N):
	cmap_dict[groups[i]] = str(RGB_tuples[i])

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

gene_names = [{'label': i, 'value': i} for i in ['Y Chromosome Index', 'PlaSCenta Assignment', 'Freemuxlet Assignment'] + adata.var_names.to_list()]

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
		'fig_width' : 1200,
		'style_width' : '100%',
		'title_center' : 0.435

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