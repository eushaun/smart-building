# Make division default to floating-point, saving confusion
from __future__ import division
from __future__ import print_function

# Allowed libraries 
import numpy as np
import pandas as pd
import math
from itertools import product, combinations
from collections import OrderedDict as odict
from tabulate import tabulate
import copy
import datetime
import re
import pickle

# calculates cumulative distribution function
def get_cdf(pdf):
    cdf = {}
    sum = 0
    for room, prob in pdf.items():
        sum += prob
        cdf[room] = np.round(sum,4)

    return cdf, sum

# resamples new room for the people in a given room
def get_new_room(transitionProb):
    transitionCdf, sum = get_cdf(transitionProb)
    sampled_prob = np.random.uniform(0, sum)

    # makes sure cdf is in sorted order
    for room, cdf in sorted(transitionCdf.items(), key=lambda x: x[1]):
        if sampled_prob <= cdf:
            return room

def simulate(map, time, transitionModel):
    # transitionModel = get_transition_model(map, df, time)
    # new dict to store updated rooms of each person
    new_rooms = {}
    for room in map:
        new_rooms[room] = []

    # approximate movement by resampling transition probabilities of each room
    for room in map:
        # only check rooms that are not empty
        if len(map[room]['ppl_in_room']):
            # print(time, room)
            # print(transitionModel[time][room])
            for ppl in map[room]['ppl_in_room']:
                # assign new room to each people
                new_room = get_new_room(transitionModel[time][room])
                new_rooms[new_room].append(ppl)

    # update map according to newly assigned rooms
    for room in map:
        update = copy.deepcopy(new_rooms[room])
        map[room]['ppl_in_room'] = update

# decide whether to turn lights on or off based on particle filtering
def get_pf_actions(map):
    actions = {}
    for room in map:
        if room[0] == 'r':
            num = re.findall("\d+", room)[0]
            lights = 'lights' + num
            if len(map[room]['ppl_in_room']):
                actions[lights] = 'on'
            else:
                actions[lights] = 'off'

    return actions

###############################
## UNIFORM DISTRIBUTION MODEL
###############################

# def get_transition_model(map):
#     transitionModel = {}
#     for room, neighbours in map.items():
#         states = {}
#         states[room] = np.nan
#         # add neighbouring rooms to possible next state
#         for neighbour in neighbours['adjacent_rooms']:
#             # avoid duplicates
#             if neighbour not in states:
#                 states[neighbour] = np.nan
#             # add rooms next to neighbouring rooms to possible next state
#             for next_neighbour in map[neighbour]['adjacent_rooms']:
#                 # avoid ownself and duplicates
#                 if next_neighbour != room and next_neighbour not in states:
#                     states[next_neighbour] = np.nan
#         # set uniform distribution for transition probabilities
#         for possibleStates in states:
#             states[possibleStates] = 1 / len(states)

#         transitionModel[room] = states

#     return transitionModel

##################################
## SLOW CALCULATION, USED PICKLE
##################################
# def get_transition_model(map, df, time):
#     transitionModel = {}
#     for room, neighbours in map.items():
#         # no point calculating probabilites if no one in the room
#         if len(map[room]['ppl_in_room']) == 0:
#             continue
#         states = {}
#         # only calculate rooms with people
#         if df.loc[time, room] != 0:
#             states[room] = calculate_transition_prob(df, room, time)
#         # add neighbouring rooms to possible next state
#         for neighbour in neighbours['adjacent_rooms']:
#             # avoid duplicates
#             if neighbour not in states:
#                 # only calculate rooms with people
#                 if df.loc[time, neighbour] != 0:
#                     states[neighbour] = calculate_transition_prob(df, neighbour, time)
#             # add rooms next to neighbouring rooms to possible next state
#             for next_neighbour in map[neighbour]['adjacent_rooms']:
#                 # avoid ownself and duplicates
#                 if next_neighbour != room and next_neighbour not in states:
#                     # only calculate rooms with people
#                     if df.loc[time, next_neighbour] != 0:
#                         states[next_neighbour] = calculate_transition_prob(df, next_neighbour, time)
#         # normalize probabilities
#         for possibleState in states:
#             states[possibleState] = normalize(possibleState, states)
#         transitionModel[room] = states
#     return transitionModel

# # calculate P(X_t | X_t-1) for all the rooms
# def calculate_transition_prob(df, next_room, time):
#     # get total number of ppl in data.csv
#     total_ppl = df.loc['08:00:15',:].sum()
#     return df.loc[time, next_room] / total_ppl

# # normalize probabilities
# def normalize(possibleState, states):
#     sum = 0
#     for state in states:
#         sum += states[state]
#     return np.round(states[possibleState] / sum, 4)