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
    "page_icon" : app_info["logo"]
    }

date_today = datetime.date.today().strftime("%Y-%m-%d")

date_yesterday = datetime.date.today() - datetime.timedelta(days=1)
date_yesterday = date_yesterday.strftime("%Y-%m-%d")

# Controller variables -------------------------------------------------------




# VIEW variables -------------------------------------------------------------

urls = {
   "WB": {
    "DATAGOUV" : "https://www.data.gouv.fr/fr/datasets/synthese-des-indicateurs-de-suivi-de-lepidemie-covid-19/"       
       },
   "DATA" : {
    "DATAGOUV" : "https://www.data.gouv.fr/fr/datasets/r/f335f9ea-86e3-4ffa-9684-93c009d5e617"
       }
        }