#
# Client-side python app for Final Project, this time working with
# web service, which in turn uses AWS S3 ato implement
# a simple ML Model for rental price prediction and apartment description generation.
#
# Final Project for CS 310
#
# Authors:
#   YOUR NAME
#   Sharika Mahadevan, Hye Won Hwang, Alejandra Lelo de Larrea Ibarra
#   Northwestern University
#   CS 310
#

###################################################################
#
# Importing packages
#

import os
import pathlib
import logging
import sys
import base64
from configparser import ConfigParser

import requests  # calling web service
# import json  # relational-object mapping

# import matplotlib.pyplot as plt
# import matplotlib.image as img

import streamlit as st

#########################################################################
# main
#
st.title('    ** Welcome to Rental Wizard **')
# Create two columns for Description and Price buttons
col1, col2, col3 = st.columns([0.3,0.6,0.2])

with col2:
    st.image("client-files/logo.png", width = 300)

st.header('Who are we?')
st.write('Welcome to Rental Wizard, your ultimate tool for simplifying the rental experience! We understand that finding the perfect rental property and creating an attractive listing can be a daunting task. That\'s why we\'ve designed Rental Wizard to make this process not only straightforward but also effective. As renters ourselves, we know the frustration of trying to determine a fair rental price and then struggling to craft an appealing listing. With Rental Wizard, we\'ve taken the guesswork out of the equation.')
st.write('With our user-friendly platform, you can predict a reasonable rental price for your property with ease, ensuring that you\'re not overcharging or undervaluing your rental. Our powerful algorithms consider various factors like location, property size, and market trends, giving you a reliable estimate.')
st.write('But that\'s not all – we also provide you with a beautiful and compelling summary for your rental posting. We understand the importance of first impressions, and our expertly crafted descriptions will showcase your property\'s unique features and amenities, making it stand out in the competitive rental market.')
st.write('At Rental Wizard, we\'re committed to simplifying the rental process for you. So, let us help you find the perfect rental price and create a captivating listing that will have renters lining up to inquire about your property. It\'s time to make renting a breeze, and we\'re here to guide you every step of the way. Let\'s make the rental experience more enjoyable and stress-free together!')
print()

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

#
# what config file should we use for this session?
#
config_file = 'client-files/rental-wizard-client-config.ini'

#
# setup base URL to web service:
#
configur = ConfigParser()
configur.read(config_file)
baseurl = configur.get('client', 'webservice')

print(baseurl)
