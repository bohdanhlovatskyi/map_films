def adjacent_states():

    with open('data/adjacent_states.csv') as f:
        data = f.readlines()
    
    adj_states = {}
    for idx, line in enumerate(data):
        line = line.rstrip().split(',')
        adj_states.setdefault(line[0], set()).add(line[1])

    return adj_states


def map_stats():

    with open('data/id_state_mapping.csv') as f:
        data = f.readlines()

    for idx, line in enumerate(data):
        line = line.rstrip().split(',')
        data[idx] = [elm.strip('"') for elm in line]


    return {line[1]: line[0]  for line in data}

def convert_dict(adj_states, map_lst):

    mapped_dict = {}
    for key in adj_states:
        mapped_dict[map_lst[key]] = {map_lst[elm] for elm in adj_states[key]}

    return mapped_dict


def get_adj_states_dict():
    adj_dict = adjacent_states()
    map_lst = map_stats()

    return convert_dict(adj_dict, map_lst)
