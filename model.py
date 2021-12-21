# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 18:47:41 2021

@author: WILLIAMU Vaihau
"""

import os
import datetime

# General variables ----------------------------------------------------------

# Path to the project folder

app_info = {
    "name"   : "COVID 19 DashBoard",
    "logo"   : ":microscope:",
    "layout" : "wide",
    "sidebar": "collapsed",
    "author" : {
        "last_name" : "Williamu",
        "first_name" : "Vaihau"
        }
    }

app_info["author"]["initials"] = app_info["author"]["last_name"].upper()[0] +\
                                 app_info["author"]["first_name"].upper()[0]

PROJECT_FOLDER = os.path.dirname(__file__)

pth = lambda fold : os.path.join(PROJECT_FOLDER, fold)


folder = {
    'data' : pth('Data')
    }

page_config = {
    "page_title" : app_info["name"] + " - " + app_info["author"]["initials"],
    "layout" : app_info["layout"],
    "page_icon" : app_info["logo"],
    "initial_sidebar_state" : app_info['sidebar']
    }

date_today = datetime.date.today().strftime("%Y-%m-%d")

date_yesterday = datetime.date.today() - datetime.timedelta(days=1)
date_yesterday = date_yesterday.strftime("%Y-%m-%d")

# Controller variables -------------------------------------------------------

cache_duration = {
    'short' : 60*60*6,
    'long' : 3600*12
    }

replacement_geojson_df = {
    'Bourgogne-Franche-Comté' : 'Bourgogne et Franche-Comté',
    'La Réunion' : 'Réunion',
    'Nouvelle-Aquitaine' : 'Nouvelle Aquitaine',
    'Auvergne-Rhône-Alpes' : 'Auvergne et Rhône-Alpes'
}

replacement_df_geojson = {v:k for k,v in replacement_geojson_df.items()}

map_isolate = {
    'lib_reg' : ['Guyane', 'Martinique', 'Guadeloupe', 'Mayotte', 'La Réunion']
    }

url = {
    "dataset" : {
        "general" : "https://www.data.gouv.fr/fr/datasets/r/f335f9ea-86e3-4ffa-9684-93c009d5e617",
        "partition" : "https://www.data.gouv.fr/fr/datasets/r/5c4e1452-3850-4b59-b11c-3dd51d7fb8b5"
    },
    "geojson" : {
        "lib_reg" : "https://france-geojson.gregoiredavid.fr/repo/regions.geojson",
        "lib_dep" : "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
    }
}

date_col = 'date'

## Map variables
chx_cat_col = ['lib_reg', 'lib_dep']
filter_zone_key = ['keep', 'location']

default_title_color_bar = "Number of Patients"
default_title_graph = "Progression"
default_projection_type = "orthographic"
default_color_continuous_scale = "orrd"

zone_isolated = ['Guyane', 'Martinique', 'Mayotte', 'Guadeloupe', 'La Réunion']

dict_txt = {
    'chx_opt' : {
        'hosp' : 'Hospitalized',
        'rea' : 'In Intensive care',
        'tx_pos' : "Positivity rate of virological tests",
        'tx_incid' : "Incidence rate",
        "TO" : "Occupancy rate of hospital beds",
        "R" : "Virus reproduction factor"
    },
    'chx_cat' : {
        'lib_reg' : 'Region',
        'lib_dep' : 'Department'
    }
}

# VIEW variables -------------------------------------------------------------

urls = {
   "WB": {
    "DATAGOUV" : "https://www.data.gouv.fr/fr/datasets/synthese-des-indicateurs-de-suivi-de-lepidemie-covid-19/"
       },
   "DATA" : {
    "DATAGOUV" : {
        'general' : "https://www.data.gouv.fr/fr/datasets/r/f335f9ea-86e3-4ffa-9684-93c009d5e617",
        'detailed' : "https://www.data.gouv.fr/fr/datasets/r/5c4e1452-3850-4b59-b11c-3dd51d7fb8b5"
        },
    "GEOJSON" : {
        'lib_reg' : 'https://france-geojson.gregoiredavid.fr/repo/regions.geojson'
        }
       }
        }

nwv = {
       "mano_var" : {
           "img" : "https://img.shields.io/badge/Mano-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&link=https://www.linkedin.com/in/manomathew/",
           "url" : "https://www.linkedin.com/in/manomathew/"
           },
       "vaihau" : {
           "img" : "https://img.shields.io/badge/Vaihau-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&link=https://www.linkedin.com/in/vaihau-williamu/",
           "url" : "https://www.linkedin.com/in/vaihau-williamu/"
           }
      }

mano_btn = f"[![Connect]({nwv['mano_var']['img']})]({nwv['mano_var']['url']})"
vaihau_btn = f"[![Connect]({nwv['vaihau']['img']})]({nwv['vaihau']['url']})"

network_btn = f"{mano_btn}&nbsp{vaihau_btn}"

