# -*- coding: utf-8 -*-
"""
@author: WILLIAMU Vaihau
"""

import streamlit as st
import model
import controller as ctrl

# Configuration --------------------------------------------------------------
st.set_page_config(**model.page_config)


# Layout ---------------------------------------------------------------------

## Sidebar --



## Main

container_header = st.empty()

container_kpi = st.empty()

container_main = st.empty()

st.markdown("[@Source : data.gouv]({})".format(model.urls["WB"]['DATAGOUV']))

# Condition ------------------------------------------------------------------

## Loading data

### Sources
df = ctrl.load_data(model.urls['DATA']['DATAGOUV'])

### Record
record_date_last = ctrl.get_last_record_date(df)


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
    

with container_main.container():
    
    st.header('# Situation in hospitals')
    
    ### Confirmed Case
    st.plotly_chart(graph_conf_case, use_container_width=True)
    
    ### Hospitalized and in reanimation
    st.plotly_chart(graph_hosp_rea, use_container_width=True)
    
    st.header('The status of deaths due to COVID-19')
    ### Dead
    st.plotly_chart(graph_dead, use_container_width=True)
