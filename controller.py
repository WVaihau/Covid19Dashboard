# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 18:47:27 2021

@author: vwork
"""

# MODULE ---------------------------------------------------------------------

## GRAPHIQUE
import plotly.express as px 
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

## View
import streamlit as st
import pandas as pd

## Other
import model as md
import numpy as np
import requests 
import json

# PRIVATE FUNCTION -----------------------------------------------------------
def __parse_metrics_txt(y, t):
    val = int(y-t)
    return f"{val}"

def __get_last_info(df):
    record_date_last = get_last_record_date(df)
    record_date_j1 = max(df[df['date']!=record_date_last]['date'])
    
    record = {
        'last' : df[df['date'] == record_date_last],
        'j-1' : df[df['date'] == record_date_j1]
        }
    return record

def __display_row(ref, j1, last):
    n = len(ref)
    cols = st.columns(n)
    for i, item in enumerate(ref.items()):
        cols[i].metric(
            label = item[1]['label'],
            value = '',
            delta = __parse_metrics_txt(j1[item[0]], last[item[0]]),
            delta_color = item[1]['d']
            )


# PUBLIC FUNCTION ------------------------------------------------------------

## Load --
#st.cache(suppress_st_warning=True)
def load_data(source, type_entry='main'):
    """
    Load a dataframe from a source

    Parameters
    ----------
    source : str
        Source of the data
    type_entry : str, optional
        Type of file. The default is 'csv'.

    Returns
    -------
    TYPE
        pandas.DataFrame

    """
    if type_entry == 'main':
        df = pd.read_csv(source)
    elif type_entry == 'spec':
        df = pd.read_csv(source, low_memory = False)
    return df

def load_chart(df:pd.DataFrame, chart:str=None):
    """
        Load a graph

    Parameters
    ----------
    df : pd.DataFrame
        the dataframe which will be used to create the graph
    chart : str, optional
        The graph to return. The default is None.

    Returns
    -------
    graph : plotly graph
        The Graph asked

    """
    graph = None
    if chart == "conf_case":
        graph = px.line(df, 
                        x='date', 
                        y='conf',
                        title = 'Number of confirmed COVID19 cases over time',
                        labels={
                            'date':'Date', 
                            'conf':'Number of confirmed cases'
                            })
    elif chart == "hosp_rea":
        df1 = df.rename(columns={"hosp" : "hospitalized", "rea":"reanimation"})
        graph = px.line(df1, 
                    x='date', 
                    y=['hospitalized', "reanimation"],
                    title = "Evolution of the number of patients in hospital and in reanimation over time",
                    labels= {
                    'date':'Date',
                    'value':'Number of patients'
                    })
    elif chart == 'death':
        graph = px.line(df, 
                    x='date', 
                    y='dchosp',
                    title = "Evolution of patient deaths in hospital",
                    labels= {
                    'date':'Date',
                    'dchosp':'Number of patient deaths'
                    })
    return graph


def load_metric(df:pd.DataFrame, date):
    """
    Load metric given a date

    Parameters
    ----------
    df : pandas.DataFrame
        DESCRIPTION.

    Returns
    -------
    
    nbr_liste

    """
    
    df = df[df['date'] == date]

    nbr_case = lambda chx: df[df['date']== date].iloc[0,df.columns.tolist().index(chx)]
    
    list_metrics = ['hosp', 'rea', 'conf_j1']
    
    nbr_liste = [nbr_case(cat) for cat in list_metrics]
    
    return nbr_liste

## CHARTS
def progress(df, p_by, p_by1, name_p_by, name_p_by1, p_title):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.update_layout(
        title_text=p_title
    )

    # Add traces
    fig.add_trace(
        go.Bar(x=df['date'].values.tolist(), y=df[p_by].values.tolist(), name=name_p_by),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df['date'].values.tolist(), y=df[p_by1].values.tolist(), name=name_p_by1, mode='lines'),
        secondary_y=True,
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Hovering
    fig.update_layout(hovermode='x unified')
    
    # Set y-axes titles
    fig.update_yaxes(title_text=name_p_by, secondary_y=False)
    fig.update_yaxes(title_text=name_p_by1, secondary_y=True)
    
    return fig

def chart_progress_stats(df, p_by, p_title):
    fig = None

    if p_by == 'R':
        fig = px.line(df, x='date', y='R', title=p_title)
        fig.update_traces(mode="lines")
        fig.add_hrect(y0=1, y1=df['R'].max(),
                      annotation_text="The epidemic is growing", annotation_position="top left",
                      fillcolor="red", opacity=0.25, line_width=0)
    elif p_by == 'occ':
        fig = px.line(df, x='date', y='TO', title=p_title),
    elif p_by == 'tx_pos':
        fig = px.line(df, x='date', y='tx_pos', title=p_title)
    elif p_by == 'tx_incid':
        fig = px.line(df, x='date', y='tx_incid', title=p_title)
    
    return fig
            

## Variables --
def get_last_record_date(df, date_col='date'):
    return df[date_col].max()

## Display procedure --
def display_general_metric(p_df):
    """
    Display general metrics

    Parameters
    ----------
    df : pandas.DataFrame
        Data source

    Returns
    -------
    None.

    """
    
    # Variables
    
    ## unclassified
    error_msg = '_'
    
    ## Last record date
    date = get_last_record_date(p_df)
    
    ## Last record date information
    df = p_df[p_df['date'] == date]
    df.replace({np.nan:None}, inplace=True)
    
    ## Positivity rate of virological tests
    tx_pos = df['tx_pos'].iloc[0]
    
    ## Number of people tested positive (RT-PCR and antigenic test)
    tx_incid = df['tx_incid'].iloc[0]
    
    ## Occupancy rate of hospital beds
    TO = df['TO'].iloc[0]
    
    ## Virus reproduction factor
    R = df['R'].iloc[0]
    
    # Layout
    if None in [tx_pos, tx_incid, TO, R]:
        st.markdown("\U00002139 | *The stats are based on the data of the last recorded date*")    

    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(label = "Positivity rate of virological tests",
                value = round(tx_pos,2) if tx_pos != None else error_msg
                )

    col2.metric(label = "Incidence rate",
                value = round(tx_incid,2) if tx_incid != None else error_msg
                )

    col3.metric(label = "Occupancy rate of hospital beds",
                value = f'{round(TO*100,2)} %' if TO != None else error_msg
                )

    col4.metric(label = "Virus reproduction factor",
                value = round(R,2) if R != None else error_msg
                )    

            

def display_today_metric(df):
    """
    Display today metric

    Parameters
    ----------
    df : pandas.DataFrame
        Data source

    Returns
    -------
    None.

    """
    day_last = max(df['date'])
    day_penultimate = max(df[df['date']!=day_last]['date'])
    today_nbr_hosp, today_nbr_rea, today_nbr_conf = load_metric(df, day_last)
    
    yest_nbr_hosp, yest_nbr_rea, yest_nbr_conf = load_metric(df, day_penultimate)
    
    st.markdown("#### Last metrics - {}".format(md.date_today))
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label = "Number of patients hospitalized", 
                value = today_nbr_hosp, 
                delta = __parse_metrics_txt(yest_nbr_hosp, today_nbr_hosp),
                delta_color="inverse")
    col2.metric(label = "Number of patients in reanimation", 
                value = today_nbr_rea, 
                delta = __parse_metrics_txt(yest_nbr_rea, today_nbr_rea),
                delta_color = "inverse")
    col3.metric(label = "Number of patients tested positive", 
                value = today_nbr_conf, 
                delta = __parse_metrics_txt(yest_nbr_conf, today_nbr_conf),
                delta_color = "inverse")

def display_progression(df):
    
    record = __get_last_info(df)
    last = record['last'].drop(columns=['date']).iloc[0]
    j1 = record['j-1'].drop(columns=['date']).iloc[0]
    
    data = {
        "hosp" : {
            'label' : 'Presently Hospitalized'
            },
        "incid_hosp" : {
            'label' : 'New patients Hospitalized'
            },
        "rea" : {
            "label" : "Presently in Intensive Care"
            },
        "incid_rea" : {
            "label" : "New patients in Intensive Care"
            },
        "rad" : {
            "label" : "Returned home"
            },
        "incid_rad" : {
            "label" : "New patients returned home"
            }
        }
    
    for k in data.keys():
        if 'rad' not in k:
            data[k]['d'] = 'inverse'
        else:
            data[k]['d'] = 'normal'
            
    l1 = ['hosp', 'rea', 'rad']
    
    rep = [{k:v for k,v in data.items() if col in k} for col in l1]
    
    for info in rep:
        __display_row(info, j1, last)
        

        
    
## Other
def get_geojson(by='reg'):
    
    url = md.urls['DATA']['GEOJSON'][by]
    
    with requests.get(url) as response:
        group = json.loads(response.text)
    
    return group
    
def transform_df(df):
    
    df['lib_reg'].replace(md.replacement_df_geojson, inplace=True)
    
    return df

def show_map(p_df, p_by, sort=None, p_date=None, animation=False):
    
    # VARIABLES
    
    ## DataFrame
    
    ### Filter by the specific date if the animation is unwanted
    if animation == False:
        if p_date != None:
            df = p_df[p_df['date'] == p_date]
        else: #### If the the date is None take the last record date
            df = p_df[p_df['date'] == p_df['date'].max()]
        
    ### Adapt the df label with the geojson file
    df['lib_reg'].replace(md.replacement_df_geojson, inplace=True)
    
    ### Keep ONLY wanted values
    if sort == None:
        liste_group = df[p_by].unique()
    else:
        liste_group = sort
    df = df[df[p_by].isin(liste_group)]
    
    ## Geojson
    p_geojson = get_geojson(by=p_by)
    
    # MAP
    map_fig = px.choropleth(
        df,
        color        = p_by,
        locations    = p_by,
        projection   ='mercator',
        geojson      = p_geojson,
        featureidkey ='properties.nom'
        )
    map_fig.update_geos(fitbounds="locations", visible=False)
    map_fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
    
    return map_fig
    


















    