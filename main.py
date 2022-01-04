# -*- coding: utf-8 -*-
"""
@author: WILLIAMU Vaihau
"""

import streamlit as st
import model
import controller as ctrl
import controller
#import streamlit_analytics

#streamlit_analytics.track(unsafe_password="12388")

#streamlit_analytics.start_tracking()

# Configuration --------------------------------------------------------------
st.set_page_config(**model.page_config)

### Sources
with st.spinner("Data recovery in progress ..."):
    df = controller.load_data(model.urls['DATA']['DATAGOUV']['general'])
    df_detailed = ctrl.load_data(model.url["dataset"]['partition'],
                                 type_entry = 'spec')
    df_hosp_detail = ctrl.load_data(model.url['dataset']['hosp_detail'], type_entry = "hosp")
    df_age = ctrl.load_data(model.url["dataset"]["age"], type_entry="hosp")

# Layout ---------------------------------------------------------------------

## Sidebar --

container_network = st.sidebar.empty()


## Main

container_header = st.empty()

container_kpi = st.empty()

container_main = st.empty()

container_exploration = st.empty()

container_region = st.empty()

st.markdown("[@Source : data.gouv]({})".format(model.urls["WB"]['DATAGOUV']))

# Condition ------------------------------------------------------------------

## Sidebar --

with container_network.container():
    st.markdown("## \U0001F4CC Contact us")
    st.markdown('**Mano Mathew**')
    st.write(model.mano_btn)
    st.markdown("**WILLIAMU Vaihau** *@Developper*")
    st.write(model.vaihau_btn)

## Main --

## Loading variables

### Record
record_date_last = df['date'].max()


### Graph
graph_conf_case = ctrl.load_chart(df, 'conf_case')
graph_hosp_rea = ctrl.load_chart(df, 'hosp_rea')
graph_dead = ctrl.load_chart(df, 'death')

with container_header.container():
    st.markdown('# \U0001F4C8 France Covid 19 - Dashboard')
    st.markdown('Last recorded date : {}'.format(record_date_last))

with container_kpi.container():
    st.header('# Overview')

    st.subheader('General')
    ctrl.display_general_metric(df, last_available=True)

    st.subheader('Progression')
    st.markdown('\U00002139 | *The calculation is based on the last two days recorded*')
    ctrl.display_progression(df)

    graph_confirmed_case = ctrl.progress(df,
                                         'conf_j1',
                                         'conf',
                                         "New",
                                         "Confirmed",
                                         "Number of confirmed cases")

    graph_hospitalized = ctrl.progress(df,
                                       'incid_hosp',
                                       'hosp',
                                       'New patients',
                                       'Hospitalized',
                                       "Hospitalization in progress")

    graph_reanimation = ctrl.progress(df,
                                      'incid_rea',
                                      'rea',
                                      'New patients',
                                      'Patients',
                                      "Reanimations in progress")

    graph_death = ctrl.progress(df,
         'incid_dchosp',
         'dchosp',
         'New deceased',
         'Deceased',
         "Deaths")

    graph_healed = ctrl.progress(df,
         'incid_rad',
         'rad',
         'Newly Healed',
         'Healed',
         "Recovery ( Hospital discharge )")

    #Layout

    st.plotly_chart(graph_confirmed_case, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.plotly_chart(graph_hospitalized, use_container_width=True)
    col2.plotly_chart(graph_reanimation, use_container_width=True)

    st.plotly_chart(graph_death, use_container_width=True)

    st.plotly_chart(graph_healed, use_container_width=True)


with container_exploration.container():

    max_date = ctrl.pd.to_datetime(df_detailed['date'].max())
    min_date = ctrl.pd.to_datetime(df_detailed['date'].min())

    st.header('# Exploration')
    ddf = df_detailed.copy(deep=True)

    # Explore either by Region or Department
    chx_cat = 'lib_reg' #TODO by Department not yet implemented

    #TODO Choose a variable to explore (For now only one case at a time)
    u_chx_opt = st.selectbox("Attribute to explore",
                             [v for k,v in model.dict_txt["chx_opt"].items()
                              if k in ["hosp", "rea"]
                              ])
    chx_opt = list(model.dict_txt['chx_opt'].keys())[list(model.dict_txt['chx_opt'].values()).index(u_chx_opt)]
    # Choose a mode
    chx_time = st.selectbox("Explore by", ['Last days',
                                           'Last 7 days',
                                       'Last 2 weeks'
                                       ])

    # Group by if needed
    if chx_cat == 'lib_reg':
        ddf = ddf[[model.date_col, chx_cat, chx_opt, 'incid_' + chx_opt]].groupby([model.date_col, chx_cat]).sum().reset_index()

    # TODO - Continue Implementing Picked Date
    if chx_time == 'Picked date':
        # Date to filter on
        dp = st.date_input(
            "Which date ?",
            value = max_date,
            min_value = min_date,
            max_value = max_date,
            help="It take by default the last date available")
        picked_date = dp.strftime("%Y-%m-%d")

        # Filter by date
        ddf = ctrl.filter_df(df_detailed,
                             'date',
                             [picked_date],
                             keep=True)
    elif chx_time == 'Last days':
        graph_bar = ctrl.chart_barplot(ddf, chx_cat, chx_opt)
        st.plotly_chart(graph_bar, use_container_width=True)

        reg = st.selectbox("Pick a region", df_detailed.lib_reg.unique().tolist())

        # Hospitalization in Picked Region by department and sex
        graph = ctrl.graph_Region_dep_sex(df_detailed, df_hosp_detail, reg,  chx_opt)
        st.plotly_chart(graph, use_container_width=True)

        # New Hospitalization in Picked Region by age group
        graph_age = ctrl.chart_age_per_region(reg, df_detailed, df_age)
        st.plotly_chart(graph_age, use_container_width=True)

    elif chx_time == 'Last 7 days' or chx_time == 'Last 2 weeks':
        ndays = 7 if chx_time == 'Last 7 days' else 12
        graph_map = ctrl.chart_map(ddf,
                                   chx_cat,
                                   chx_opt,
                                   p_ndays=ndays,
                                   p_filter_zone={
                                       'keep' : False,
                                       'location' : model.zone_isolated
                                       })
        st.plotly_chart(graph_map, use_container_width=True)

with container_main.container():

    st.header('# The statistical progression')
    # Variables

    graph_R = ctrl.chart_progress_stats(df, 'R', 'Virus reproduction factor - R')
    # graph_occ_rate = ctrl.chart_progress_stats(df, 'occ', 'Occupation rate - TO')
    graph_tx_pos = ctrl.chart_progress_stats(df, 'tx_pos', "Positivity rate of virological tests : tx_pos")
    graph_tx_incid = ctrl.chart_progress_stats(df, 'tx_incid', "Incidence rate : tx_incid")

    # Layout

    st.plotly_chart(graph_R, use_container_width=True)

    # st.markdown("""
    #             Evolution of the R0: the number of reproduction of the virus
    #             It is the average number of people that an infected person can contaminate. If the effective **R is greater than 1, the epidemic is growing; if it is less than 1, the epidemic is declining**
    #             """)

    col11, col22 = st.columns(2)

    col11.plotly_chart(graph_tx_pos, use_container_width=True)
    # col11.markdown("""
    #               The positivity rate corresponds to the number of people tested positive (RT-PCR and antigenic test)
    #               The above graph refers to the rate of virological test positivity for the first time in more than 60 days as a proportion of the total number of people who tested positive or negative in a given period; and who never tested positive in the previous 60 days).
    #               """)
    col22.plotly_chart(graph_tx_incid, use_container_width=True)
    # col22.markdown("""
    #                The incidence rate is the number of people who tested positive (RT-PCR and antigenic test)
    #                In the graph above, it is the Incidence Rate for the first time in more than 60 days related to the population size. It is expressed per 100,000 population)
    #                """)

#streamlit_analytics.stop_tracking(unsafe_password="123")
