# -*- coding: utf-8 -*-
"""
@author: WILLIAMU Vaihau
"""

import streamlit as st
import model
import model as md_data
import controller as ctrl
import controller

# Configuration --------------------------------------------------------------
st.set_page_config(**model.page_config)

### Sources

df = controller.load_data(model.urls['DATA']['DATAGOUV']['general'])
    # df_detailed = ctrl.load_data(model.urls['DATA']['DATAGOUV']['detailed'])

# Layout ---------------------------------------------------------------------

## Sidebar --

container_network = st.sidebar.empty()


## Main

container_header = st.empty()

container_kpi = st.empty()

container_main = st.empty()

st.markdown("[@Source : data.gouv]({})".format(model.urls["WB"]['DATAGOUV']))

# Condition ------------------------------------------------------------------

## Sidebar --

with container_network.container():
    st.markdown("## \U0001F4CC Contact us")
    st.markdown('**Mano Mathew**')
    st.write(md_data.mano_btn)
    st.markdown("**WILLIAMU Vaihau** *@Developper*")
    st.write(md_data.vaihau_btn)
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
    ctrl.display_general_metric(df)
    
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

    # p_by = 'lib_reg'
    # main_zone = [zone for zone in df_detailed[p_by].unique() \
    #                  if zone not in model.map_isolate[p_by]]
    # st.write(main_zone)
    # fig_map = ctrl.show_map(df_detailed, p_by, sort=main_zone)
    # st.plotly_chart(fig_map)
    

with container_main.container():
    
    # Variables
    st.header('# The statistical progression')
    
    graph_R = ctrl.chart_progress_stats(df, 'R', 'Virus reproduction factor - R')
    # graph_occ_rate = ctrl.chart_progress_stats(df, 'occ', 'Occupation rate - TO')
    graph_tx_pos = ctrl.chart_progress_stats(df, 'tx_pos', "Positivity rate of virological tests : tx_pos")
    graph_tx_incid = ctrl.chart_progress_stats(df, 'tx_incid', "Incidence rate : tx_incid")
    
    # Layout
    
    st.plotly_chart(graph_R, use_container_width=True)
    
    st.markdown("""
                Evolution of the R0: the number of reproduction of the virus  
                It is the average number of people that an infected person can contaminate. If the effective **R is greater than 1, the epidemic is growing; if it is less than 1, the epidemic is declining**
                """)
                
    col11, col22 = st.columns(2)
    
    col11.plotly_chart(graph_tx_pos, use_container_width=True)
    col11.markdown("""
                  The positivity rate corresponds to the number of people tested positive (RT-PCR and antigenic test)  
                  The above graph refers to the rate of virological test positivity for the first time in more than 60 days as a proportion of the total number of people who tested positive or negative in a given period; and who never tested positive in the previous 60 days).
                  """)
    col22.plotly_chart(graph_tx_incid, use_container_width=True)
    col22.markdown("""
                   The incidence rate is the number of people who tested positive (RT-PCR and antigenic test)  
                   In the graph above, it is the Incidence Rate for the first time in more than 60 days related to the population size. It is expressed per 100,000 population)
                   """)
                   
    # st.plotly_chart(graph_occ_rate, use_container_width=True)
    # st.markdown("""
    #             Occupancy rate: hospital tension on resuscitation capacity  
    #             This is the proportion of patients with COVID-19 currently in resuscitation, intensive care, or continuous monitoring units relative to total beds in initial capacity, i.e., before increasing resuscitation bed capacity in a hospital
    #             """)
    
    
    
    
    
    
    # ### Confirmed Case
    # st.plotly_chart(graph_conf_case, use_container_width=True)
    
    # ### Hospitalized and in reanimation
    # st.plotly_chart(graph_hosp_rea, use_container_width=True)
    
    # st.header('The status of deaths due to COVID-19')
    # ### Dead
    # st.plotly_chart(graph_dead, use_container_width=True)
