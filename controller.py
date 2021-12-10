# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 18:47:27 2021

@author: vwork
"""

# MODULE ---------------------------------------------------------------------

## GRAPHIQUE
import plotly.express as px 
import plotly 

## View
import streamlit as st
import pandas as pd

## Other
import model

# PRIVATE FUNCTION -----------------------------------------------------------
def __parse_metrics_txt(y, t):
    val = int(y-t)
    return f"{val} since yesterday"

# PUBLIC FUNCTION ------------------------------------------------------------

## Load --
@st.cache
def load_data(source, type_entry='csv'):
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
    if type_entry == 'csv':
        df = pd.read_csv(source)
    return df

@st.cache
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

@st.cache
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

## Display procedure --
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
    today_nbr_hosp, today_nbr_rea, today_nbr_conf = load_metric(df, 
                                                            model.date_today)
    
    yest_nbr_hosp, yest_nbr_rea, yest_nbr_conf = load_metric(df,
                                              model.date_yesterday)
    
    st.markdown("#### Today metrics - {}".format(model.date_today))
    
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
    