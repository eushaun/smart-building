# Make division default to floating-point, saving confusion
from __future__ import division
from __future__ import print_function

# Allowed libraries 
import numpy as np
import pandas as pd
import scipy as sp
import scipy.special
import heapq as pq
import matplotlib as mp
import matplotlib.pyplot as plt
import math
from itertools import product, combinations
from collections import OrderedDict as odict
import collections
from graphviz import Digraph, Graph
from tabulate import tabulate
import copy
import sys
import os
import datetime
import sklearn
import ast
import re

# TODO: NEED TO FIGURE OUT PROPER TRANSITION PROBABILITIES
# FOR NOW USE UNIFORM DISTRIBUTION
def get_transition_model(map):
    transitionModel = {}
    for room, neighbours in map.items():
        states = {}
        states[room] = np.nan
        # add neighbouring rooms to possible next state
        for neighbour in neighbours['adjacent_rooms']:
            # avoid duplicates
            if neighbour not in states:
                states[neighbour] = np.nan
            # add rooms next to neighbouring rooms to possible next state
            for next_neighbour in map[neighbour]['adjacent_rooms']:
                # avoid ownself and duplicates
                if next_neighbour != room and next_neighbour not in states:
                    states[next_neighbour] = np.nan
        # set uniform distribution for transition probabilities
        for possibleStates in states:
            states[possibleStates] = 1 / len(states)

        transitionModel[room] = states

    return transitionModel

# calculates cumulative distribution function
def get_cdf(pdf):
    cdf = {}
    sum = 0
    for room, prob in pdf.items():
        sum += prob
        cdf[room] = np.round(sum,4)

    return cdf

# resamples new room for the people in a given room
def get_new_room(transitionProb):
    sampled_prob = np.random.uniform(0,1)
    transitionCdf = get_cdf(transitionProb)

    # makes sure cdf is in sorted order
    for room, cdf in sorted(transitionCdf.items(), key=lambda x: x[1]):
        if sampled_prob <= cdf:
            return room

# simulate movement for one time step
def simulate(map):
    transitionModel = get_transition_model(map)
    # new dict to store updated rooms of each person
    new_rooms = {}
    for room in map:
        new_rooms[room] = []

    # approximate movement by resampling transition probabilities of each room
    moved = []
    for room in map:
        # only check rooms that are not empty
        if len(map[room]['ppl_in_room']):
            # print("In:", room)
            for ppl in map[room]['ppl_in_room']:
                # print(ppl)
                # skip if already moved
                if ppl in moved:
                    print("already moved:", ppl)
                    continue
                # mark person as moved
                moved.append(ppl)
                # assign new room to each people 
                new_room = get_new_room(transitionModel[room])
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
