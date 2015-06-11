import csv
import multiprocessing as mp
from random import choice

output = mp.Queue()

def get_avg_count_in_groups(groups, field_name):
    count_in_groups = []
    for g_i in groups:
        g = groups[g_i]
        teams = []
        for m in g:
            if m[field_name] not in teams:
                teams.append(m[field_name])
            count_in_groups.append(len(teams))
    return sum(count_in_groups)/float(len(count_in_groups))

def rate_team_split(groups):
    ideal = 9.0
    avg = get_avg_count_in_groups(groups, 'team')
    return avg/ideal

def rate_location_split(groups):
    ideal = 4.0
    avg = get_avg_count_in_groups(groups, 'location')
    return avg/ideal

def rate_gender_split(groups):
    ideal = 2.0
    avg = get_avg_count_in_groups(groups, 'gender')
    return avg/ideal

def rate_groups(groups):
    team_split = rate_team_split(groups)
    location_split = rate_location_split(groups)
    gender_split = rate_gender_split(groups)
    return (team_split + location_split + gender_split) / 3.0

def get_managers():
    header = []
    managers = []

    with open('managers.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        header = reader.next()
        for row in reader:
            managers.append({'name': row[0].strip(), 'gender': row[2], 'tenure': int(row[3]), 'location': row[5], 'team': row[4], 'level': row[1]})
    return managers


def gen_groups(managers):
    groups = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
    tenures = {0: [], 1: [], 2: [], 3: []}
    in_groups = []

    # First things first, let's have an exec per team (but let's consider Guy a RSM, not an exec)
    execs = [x for x in managers if x['team'] == 'Executive' and 'Zerega' not in x['name']]
    for x in execs:
        managers.remove(x)
    
    group_index = 0
    while len(execs) != 0:
        if group_index > 8:
            group_index = 0
        m = choice(execs)
        groups[group_index].append(m)
        in_groups.append(m['name'])
        execs.remove(m)
        group_index += 1

    # Next, let's put the regional sales managers (and Guy) in distinct groups
    rsms = [x for x in managers if x['team'] == 'Careers Sales' and (x['level'] == 'director' or x['level'] == 'manager') and 'Korneel' not in x['name']]
    rsms += [x for x in managers if 'Zerega' in x['name']]
    for x in rsms:
        managers.remove(x)
    
    group_index = 0    
    while len(rsms) != 0:
        if group_index > 8:
            group_index = 0
        m = choice(rsms)
        groups[group_index].append(m)
        in_groups.append(m['name'])
        rsms.remove(m)
        group_index += 1
        
    # Then let's put the engineering managers (and David) in distinct groups
    eng_mgs = [x for x in managers if x['team'] == 'Engineering' and (x['level'] == 'VP' or x['level'] == 'manager')]
    for x in eng_mgs:
        managers.remove(x)
    
    group_index = 0
    while len(eng_mgs) != 0:
        if group_index > 8:
            group_index = 0
        m = choice(eng_mgs)
        groups[group_index].append(m)
        in_groups.append(m['name'])
        eng_mgs.remove(m)
        group_index += 1

    # Since tenure is our biggest pain factor, let's distribute by tenure evenly going one at a time    
    for m in managers:
        tenures[m['tenure']].append(m)

    for group_index in range(len(groups)):
        for tenure_index in range(len(tenures)):
            if len(tenures[tenure_index]) == 0:
                continue
            m = choice(tenures[tenure_index])
            groups[group_index].append(m)
            in_groups.append(m['name'])
            tenures[tenure_index].remove(m)
    
    # Then for everyone left over, randomly put them in a group.
    not_in_groups = []
    for m in managers:
        if m['name'] not in in_groups:
            not_in_groups.append(m)

    # We would prefer 4 groups of 6 and 5 groups of 7 (59 total managers)
    num_with_six = 0
    num_with_seven = 0 
    groups_available = range(len(groups))
    while len(not_in_groups) > 0:
        group_index = choice(groups_available)
        while len(groups[group_index]) > 6:
            group_index = choice(groups_available)
        m = choice(not_in_groups)
        groups[group_index].append(m)
        not_in_groups.remove(m)
        if len(groups[group_index]) == 6 and num_with_six != 4:
            groups_available.remove(group_index)
            num_with_six += 1
        if len(groups[group_index]) == 7 and num_with_seven != 5:
            groups_available.remove(group_index)
            num_with_seven += 1

    return groups


def gen_and_get_best():
    ITERATION_COUNT = 250000

    best_rating_so_far = 0
    best_groups_so_far = None

    for i in range(ITERATION_COUNT):
        managers = get_managers()
        groups = gen_groups(managers)
        rating = rate_groups(groups)
        if rating > best_rating_so_far:
            best_rating_so_far = rating
            best_groups_so_far = groups
    
    output.put((best_rating_so_far, best_groups_so_far))
    return best_groups_so_far

if __name__ == "__main__":
    processes = [mp.Process(target=gen_and_get_best) for x in range(mp.cpu_count())]

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    results = [output.get() for p in processes]

    best_rating_so_far = 0
    best = ()
    for r in results:
        if r[0] > best_rating_so_far:
            best = r

    for i in range(len(best[1])):
        print [x['name'] for x in best[1][i]]

    print best[0]