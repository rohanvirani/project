import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
import pgeocode
from sklearn.metrics.pairwise import haversine_distances
from math import radians 
import Levenshtein

def great_circle(loc1, lat2, long2):
    rest = np.array(loc1)
    comparison = np.array([lat2,long2]).reshape(1,2)
    rest_in_radians = np.radians(rest)
    comp_in_radians = np.radians(comparison)
    result = haversine_distances(rest_in_radians, comp_in_radians)
    result = result * 6371000/1000
    return result 

def compare(food_sim, radius):
    lat = restaurant_data['latitude'].iloc[0]
    lon = restaurant_data['longitude'].iloc[0]
    mean_price = restaurant_data['median_price'].iloc[0]
    sim_rest_price = data.loc[(data['median_price'] > mean_price - price_sim) & (data['median_price'] < mean_price + price_sim)]
    rest_comp = sim_rest_price.loc[(sim_rest_price['latitude']!=lat) & (sim_rest_price['longitude']!=lon)]
    rest_comp['distance'] = great_circle(rest_comp[['latitude','longitude']],lat,lon)
    trial_close = rest_comp.loc[rest_comp['distance'] < radius]
    if len(trial_close) != 0:
        trial_close['food_sim'] = trial_close.apply(lambda x: Levenshtein.distance(x['menu_items'],  str(meal_option)), axis=1)
        close_food = trial_close.loc[trial_close['food_sim'] < food_sim]
        compared_meals = close_food['menu_items'].value_counts().rename_axis('Meals').reset_index(name='Count')
    else:
        return ([], [])
    return (compared_meals, close_food)


data = pd.read_csv('./pizza_menu_data.csv')

title = st.title('Compare Dishes Product Demo')

restaurant_option = st.selectbox('Which restaurant is this?',(data['restaurant_url'].unique()))

restaurant_data = data.loc[data['restaurant_url']==str(restaurant_option)]
meal_option = st.selectbox('Which meal are we comparing?',(restaurant_data['menu_items'].unique()))

food_sim = st.slider(label='How sensitive do you want the meal comparison?',value=4, min_value = 0, max_value = 10)
radius = st.slider(label='How far around your restaurant do you want to search (km)',value=5, min_value = 0, max_value = 10)
price_sim = st.slider(label="Choose the maximum difference in average prices between your restaurant and compared restaurants",value=2, min_value = 0, max_value = 5)

if st.button('Find Similar Meals'):
    compared_meals, close_foods = compare(food_sim, radius)
    if len(close_foods) != 0:
        st.title("Compared Dishes")
        st.table(compared_meals)
        minimum = close_foods['prices'].min()
        maximum = close_foods['prices'].max()
        mean = close_foods['prices'].mean()
        meal_data = restaurant_data.loc[restaurant_data['menu_items']==str(meal_option)]
        meal_price = meal_data['prices'].iloc[0]
        st.title("Compared Restaurants")
        st.table(close_foods['restaurant_url'].unique())
        st.title("Aggregate statistics")
        st.write('Your item costs £' + str(round(meal_price,2)))
        st.write('The minimum price in your local area is £' + str(round(minimum,2)))
        st.write('The maximum price in your local area is £' + str(round(maximum,2)))
        st.write('The average price in your local area is £' + str(round(mean,2)))


