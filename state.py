def initial_state():
    state = {
        'outside': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r12']
        },
        'r1': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r2','r3']
        },
        'r2': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r1','r4']
        },
        'r3': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r1','r7']
        },
        'r4': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r2','r8']
        },
        'r5': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r6','r9','c3']
        },
        'r6': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r5','c3'] 
        },
        'r7': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r3','c1']
        },
        'r8': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r4','r9']
        },
        'r9': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r5','r8','r13']
        },
        'r10': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c3']
        },
        'r11': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c3']
        },
        'r12': {
            'ppl_in_room': [],
            'adjacent_rooms': ['outside','r22']
        },
        'r13': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r9','r24']
        },
        'r14': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r24']
        },
        'r15': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c3']
        },
        'r16': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c3']
        },
        'r17': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c3']
        },
        'r18': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c3']
        },
        'r19': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c3']
        },
        'r20': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c3']
        },
        'r21': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c3']
        },
        'r22': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r12','r25']
        },
        'r23': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r24']
        },
        'r24': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r13','r14','r23']
        },
        'r25': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r22','r26','c1']
        },
        'r26': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r25','r27']
        },
        'r27': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r26','r32']
        },
        'r28': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c4']
        },
        'r29': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r30','c4']
        },
        'r30': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r29']
        },
        'r31': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r32']
        },
        'r32': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r27','r31','r33']
        },
        'r33': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r32']
        },
        'r34': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c2']
        },
        'r35': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c4']
        },
        'c1': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r7','r25','c2']
        },
        'c2': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r34','c1','c4']
        },
        'c3': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r5','r6','r10','r11','r15','r16','r17','r18','r19','r20','r21','o1']
        },
        'c4': {
            'ppl_in_room': [],
            'adjacent_rooms': ['r28','r29','r35','c2','o1']
        },
        'o1': {
            'ppl_in_room': [],
            'adjacent_rooms': ['c3','c4']
        }
    }

    return state