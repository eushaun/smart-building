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

from state import initial_state

def normalize(states):
    normalized = {}
    sum = 0
    for state in states:
        sum += states[state]
    for state in states:
        normalized[state] = np.round(states[state] / sum, 4)
    return normalized

def get_adjacent_rooms(df, room, time, map):
    states = {}
    # non-zero probability
    if df.loc[time, room]:
        states[room] = df.loc[time, room]
    # add neighbouring rooms to possible next state
    for neighbour in map[room]['adjacent_rooms']:
        # avoid duplicates
        if neighbour not in states:
            # non-zero probability
            if df.loc[time, neighbour]:
                states[neighbour] = df.loc[time, neighbour]
        # add rooms next to neighbouring rooms to possible next state
        for next_neighbour in map[neighbour]['adjacent_rooms']:
            # avoid ownself and duplicates
            if next_neighbour != room and next_neighbour not in states:
                # non-zero probability
                if df.loc[time, next_neighbour]:
                    states[next_neighbour] = df.loc[time, next_neighbour]
    return normalize(states)

def main():
    map = initial_state()
    data = pd.read_csv('data.csv')
    df = data.drop(['reliable_sensor1','reliable_sensor2','reliable_sensor3','reliable_sensor4',
                    'unreliable_sensor1','unreliable_sensor2','unreliable_sensor3','unreliable_sensor4',
                    'robot1','robot2','door_sensor1','door_sensor2','door_sensor3','door_sensor4',
                    'electricity_price','Unnamed: 0'], axis=1)
    df = df.set_index('time')
    num_ppl = df.loc['08:00:15',:].sum()
    df = df.apply(lambda x: np.round(x/num_ppl, 4))
    df_dict = df.to_dict(orient='index')

    transition = {}
    for time in df_dict:
        transition[time] = {}
        for room in df_dict[time]:
            # if df.loc[time, room] != 0:
            transition[time][room] = get_adjacent_rooms(df, room, time, map)

    with open('parameters.pickle', 'wb') as p:
        pickle.dump(transition, p, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    main()