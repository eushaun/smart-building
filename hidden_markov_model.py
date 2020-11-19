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

# calculate transition and emission probablities from data
def calc_prob(data, room_num, sensor):
    room = data[['time']]

    # shift values down to get X_t-1
    room['X_t-1'] = data[room_num].shift(1)
    room['X_t'] = data[room_num]
    room['E_t'] = data[sensor]

    # drop first row (X_1)
    room.drop(room.index[0], inplace=True)
    room['X_t-1'] = room['X_t-1'].astype('int64')

    # chance values in X_t to 1 if > 1
    # motion to 1, no motion to 0
    room.loc[room['X_t'] > 1, 'X_t'] = 1
    room.loc[room['X_t-1'] > 1, 'X_t-1'] = 1
    room.loc[room['E_t'] == 'no motion', 'E_t'] = 0
    room.loc[room['E_t'] == 'motion', 'E_t'] = 1

    # calculate transition probabilities P(X_t | X_t-1)
    on = room[room['X_t-1'] == 1].drop(['time','E_t'], axis=1)
    print("Transition probabilities:")
    print("P(off | on) =", np.round(on['X_t'].value_counts()[0] / len(on), 4))
    print("P(on | on) =", np.round(on['X_t'].value_counts()[1] / len(on), 4))

    off = room[room['X_t-1'] == 0].drop(['time','E_t'], axis=1)
    print("P(off | off) =", np.round(off['X_t'].value_counts()[0] / len(off), 4))
    print("P(on | off) =", np.round(off['X_t'].value_counts()[1] / len(off), 4))

    # calculate emission probabilities P(E_t | X_t)
    on = room[room['X_t'] == 1].drop(['time','X_t-1'], axis=1)
    print("\nEmission probabilities:")
    print("P(no motion | on) =", np.round(on['E_t'].value_counts()[0] / len(on), 4))
    print("P(motion | on) =", np.round(on['E_t'].value_counts()[1] / len(on), 4))

    off = room[room['X_t'] == 0].drop(['time','X_t-1'], axis=1)
    print("P(no motion | off) =", np.round(off['E_t'].value_counts()[0] / len(off), 4))
    print("P(motion | off) =", np.round(off['E_t'].value_counts()[1] / len(off), 4))

def print_prob():
    # read data
    data = pd.read_csv('data.csv')
    print("ROOM 16:")
    calc_prob(data, "r16", "reliable_sensor1")
    print("\nROOM 5:")
    calc_prob(data, "r5", "reliable_sensor2")
    print("\nROOM 25:")
    calc_prob(data, "r25", "reliable_sensor3")
    print("\nROOM 31:")
    calc_prob(data, "r31", "reliable_sensor4")
    print("\nROOM 1:")
    calc_prob(data, "r1", "unreliable_sensor3")
    print("\nROOM 24:")
    calc_prob(data, "r24", "unreliable_sensor4")

#####################################
### CODE TAKEN FROM WEEK 5 TUTORIAL
#####################################

def printFactor(f):
    """
    argument 
    `f`, a factor to print on screen
    """
    # Create a empty list that we will fill in with the probability table entries
    table = list()
    
    # Iterate over all keys and probability values in the table
    for key, item in f['table'].items():
        # Convert the tuple to a list to be able to manipulate it
        k = list(key)
        # Append the probability value to the list with key values
        k.append(item)
        # Append an entire row to the table
        table.append(k)
    # dom is used as table header. We need it converted to list
    dom = list(f['dom'])
    # Append a 'Pr' to indicate the probabity column
    dom.append('Pr')
    print(tabulate(table,headers=dom,tablefmt='orgtbl'))

def prob(factor, *entry):
    """
    argument 
    `factor`, a dictionary of domain and probability values,
    `entry`, a list of values, one for each variable in the same order as specified in the factor domain.
    
    Returns p(entry)
    """

    return factor['table'][entry]       

def join(f1, f2, outcomeSpace):
    """
    argument 
    `f1`, first factor to be joined.
    `f2`, second factor to be joined.
    `outcomeSpace`, dictionary with the domain of each variable
    
    Returns a new factor with a join of f1 and f2
    """
    
    # First, we need to determine the domain of the new factor. It will be union of the domain in f1 and f2
    # But it is important to eliminate the repetitions
    common_vars = list(f1['dom']) + list(set(f2['dom']) - set(f1['dom']))
    
    # We will build a table from scratch, starting with an empty list. Later on, we will transform the list into a odict
    table = list()
    
    # Here is where the magic happens. The product iterator will generate all combinations of varible values 
    # as specified in outcomeSpace. Therefore, it will naturally respect observed values
    for entries in product(*[outcomeSpace[node] for node in common_vars]):
        
        # We need to map the entries to the domain of the factors f1 and f2
        entryDict = dict(zip(common_vars, entries))
        f1_entry = (entryDict[var] for var in f1['dom'])
        f2_entry = (entryDict[var] for var in f2['dom'])
        
        # Use the fuction prob to calculate the probability 
        p1 = prob(f1, *f1_entry)           
        p2 = prob(f2, *f2_entry)           
        
        # Create a new table entry with the multiplication of p1 and p2
        table.append((entries, p1 * p2))
    return {'dom': tuple(common_vars), 'table': odict(table)}


def marginalize(f, var, outcomeSpace):
    """
    argument 
    `f`, factor to be marginalized.
    `var`, variable to be summed out.
    `outcomeSpace`, dictionary with the domain of each variable
    
    Returns a new factor f' with dom(f') = dom(f) - {var}
    """    
    
    # Let's make a copy of f domain and convert it to a list. We need a list to be able to modify its elements
    new_dom = list(f['dom'])
    
    new_dom.remove(var)       # Remove var from the list new_dom 
    table = list()            # Create an empty list for table
    for entries in product(*[outcomeSpace[node] for node in new_dom]):
        s = 0;                     # Initialize the summation variable s. 
        # We need to iterate over all possible outcomes of the variable var
        for val in outcomeSpace[var]:
            # To modify the tuple entries, we will need to convert it to a list
            entriesList = list(entries)
            # We need to insert the value of var in the right position in entriesList
            entriesList.insert(f['dom'].index(var), val)
            # Calculate the probability of factor f for entriesList. 
            p = prob(f, *tuple(entriesList))   
            # Sum over all values of var by accumulating the sum in s.  
            s = s + p                            
            
        # Create a new table entry with the multiplication of p1 and p2
        table.append((entries, s))
    return {'dom': tuple(new_dom), 'table': odict(table)}

def evidence(var, e, outcomeSpace):
    """
    argument 
    `var`, a valid variable identifier.
    `e`, the observed value for var.
    `outcomeSpace`, dictionary with the domain of each variable
    
    Returns dictionary with a copy of outcomeSpace with var = e
    """    
    # Make a copy of outcomeSpace
    newOutcomeSpace = outcomeSpace.copy()      
    # Replace the domain of variable var with a tuple with a single element e
    newOutcomeSpace[var] = (e,)                
    return newOutcomeSpace

def normalize(f):
    """
    argument 
    `f`, factor to be normalized.
    
    Returns a new factor f' as a copy of f with entries that sum up to 1
    """ 
    table = list()
    sum = 0
    for k, p in f['table'].items():
        sum = sum + p
    for k, p in f['table'].items():
        table.append((k, p/sum))
    return {'dom': f['dom'], 'table': odict(table)}

def maximize(f, var, outcomeSpace):
    """
    argument 
    `f`, factor to be marginalized.
    `var`, variable to be maximized out.
    `outcomeSpace`, dictionary with the domain of each variable
    
    Returns a new factor f' with dom(f') = dom(f) - {var}
    """    
    # Let's make a copy of f domain and convert it to a list. We need a list to be able to modify its elements
    new_dom = list(f['dom'])
    new_dom.remove(var)            # Remove var from the list new_dom
    table = list()                 # Create an empty list for table.
    for entries in product(*[outcomeSpace[node] for node in new_dom]):     
        m = 0;                  # Initialize the maximization variable m.

        # We need to iterate over all possible outcomes of the variable var
        for val in outcomeSpace[var]:
            # To modify the tuple entries, we will need to convert it to a list
            entriesList = list(entries)
            # We need to insert the value of var in the right position in entriesList
            entriesList.insert(f['dom'].index(var), val)
            # Calculate the probability of factor f for entriesList.
            p = prob(f, *tuple(entriesList))     
            # Maximize over all values of var by storing the max value in m.
            m = max(m, p)                        
            
        # Create a new table entry with the multiplication of p1 and p2
        table.append((entries, m))
    return {'dom': tuple(new_dom), 'table': odict(table)}

def viterbiOnline(f, transition, emission, stateVar, emissionVar, emissionEvi, outcomeSpace, norm):
    """
    argument 
    `f`, factor that represents the previous state.
    `transition`, transition probabilities from time t-1 to t.
    `emission`, emission probabilities.
    `stateVar`, state (hidden) variable.
    `emissionVar`, emission variable.
    `emissionEvi`, emission observed evidence. If undef, we do only the time update
    `outcomeSpace`, dictionary with the domain of each variable.
    
    Returns a new factor that represents the current state.
    """ 

    # Set fCurrent as a copy of f
    fCurrent = f.copy()
    # Set the f_previous domain to be a list with a single variable name appended with '_t-1' to indicate previous time step
    fCurrent['dom'] = (stateVar + '_t-1', )       
    # Make the join operation between fCurrent and the transition probability table    
    fCurrent = join(fCurrent, transition, outcomeSpace)        
    # Eliminate the randVariable_t-1 with the maximization operation
    fCurrent = maximize(fCurrent, fCurrent['dom'][0], outcomeSpace)        
    # If emissionEvi == None, we will assume this time step has no observed evidence    
    if emissionEvi != None:                  # WARNING: do not change this line
        # Set evidence in the form emissionVar = emissionEvi    
        newOutcomeSpace = evidence(emissionVar, emissionEvi, outcomeSpace)     
        # Make the join operation between fCurrent and the emission probability table. Use the newOutcomeSpace    
        fCurrent = join(fCurrent, emission, newOutcomeSpace)      
        # Marginalize emissionVar. Use the newOutcomeSpace    
        fCurrent = marginalize(fCurrent, emissionVar, newOutcomeSpace)         
        # Normalize fcurrent.
        if norm:
            fCurrent = normalize(fCurrent)           
    # Set the domain of w to be name of the random variable without time index
    fCurrent['dom'] = (stateVar, )
    return fCurrent

#################################################
### INITIALIZE HIDDEN MARKOV MODEL PARAMETERS ###
#################################################

# define outcome space and initial state probability
def initialize():
    outcomeSpaceLights = {
    "Lights_t": ('on','off'),
    "Lights_t-1": ('on','off'),
    }

    startLights = {
        'dom': ('Lights',), 
        'table': odict([
            (('on',), 0.5),
            (('off',), 0.5),
        ])
    }

    return outcomeSpaceLights, startLights

# room 16, reliable sensor 1
def room16():
    transitionLights = {
        'dom': ('Lights_t-1', 'Lights_t'), 
        'table': odict([
            (('on','on'), 0.9874),
            (('on','off'), 0.0126),
            (('off','on'), 0.0124),
            (('off','off'), 0.9876),        
        ])
    }

    evidenceLights = {
        'dom': ('Lights_t', 'Sensor_t'), 
        'table': odict([
            (('on','motion'), 0.984),
            (('on','no motion'), 0.016),
            (('off','motion'), 0.0265),
            (('off','no motion'), 0.9735),
        ])
    }
    return transitionLights, evidenceLights

# room 5, reliable sensor 2
def room5():
    transitionLights = {
        'dom': ('Lights_t-1', 'Lights_t'), 
        'table': odict([
            (('on','on'), 0.6163),
            (('on','off'), 0.3837),
            (('off','on'), 0.0614),
            (('off','off'), 0.9386),        
        ])
    }

    evidenceLights = {
        'dom': ('Lights_t', 'Sensor_t'), 
        'table': odict([
            (('on','motion'), 0.9577),
            (('on','no motion'), 0.0423),
            (('off','motion'), 0.0367),
            (('off','no motion'), 0.9633),
        ])
    }

    return transitionLights, evidenceLights

# room 25, reliable sensor 3
def room25():
    transitionLights = {
        'dom': ('Lights_t-1', 'Lights_t'), 
        'table': odict([
            (('on','on'), 0.8693),
            (('on','off'), 0.1307),
            (('off','on'), 0.0726),
            (('off','off'), 0.9274),        
        ])
    }

    evidenceLights = {
        'dom': ('Lights_t', 'Sensor_t'), 
        'table': odict([
            (('on','motion'), 0.9568),
            (('on','no motion'), 0.0432),
            (('off','motion'), 0.0337),
            (('off','no motion'), 0.9663),
        ])
    }

    return transitionLights, evidenceLights

# room 31, reliable sensor 4
def room31():
    transitionLights = {
        'dom': ('Lights_t-1', 'Lights_t'), 
        'table': odict([
            (('on','on'), 0.9865),
            (('on','off'), 0.0135),
            (('off','on'), 0.01323),
            (('off','off'), 0.9868),        
        ])
    }

    evidenceLights = {
        'dom': ('Lights_t', 'Sensor_t'), 
        'table': odict([
            (('on','motion'), 0.9806),
            (('on','no motion'), 0.0194),
            (('off','motion'), 0.0371),
            (('off','no motion'), 0.9629),
        ])
    }

    return transitionLights, evidenceLights

# room 1, unreliable sensor 3
def room1():
    transitionLights = {
        'dom': ('Lights_t-1', 'Lights_t'), 
        'table': odict([
            (('on','on'), 0.9434),
            (('on','off'), 0.0566),
            (('off','on'), 0.0741),
            (('off','off'), 0.9259),        
        ])
    }

    evidenceLights = {
        'dom': ('Lights_t', 'Sensor_t'), 
        'table': odict([
            (('on','motion'), 0.9515),
            (('on','no motion'), 0.0485),
            (('off','motion'), 0.1405),
            (('off','no motion'), 0.8595),
        ])
    }

    return transitionLights, evidenceLights

# room 24, unreliable sensor 4
def room24():
    transitionLights = {
        'dom': ('Lights_t-1', 'Lights_t'), 
        'table': odict([
            (('on','on'), 0.5378),
            (('on','off'), 0.4622),
            (('off','on'), 0.0281),
            (('off','off'), 0.9719),        
        ])
    }

    evidenceLights = {
        'dom': ('Lights_t', 'Sensor_t'), 
        'table': odict([
            (('on','motion'), 0.9328),
            (('on','no motion'), 0.0672),
            (('off','motion'), 0.1438),
            (('off','no motion'), 0.8562),
        ])
    }

    return transitionLights, evidenceLights

#############################
#### HIDDEN MARKOV MODEL ####
#############################

# start chain without evidence from sensors
# 8:00:00 to 8:00:15
def start_hmm():
    # get outcome space and starting probability
    outcomeSpaceLights, startLights = initialize()

    # ROOM 16
    transitionLights16, evidenceLights16 = room16()
    fCurrent16 = viterbiOnline(startLights, transitionLights16, evidenceLights16, 'Lights', 'Sensor_t', None, outcomeSpaceLights, norm=True)

    # ROOM 5
    transitionLights5, evidenceLights5 = room5()
    fCurrent5 = viterbiOnline(startLights, transitionLights5, evidenceLights5, 'Lights', 'Sensor_t', None, outcomeSpaceLights, norm=True)

    # ROOM 25
    transitionLights25, evidenceLights25 = room25()
    fCurrent25 = viterbiOnline(startLights, transitionLights25, evidenceLights25, 'Lights', 'Sensor_t', None, outcomeSpaceLights, norm=True)

    # ROOM 31
    transitionLights31, evidenceLights31 = room31()
    fCurrent31 = viterbiOnline(startLights, transitionLights31, evidenceLights31, 'Lights', 'Sensor_t', None, outcomeSpaceLights, norm=True)

    # ROOM 1
    transitionLights1, evidenceLights1 = room1()
    fCurrent1 = viterbiOnline(startLights, transitionLights1, evidenceLights1, 'Lights', 'Sensor_t', None, outcomeSpaceLights, norm=True)

    # ROOM 24
    transitionLights24, evidenceLights24 = room24()
    fCurrent24 = viterbiOnline(startLights, transitionLights24, evidenceLights24, 'Lights', 'Sensor_t', None, outcomeSpaceLights, norm=True)

    return fCurrent16, fCurrent5, fCurrent25, fCurrent31, fCurrent1, fCurrent24

# continue chain using evidence from sensors
def hmm(emissionEvi):

    # get outcome space and starting probability
    outcomeSpaceLights, startLights = initialize()

    # initial Markov chain
    fCurrent16, fCurrent5, fCurrent25, fCurrent31, fCurrent1, fCurrent24 = start_hmm()

    # ROOM 16
    transitionLights16, evidenceLights16 = room16()
    fCurrent16 = viterbiOnline(fCurrent16, transitionLights16, evidenceLights16, 'Lights', 'Sensor_t', emissionEvi['reliable_sensor1'], outcomeSpaceLights, norm=True)

    # ROOM 5
    transitionLights5, evidenceLights5 = room5()
    fCurrent5 = viterbiOnline(fCurrent5, transitionLights5, evidenceLights5, 'Lights', 'Sensor_t', emissionEvi['reliable_sensor2'], outcomeSpaceLights, norm=True)

    # ROOM 25
    transitionLights25, evidenceLights25 = room25()
    fCurrent25 = viterbiOnline(fCurrent25, transitionLights25, evidenceLights25, 'Lights', 'Sensor_t', emissionEvi['reliable_sensor3'], outcomeSpaceLights, norm=True)

    # ROOM 31
    transitionLights31, evidenceLights31 = room31()
    fCurrent31 = viterbiOnline(fCurrent31, transitionLights31, evidenceLights31, 'Lights', 'Sensor_t', emissionEvi['reliable_sensor4'], outcomeSpaceLights, norm=True)

    # ROOM 1
    transitionLights1, evidenceLights1 = room1()
    fCurrent1 = viterbiOnline(fCurrent1, transitionLights1, evidenceLights1, 'Lights', 'Sensor_t', emissionEvi['unreliable_sensor3'], outcomeSpaceLights, norm=True)

    # ROOM 24
    transitionLights24, evidenceLights24 = room24()
    fCurrent24 = viterbiOnline(fCurrent24, transitionLights24, evidenceLights24, 'Lights', 'Sensor_t', emissionEvi['unreliable_sensor4'], outcomeSpaceLights, norm=True)

    return fCurrent16, fCurrent5, fCurrent25, fCurrent31, fCurrent1, fCurrent24

# get most probable outcome from HMM
def most_probable(f):
    return max(f['table'], key=f['table'].get)[0]

# update actions_dict
def update_dict(f, room, actions_dict):
    action = most_probable(f)
    num = re.findall("\d+", room)[0]
    lights = 'lights' + num
    actions_dict[lights] = action

# update actions_dict with decisions from HMM and robot sensors
def update_hmm_actions(actions_dict, room16, room5, room25, room31, room1, room24):
    # make new copy
    new_actions = copy.deepcopy(actions_dict)
    
    # ROOM 16
    update_dict(room16, 'room16', new_actions)

    # ROOM 5
    update_dict(room5, 'room5', new_actions)

    # ROOM 25
    update_dict(room25, 'room25', new_actions)

    # ROOM 31
    update_dict(room31, 'room31', new_actions)

    # ROOM 1
    update_dict(room1, 'room1', new_actions)

    # ROOM 24
    update_dict(room24, 'room24', new_actions)

    return new_actions

