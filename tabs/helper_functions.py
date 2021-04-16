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
        umap_title = view_meta['fm_umap']
        bar_title = 'Maternal/Fetal Origin Breakdown'
    else:
        gene_vals = adata[:, view_meta['fm_umap']].copy().to_df()[view_meta['fm_umap']].to_list()
        adj_sc_df['gene_color'] = gene_vals
        umap_title = view_meta['fm_umap'] + ' Expression'
        bar_title = view_meta['fm_umap'] + ' Expression Distribution'

    fig = make_subplots(6, 1,
        specs = [
            [{'rowspan':2}],
            [{}],
            [{'rowspan':2}],
            [{}],
            [{}],
            [{}]    
        ],
        #colorscale
#2nd title add CDA Expression in Each Cell on UMAP
#3rd is CDA expression distirbution
#show red/blue maternal/fetal
#4th is Cell Type Frequencies
        vertical_spacing = 0.04,
        subplot_titles = [
            'Cell Type on UMAP',
            '',
            f'{umap_title} on UMAP',
            '',
            bar_title,
            'Cell Type Frequencies'
        ]
    )
    s_sc_df = adj_sc_df[adj_sc_df.sample_num.isin(view_meta['sample_selection'])]
    shown_groups = 0
    for group_count, group in enumerate(cmap_dict.keys()):

        if(view_filter['selection_data'][(group_count + 1) * 2 + group_count * 8 + 1] == True):
            shown_groups += 1
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

            if(view_meta['fm_umap'] == 'Freemuxlet Assignment'):
                fm_filter = select_df['free_assign'] == 'fetal'
            else:
                fm_filter = select_df['fetal_maternal_origin'] == 'fetal'

            fetal_df, maternal_df = select_df[fm_filter], select_df[~fm_filter]

            f_count, m_count = determine_fetal_counts(fetal_df, maternal_df)

            for fm_label, fm_count, fm_color, fm_df, side, point_pos in zip(['fetal', 'maternal'],[f_count, m_count], ['red', 'blue'], [fetal_df, maternal_df], ['positive', 'negative'], [1, -1]):
                if(gene_vals is None):
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
                else:
                    fig.add_trace(
                        go.Violin(
                            x0 = group,
                            y = fm_df['gene_color'].to_list(),
                            side = side,
                            name=fm_label,
                            legendgroup = fm_label,
                            scalegroup = fm_label,
                            marker = dict(
                                size = 3
                            ),
                            showlegend = False,
                            alignmentgroup = group,
                            pointpos = point_pos,
                            points="all",
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
                        hovertext = [group] * len(r_df),
                        hoverinfo="text",
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
                for fm_r_df, fm_label, fm_color, hover in zip([fetal_df, maternal_df],[f_count, m_count], ['red', 'blue'], ['fetal', 'maternal']):
                    if(gene_vals is not None):
                        fm_color = fm_r_df['gene_color'].to_list()
                        colorscale='sunset'
                        hovertext = fm_color
                    else:
                        colorscale = None
                        hovertext = [hover] * len(fm_r_df)
                    fig.add_trace(
                        go.Scattergl(
                            x = fm_r_df.umap_1.to_list(),
                            y = fm_r_df.umap_2.to_list(),
                            hovertext = hovertext,
                            hoverinfo="text",
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
#if(gene_vals is not None):
   #     fig['layout'][f'xaxis4'] = fig['layout'][f'xaxis5']

    fig['layout']['title'] = dict(text = view_meta.get('name'), font=dict(size=22))
    fig['layout']['title_x'] = view_meta['title_center']
    fig.update_layout(violingap=0.4)#, violinmode='overlay')

    fig.update_layout(
        margin=dict(
        l=0,
        r=0,
        b=30,
        t=80,
        )
    )
    #print(fig['layout'])
    print(shown_groups)
    fig['layout'][f'xaxis5']['range'] = [-0.5, shown_groups - 0.5]


    return fig

#obj = generate_view_plot(sc_df, generate_filter_view(), current_data_test['view_1'])
#count = 0
#print(obj['data'])
#for val in obj['data']:
#    print(val['legendgroup'])
#    count +=1
#print(count)
#print(1/0)

#colorscale
#2nd title add CDA Expression in Each Cell on UMAP
#3rd is CDA expression distirbution
#show red/blue maternal/fetal
#4th is Cell Type Frequencies

#mf distirbuted acorss cell types
#consistency with y chromosome

# confuisuon matrix freemuxlet and plascenta

#compare free muxelet plascenta, intersection

['fetal', 'fetal', 'maternal', 'maternal', 'fetal', 'maternal', 'maternal', 'maternal', 'maternal', 'maternal', 'fetal', 'maternal', 'maternal', 'fetal', 'fetal', 'maternal', 'maternal', 'maternal']