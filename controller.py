# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 18:47:27 2021

@author: vwork
"""

# MODULE ---------------------------------------------------------------------

## GRAPHIQUE
import plotly.express as px
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
import calendar
import datetime
from datetime import timedelta
import re
import numpy as np

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

def parse_date(date, format_date):
    return pd.to_datetime(date).strftime(format_date)

def __get_start_and_end_date_from_calendar_week(year, calendar_week):
    monday = datetime.datetime.strptime(f'{year}-{calendar_week}-1', "%Y-%W-%w").date()
    return monday, monday + datetime.timedelta(days=6.9)

def __get_last_date_from_week_number(p_yw):

    # Parse the year and week number
    year, week_nbr = [int(nbr) for nbr in re.findall("\d+", p_yw)]

    # Get the last date of this specific week
    _, date_last = __get_start_and_end_date_from_calendar_week(year, week_nbr)

    # Format the date
    date = date_last

    return date

# PUBLIC FUNCTION ------------------------------------------------------------

## Load --
@st.cache(suppress_st_warning=True, ttl=md.cache_duration['short'])
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
    elif type_entry == 'hosp':
        df = pd.read_csv(source, low_memory = False, delimiter = ";")
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

@st.cache(allow_output_mutation=True)
def process_geojson(df, sort_by_cat):
    geojson_file = fetch_geojson(sort_by_cat)
    geojson_place_name = [ feature['properties']['nom'] for feature in geojson_file["features"] ]

    # Instanciate
    df_cat_col = df[sort_by_cat].unique().tolist()
    df_cat_col

    replacement = {
        '' : ['et', 'de', 'la', "d'"],
        ' ': ['-']
    }

    # Split Each zone by word and replace if needed
    loc = {}
    for col in df_cat_col:
        c = col
        for replace_val,liste in replacement.items():
            c = replace_word(c, liste, replace_val)
        loc[col] = c.split()

    # Associate df_zone with geojson zone
    dict_replacement = {}
    for df_zone, liste_word in loc.items():

        for zone in geojson_place_name:
            ctn = 0
            for word in liste_word:

                if word.lower() in zone.lower():
                    ctn += 1

            if (len(liste_word) >= 2 and ctn >= 2) or (len(liste_word) ==1 and ctn >= 1):
                dict_replacement[df_zone] = zone

    df[sort_by_cat] = df[sort_by_cat].map(lambda df_zone : dict_replacement[df_zone] if df_zone in dict_replacement.keys() else df_zone)

    return df, geojson_file

## Reusable

def filter_df(p_df:pd.DataFrame, col_name:str, value, keep:bool=True, period=None):
    """
        Filter a dataframe based on a specific date

        Parameters :
            p_df : pandas.DataFrame
                The original dataframe
            col_name : str
                The dataframe column name where the filter will be applyed
            value : item or list
                The value used to filter the specified column
            keep : bool
                If it must keep or not the selected value

        Return : pandas.DataFrame
            The filtered initial dataframe
    """

    if type(value) == list:
        operator = 'not in' if keep == False else 'in'
    else:
        operator = "==" if keep == True else "!="

    df = p_df.query(f"{col_name} {operator} @value")

    return df

def filter_df_last_n_date(df:pd.DataFrame, date_col:str, ndays=7, pattern='%Y-%m-%d'):
    """
    Return the df based on the last n days inside the col_name
    """
    if ndays == None:
        ndays = 7

    # Last date
    last_date_str = df[date_col].max()

    # Last date in date format
    start_date_d = pd.to_datetime(last_date_str) - pd.Timedelta(days=ndays - 1)

    # Last date in string format
    start_date_str = start_date_d.strftime(pattern)

    # Filter the data frame
    df = df[df[date_col].between(start_date_str, last_date_str)]

    return df

def replace_word(var, list_replace, replacement_value):
    for word in list_replace:
        var = var.replace(word, replacement_value)
    return var

def fetch_geojson(name):

    with requests.get(md.url['geojson'][name]) as bdd:
        raw = json.loads(bdd.text)

    return raw

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
        fig = px.line(df,
                      x='date',
                      y='R',
                      title=p_title)
        fig.update_traces(mode="lines",
                          hovertemplate = "<b>%{x}</b> <br> R : %{y}"
                          )
        fig.add_hrect(y0=1, y1=df['R'].max(),
                      annotation_text="Area where the epidemic is developing", annotation_position="top left",
                      fillcolor="red", opacity=0.25, line_width=0)
    elif p_by == 'occ':
        fig = px.line(df, x='date', y='TO', title=p_title),
    elif p_by == 'tx_pos':
        fig = px.line(df, x='date', y='tx_pos', title=p_title)
    elif p_by == 'tx_incid':
        fig = px.line(df, x='date', y='tx_incid', title=p_title)

    return fig

@st.cache(ttl=md.cache_duration['short'])
def chart_barplot(p_df, chx_cat, chx_opt):

    df = p_df.copy(deep=True)

    # Filter by last date
    df = df[df['date'] == df['date'].max()]

    # ORDER DESC
    df = df.sort_values(chx_opt, ascending=False)

    val_chx_cat = md.dict_txt['chx_cat'][chx_cat]
    val_chx_opt = md.dict_txt['chx_opt'][chx_opt]

    fig = px.bar(df,
                 x=chx_cat,
                 y=[chx_opt],
                 color="incid_"+chx_opt,
                 title = f"Patients {val_chx_opt.lower()} by {val_chx_cat.upper()}",
                 labels = {
                     'value' : f"Patient {val_chx_opt.lower()}",
                     chx_cat : val_chx_cat
                 },
                 color_continuous_scale='Bluered'
                )
    fig.update_layout(showlegend=False,
                    coloraxis_colorbar = dict(
                        title = "New Patients"
                    )
                     )
    fig.update_traces(hovertemplate = "<br>".join([
                        "<b>%{x}</b>",
                        "",
                        md.default_title_color_bar + " : %{y}",
                        "New : %{customdata}"
                    ]),
                      customdata = df['incid_' + chx_opt].values.tolist()
                     )
    return fig

@st.cache(suppress_st_warning=True, ttl=md.cache_duration['short'])
def chart_map(p_df, p_chx_cat:str, p_chx_opt:str, p_title=None, p_ndays:int=7, p_date_col:str='date', p_filter_zone=None):
    """
        Generate a plotly choropleth map

        Parameters:
            p_df : pandas.DataFrame
                The data frame which contains the data to be plot
            p_chx_cat : str
                The column in p_df that will be used as reference (can only be lib_reg or lib_dep)
            p_chx_opt : str
                The column in p_df that we want to see the evolution
            p_title : str, optional
                The title of the graph
            p_ndays : int, optional
                Number of days to be taken for animation (last n days), Default : 7 (1 week)
            p_date_col: str, optional
                The name of the column that contains the dates, Default : 'date'
            p_filter_zone : bool, optional
                Dictionnary which contains zone to handle
                Default : None
                Format :
                {
                    'location' : #list or single value of type string
                    'keep' : #bool -> True :  keep these areas | False : removes these areas
                }

        Dict :
        dict(
            p_df = ,
            p_chx_cat=,
            p_chx_opt=,
            p_ndays=,
            p_date_col=,
        )

        Return : plotly.express.choropleth figure
    """

    # Parameters verification --
    if p_chx_cat not in md.chx_cat_col:
        raise ValueError("{} must be either one of them : {}".format('p_chx_cat', md.chx_cat_col))

    if p_chx_opt not in md.dict_txt['chx_opt'].keys():
        raise ValueError("p_chx_opt must be either one of them : {}".format(md.dict_txt['chx_opt'].keys()))

    if p_title != None and type(p_title) != str:
        raise ValueError("p_title must be a string")

    if type(p_filter_zone) == dict:
        zones = p_filter_zone
        if set(md.filter_zone_key).issubset(zones) == False:
            raise ValueError("p_filterzone keys must contains those keys : {}".format(md.filter_zone_key))
        else:
            # Verify keep value
            if type(zones['keep']) != bool:
                raise ValueError("The keep key must be a boolean")

            # Verify location value
            if (type(zones['location']) != str and type(zones['location']) == list) or (type(zones['location']) == str and type(zones['location']) != list):
                pass
            else:
                raise ValueError("The location value must be either a list or a string")

            screen = True
    else:
        raise ValueError("p_filterzone must be a dictionary")

    # Variables instanciation --
    date_col = p_date_col
    chx_cat = p_chx_cat
    chx_opt = p_chx_opt

    val_hover_txt_name = md.dict_txt['chx_opt'][chx_opt]

    # val_hover_data = {
    #     chx_cat : False,
    #     chx_opt : True,
    #     date_col : False
    # }


    # Dataframe preparation --

    ## Filter by date
    df = filter_df_last_n_date(p_df, date_col, ndays=p_ndays)

    ## Adapt the dataframe zone column with the geojson one
    df, val_geojson = process_geojson(df, chx_cat)

    ## Filter if needed
    if screen == True:
        df = filter_df(df, chx_cat, zones['location'], keep = zones['keep'])

    ## Group if needed
    if chx_cat == 'lib_reg':
        df = df[[date_col, chx_cat, chx_opt]].groupby([date_col, chx_cat]).sum().reset_index()

    ## Generate the graph
    fig = px.choropleth(
        df,
        geojson = val_geojson,
        color = chx_opt,
        range_color = [0, df[chx_opt].max()],
        color_continuous_scale = md.default_color_continuous_scale,
        #hover_name = chx_cat,
        #hover_data = val_hover_data,
        locations = chx_cat,
        animation_frame = date_col,
        featureidkey = "properties.nom",
        projection = md.default_projection_type
    )
    fig.update_geos(fitbounds="locations", visible=True)
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar = dict(
            title = md.default_title_color_bar
        )
        )
    fig.update_traces(
        hovertemplate='<b>%{text}</b> <br> <br> '+val_hover_txt_name+' : %{customdata}',
        text = df[chx_cat],
        customdata=df[chx_opt])

    return fig

def graph_Region_dep_sex(p_df_reg, p_df_hosp_detail, p_region, p_col, p_date=None, all_sexe = False):

    # Copy of the dataframes
    df_reg = p_df_reg.copy(deep=True)
    df_hosp_detail = p_df_hosp_detail.copy(deep=True)

    region =  p_region # Wanted region

    # Liste des départements pour la région sélectionnée
    region_department = df_reg[df_reg['lib_reg'] == region]['dep'].unique().tolist()
    # Filtre les données départemental pour les département sélectionnée
    df_hosp_detail.query("dep in [" + "'" + "','".join(region_department) + "']", inplace=True)

    # Change le code du département par son libelé
    dep_code = {df_reg[df_reg['lib_dep'] == dep]['dep'].iloc[0]:dep for dep in df_reg['lib_dep'].unique()}
    dep_code['978'] = 'SAINT-MARTIN'
    df_hosp_detail['dep'] = df_hosp_detail['dep'].map(dep_code)

    # Change le code du sexe par son libelé
    sexe_code_to_lib = {
        0 : "men and women",
        1 : "men",
        2 : "women"
    }
    df_hosp_detail['sexe'] = df_hosp_detail['sexe'].map(sexe_code_to_lib)

    # Filter by the wanted date
    if p_date == None: # By default take the last available date
        date_picked = df_hosp_detail['jour'].max()
    else:
        date_picked = p_date
    df_dep = df_hosp_detail[df_hosp_detail['jour'] == date_picked]

    # Take only the ones with men or women
    df = df_dep.query("sexe in ({})".format("'{}'".format("','".join(["men", "women"])))).groupby(['dep', 'sexe']).sum().reset_index()

    # Figure creation
    x_col = "dep" # x-axis
    y_col = p_col # y-axis

    color = ['indianred', 'lightsalmon']
    groupby_vals = ['men', 'women']
    groupby_col = "sexe"

    fig = go.Figure()
    for i, groupby_val in enumerate(groupby_vals):
        fig.add_trace(go.Bar(
            x=df[df[groupby_col] == groupby_val][x_col],
            y=df[df[groupby_col] == groupby_val][y_col],
            name=groupby_val[0].upper() + groupby_val[1:],
            marker_color=color[i]
        ))
        fig.update_traces(
        hovertemplate="<b>%{y}</b>")

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        title_text="<br>".join([
            '<b> {} patients {} by department and sex </b>'.format(region, md.dict_txt['chx_opt'][y_col].lower()),
            " <span style='font-size:0.9em; color:#808080'>{}</span>".format(date_picked)
        ]),
        barmode='group',
        xaxis={'categoryorder':'total descending'})

    return fig

def chart_age_per_region(p_region, p_df_reg, p_df_age, graph_type="line"):
    # Make a copy of each input dataframe
    df_reg = p_df_reg.copy(deep=True)
    df_age = p_df_age.copy(deep=True)

    # Replace each code by its respective label
    reg_nbr = {df_reg[df_reg['lib_reg'] == reg].iloc[0,:]["reg"]:reg for reg in df_reg['lib_reg'].unique()}
    df_age['reg'] = df_age['reg'].map(reg_nbr)

    # Keep only records about the wanted region
    df_age = df_age[df_age["reg"] == p_region]

    # Change the age column with its respective value
    df_age["cl_age90"] = df_age["cl_age90"].map(md.age_trad)

    # Change the Week column to take the last date available for the given week number
    df_age["Semaine"] = df_age["Semaine"].map(lambda x: __get_last_date_from_week_number(x))

    # Rename the dataframe column
    df_age.rename(columns={"cl_age90":"cl_age", "Semaine":"Date"}, inplace=True)

    if graph_type == "line":
        fig = px.line(
            df_age[df_age["cl_age"] != "all ages"],
            x="Date",
            y="NewAdmHospit",
            color="cl_age",
            labels = {"NewAdmHospit" : "Number of Patients"},
            title = "<br>".join([
                "<b>New hospitalization in {} by age group</b>".format(p_region),
                "{}".format(df_age["Date"].max())
                ]),
            custom_data=["cl_age"]
            #log_y=True
            )

        fig.update_traces(
            hovertemplate="<br>".join([
                "<b>%{customdata[0]} years old </b>",
                "Date : %{x}",
                "Number of new hospitalizations : %{y}"
                ]))
        fig.update_layout(legend_title_text='Age Group <br><span style="color:grey; font-size:0.7em">unit : years old</span>')
    else:
        df_pivot = pd.pivot(
            df_age.groupby(["Date", "cl_age"]).max().reset_index(),
            values="NewAdmHospit",
            index=['cl_age'],
            columns = ["Date"]
        )
        fig = px.imshow(
            df_pivot
            )
    return fig

## Variables --
def get_last_record_date(df, date_col='date'):
    return df[date_col].max()


## Display procedure --
def display_general_metric(p_df, last_available=False):
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

    if last_available == False:
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
                    value = "{} R".format(round(R,2)) if R != None else error_msg
                    )
    else:
        df = p_df.copy(deep=True)

        fields = ['tx_pos', 'tx_incid', 'TO', 'R']

        dict_data = {}
        for field in fields:
            sdf = df[df[field].notna() == True]

            data = sdf.iloc[-1, :]

            dict_data[field] = {
                "val" : data[field] if field != "TO" else data[field] * 100,
                "date": data['date'],
                "name" : field
                }

        # Positivity rate of virological tests

        cols = st.columns(len(dict_data.keys()))
        dim = ["%", "", "%", "R"]
        i = 0
        for i, col in enumerate(dict_data.keys()):
            cols[i].plotly_chart(chart_kpi_simple(cat=col, **dict_data[col], s=dim[i]), use_container_width=True)

        with cols[0].expander("More about the indicator"):
            txt_tx_pos = [
                "Unit :",
                "Percentage of positive cases",
                "Description :",
                "Daily percentage of positive testers compared to the number of testers (positive and negative)."
                ]
            caption(txt_tx_pos)

        with cols[1].expander("More about the indicator"):
            txt_incid_rate = [
                "Unit :",
                "Number of cases per week per 100,000 population",
                "Description : ",
                "The incidence rate is stopped at D-3 and calculated on the sum of the number of new positive persons for the last 7 days [D-9; D-3] in order to better take into account the delay of data reporting. It is expressed per 100,000 inhabitants.",
                "Range : ",
                "National level (France as a whole), at the regional level and at the departmental level (metropolitan and ultra-marine departments)"
                ]
            caption(txt_incid_rate)

        with cols[2].expander("More about the indicator"):
            txt_TO = [
                "Unit :",
                "Percentage",
                "Description :",
                "Proportion of patients with COVID-19 currently in resuscitation, intensive care, or continuous monitoring units relative to total beds in initial capacity, i.e., before increasing resuscitation bed capacity in a hospital"
                ]
            caption(txt_TO)
        with cols[3].expander("More about the indicator"):
            txt_R = [
                "Unit :",
                "Average number of people an infected person can infect",
                "Description : ",
                "R effective > 1 :arrow_right: the epidemic is growing",
                "R effective < 1 :arrow_right: the epidemic is decreasing",
                "Type of update :",
                "Once a week."
                ]
            caption(txt_R)
def caption(txt_list):
    for txt in txt_list:
        st.caption(txt)


def chart_kpi_simple(val, date, cat, s="", name=""):

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        number = {
            "font" : {
                "size" : 55
                },
            "suffix" : s
            },
        mode = 'number',

        value = val,
        title = {
            "text" : "<br>".join([
                "<span style='color:#EFD09E'><b>{}</b></span>".format(md.dict_txt['chx_opt'][cat]),
                "<span style='color:#D4AA7D'>{}</span>".format(date)
            ])
        },
        gauge = {
            'axis': {'visible': False}},
        domain = {'row': 0, 'column': 0}
        ))
    fig.update_layout(
    paper_bgcolor="#726bfa",
    height=250,  # Added parameter
    autosize=True
    )
    return fig


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
        "conf" : {
            'label' : "Confirmed case"
            },
        "conf_j1" : {
            'label' : "New Confirmed case"
            },
        "dchosp" : {
            'label' : "Deceased person"
            },
        "incid_dchosp" : {
            'label' : "Recently deceased person"
            },
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

    l0 = ['conf', 'hosp']
    l1 = ['rea', 'dchosp','rad']

    rep = [{k:v for k,v in data.items() if col in k and 'dc' not in k} for col in l0] + [{k:v for k,v in data.items() if col in k} for col in l1]

    for info in rep:
        __display_row(info, j1, last)
