'''
COMP9418 Assignment 2
This file is the example code to show how the assignment will be tested.

Name: Eu Shaun Lim      zID: z5156345

Name: Utkarsh Gulumkar  zID: z5287077
'''

# Make division default to floating-point, saving confusion
from __future__ import division
from __future__ import print_function

# Allowed libraries 
import numpy as np
import pandas as pd
import math
from itertools import product, combinations
from collections import OrderedDict as odict
import copy
import datetime
import re

# external python files
from state import initial_state
from hidden_markov_model import hmm, update_hmm_actions
from particle_filtering import simulate, get_pf_actions


###################################
# Code stub
# 
# The only requirement of this file is that is must contain a function called get_action,
# and that function must take sensor_data as an argument, and return an actions_dict
# 

# this global state variable demonstrates how to keep track of information over multiple 
# calls to get_action 
state = initial_state()
# training data for on-the-fly learning
data = pd.read_csv('data.csv')
df = data.drop(['reliable_sensor1','reliable_sensor2','reliable_sensor3','reliable_sensor4',
                'unreliable_sensor1','unreliable_sensor2','unreliable_sensor3','unreliable_sensor4',
                'robot1','robot2','door_sensor1','door_sensor2','door_sensor3','door_sensor4',
                'electricity_price','Unnamed: 0'], axis=1)
df = df.set_index('time')

# sample number of workers from Normal distribution
num_ppl = np.int32(np.round(np.random.normal(20, 1)))

# assign everyone to outside at the start (08:00:00)
for i in range(num_ppl):
    state['outside']['ppl_in_room'].append(i)

def update_robot_actions(actions_dict, sensor_data):
    # make new copy
    new_actions = copy.deepcopy(actions_dict)

    # check which room robot is in
    for robot in ['robot1', 'robot2']:
        room = sensor_data[robot][0]
        if room[0] == 'r':
            num = re.findall("\d+", room)[0]
            lights = 'lights' + num
            # get number of people in the room
            num_ppl = sensor_data[robot][1]
            if num_ppl > 0:
                new_actions[lights] = 'on'
            else:
                new_actions[lights] = 'off'

    return new_actions

def get_action(sensor_data):
    # declare state as a global variable so it can be read and modified within this function
    global state
    global df

    # if sensor reports None, assume there is motion
    for sensor, val in sensor_data.items():
        if val is None:
            sensor_data[sensor] = 'motion'

    # particle filtering for each time step
    simulate(state, df, str(sensor_data['time']))
    actions_dict = get_pf_actions(state)

    # hidden markov model for the rooms with sensors
    room16, room5, room25, room31, room1, room24 = hmm(sensor_data)

    # update actions_dict with decisions from HMM
    actions_dict = update_hmm_actions(actions_dict, room16, room5, room25, room31, room1, room24) 

    # update actions_dict with decisions from robot sensor
    actions_dict = update_robot_actions(actions_dict, sensor_data)

    return actions_dict



