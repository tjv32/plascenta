import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_core_components as dcc

import pandas as pd

from tabs.default_data import *

def generate_meta_view(view_num, view_total_count, sample_list, fm_umap, view_name):
    template = figure_sizes.get(view_total_count).copy()
    template['sample_selection'] = sample_list
    template['name'] = view_name
    template['fm_umap'] = fm_umap

    return template

def generate_filter_view():
    template_view = {        
        'selection_data' : [True] * len(cmap_dict.keys()) * 10,
        'umap_filter' : 
        {
            'x' : [-100, 100],
            'y' : [-100, 100]
        },
    }

    return template_view

def determine_filter_samples(group_info, sex, location, clinical):
    r_df = group_info.copy()
    if(sex is not None):
        r_df = r_df[r_df.Sex.isin(sex)]
    if(location is not None):
        r_df = r_df[r_df.SampleLoc.isin(location)]
    if(clinical is not None):
        r_df = r_df[r_df.Condition.isin(clinical)]
    return list(r_df.SampleNum)


def determine_fetal_counts(fetal_df, maternal_df):
    if(len(fetal_df) == 0 and len(maternal_df) == 0):
        return 0, 0
    else:
        f_count = len(fetal_df)/(len(fetal_df) + len(maternal_df))
    return f_count, 1 - f_count

def generate_view_plot(sc_df, view_filter, view_meta):
    adj_sc_df = sc_df.copy()
    if(view_meta['fm_umap'] in ['Y Chromosome Index', 'PlaSCenta Assignment', 'Freemuxlet Assignment']):
        gene_vals = None
    else:
        gene_vals = adata[:, view_meta['fm_umap']].copy().to_df()[view_meta['fm_umap']].to_list()
        adj_sc_df['gene_color'] = gene_vals

    fig = make_subplots(6, 1,
        specs = [
            [{'rowspan':2}],
            [{}],
            [{'rowspan':2}],
            [{}],
            [{}],
            [{}]    
        ],
        vertical_spacing = 0.04,
        subplot_titles = [
            'Cell Type on UMAP',
            '',
            'Maternal/Fetal Origin on UMAP',
            '',
            'Maternal/Fetal Origin breakdown',
            'Cell Type breakdown'
        ]
    )
    s_sc_df = adj_sc_df[adj_sc_df.sample_num.isin(view_meta['sample_selection'])]
    for group_count, group in enumerate(cmap_dict.keys()):
        g_df = s_sc_df[s_sc_df.annotated_clusters == group].copy()

        selection_bool = view_filter['selection_data'][group_count * 2]

        if(not selection_bool):
            select_df = pd.DataFrame(g_df.columns)
            unselect_df = g_df.copy()
        else:
            selection_filter = (g_df.umap_1 > view_filter['umap_filter']['x'][0]) & \
                (g_df.umap_1 < view_filter['umap_filter']['x'][1]) & \
                (g_df.umap_2 > view_filter['umap_filter']['y'][0]) & \
                (g_df.umap_2 < view_filter['umap_filter']['y'][1])    

            select_df, unselect_df = g_df[selection_filter], g_df[~selection_filter]

            if(gene_vals is None):
                fm_filter = select_df['fetal_maternal_origin'] == 'fetal'
            else:
                ##CHNAGE HERE WHEN ADDING FREEMUXLET
                fm_filter = select_df['fetal_maternal_origin'] == 'fetal'
            fetal_df, maternal_df = select_df[fm_filter], select_df[~fm_filter]

            f_count, m_count = determine_fetal_counts(fetal_df, maternal_df)

            for fm_label, fm_count, fm_color in zip(['fetal', 'maternal'],[f_count, m_count], ['red', 'blue']):
                fig.add_trace(
                    go.Bar(
                        x = [group],
                        y = [fm_count],
                        name=fm_label,
                        legendgroup = fm_label,
                        marker = dict(
                            color = fm_color
                        ),
                        showlegend = False,
                        visible=view_filter['selection_data'][(group_count + 1) * 2 + group_count * 8 + 1] 
                    ),
                    row=5,
                    col=1
                )    



            for r_df, opacity, select_count in zip([select_df, unselect_df], [1.0, 0.3], [0, 1]):

                fig.add_trace(
                    go.Scattergl(
                        x = r_df.umap_1.to_list(),
                        y = r_df.umap_2.to_list(),
                        mode='markers',
                        marker = dict(
                        color = cmap_dict[group],
                        size = 4,
                        opacity=opacity,
                        ),
                        name=group,
                        legendgroup = group,
                        showlegend = False,
                        visible=view_filter['selection_data'][(group_count + 1) * 2 + group_count * 8 + 1] 
                    ),
                    row = 1,
                    col = 1
                )
                fig.add_trace(
                    go.Bar(
                        x = [group],
                        y = [len(r_df[r_df.annotated_clusters == group])],
                        name=group,
                        legendgroup = group,
                        marker = dict(
                            color = cmap_dict[group],
                            opacity = opacity
                        ),
                        showlegend = select_count < 1,
                        visible=view_filter['selection_data'][(group_count + 1) * 2 + group_count * 8 + 1] 
                    ),
                    row=6,
                    col=1
                )
                fm_filter = r_df['fetal_maternal_origin'] == 'fetal'
                for fm_r_df, fm_label, fm_color in zip([r_df[fm_filter], r_df[~fm_filter]],[f_count, m_count], ['red', 'blue']):
                    if(gene_vals is not None):
                        fm_color = fm_r_df['gene_color'].to_list()
                        colorscale='sunset'
                    else:
                        colorscale=None
                    fig.add_trace(
                        go.Scattergl(
                            x = fm_r_df.umap_1.to_list(),
                            y = fm_r_df.umap_2.to_list(),
                            mode='markers',
                            marker = dict(
                                color = fm_color,
                                size = 4,
                                opacity=opacity,
                                colorscale=colorscale,
                            ),
                            name=group,
                            legendgroup = group,
                            showlegend = False,
                            visible=view_filter['selection_data'][(group_count + 1) * 2 + group_count * 8 + 1] 
                        ),
                        row = 3,
                        col = 1
                    )

    fig.update_layout(barmode='stack', height=800, width=view_meta['fig_width'])
    for i in range(1, 6):
        for ax in ['x', 'y']:
            fig['layout'][f'{ax}axis{i}']['title'] = dict(text = '', font=dict(size=12))
            fig['layout'][f'{ax}axis{i}']['showgrid'] = False
            fig['layout'][f'{ax}axis{i}']['zeroline'] = False
            fig['layout'][f'{ax}axis{i}']['showticklabels'] = False
            fig['layout'][f'{ax}axis{i}']['showspikes'] = False

    fig['layout']['title'] = dict(text = view_meta.get('name'), font=dict(size=22))
    fig['layout']['title_x'] = view_meta['title_center']

    fig.update_layout(
        margin=dict(
        l=0,
        r=0,
        b=30,
        t=80,
        )
    )

    return fig

#obj = generate_view_plot(sc_df, generate_filter_view(), current_data_test['view_1'])
#count = 0
#print(obj['data'])
#for val in obj['data']:
#    print(val['legendgroup'])
#    count +=1
#print(count)
#print(1/0)

