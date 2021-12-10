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


### DATA GOUV

st.header('FROM DATA GOUV')

data_gouv_KPI = st.empty()

dg_content = st.empty()

st.markdown("[@Source : data.gouv]({})".format(model.urls["WB"]['DATAGOUV']))

# Condition ------------------------------------------------------------------


## DATA GOUV

df = ctrl.load_data(model.urls['DATA']['DATAGOUV'])

with dg_content.container():
    
    st.subheader('#France')
    
    ctrl.display_today_metric(df)
    
    ### Confirmed Case
    graph_conf_case = ctrl.load_chart(df, 'conf_case')
    st.plotly_chart(graph_conf_case, use_container_width=True)
    
    ### Hospitalized and in reanimation
    graph_hosp_rea = ctrl.load_chart(df, 'hosp_rea')
    st.plotly_chart(graph_hosp_rea, use_container_width=True)
    
    
    nbr_death_total = df[df['date']==model.date_today].iloc[0, df[df['date']==model.date_today].columns.tolist().index("dchosp")]
    st.markdown('Total number of patients who died in French hospitals : **{:.0f}**'.format(nbr_death_total))

    ### Dead
    graph_dead = ctrl.load_chart(df, 'death')
    st.plotly_chart(graph_dead, use_container_width=True)
