# coding: utf-8

import math, csv, classes, settings, logging


def aversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    with aversine methods (Formula dell'emisenoverso)
    Distance between center of the earth and one pole of 6356,988 Km
    :param lon1: Longitude of Object 1
    :param lat1: Latitude of Object 1
    :param lon2: Longitude of Object 2
    :param lat2: Latitude of Object 2
    """

    lon1 = float(lon1)
    lon2 = float(lon2)
    lat1 = float(lat1)
    lat2 = float(lat2)

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    meters = 6356988 * c
    return meters


def obj_distance(obj1, obj2):
    """
    Calculate the distance between two objects in earth surface with aversine function
    :param obj1:
    :param obj2:
    :return: float
    """
    distance = aversine(obj1.details["lon"], obj1.details["lat"], obj2.details["lon"], obj2.details["lat"])

    return distance


def scale_to_1(factors):
    """
    Scale a list components as they results to sum 1 (or rather 100%).
    Useful to calculate the waste subdivision factors.
    :param factors: list of numbers
    :return: list of input numbers scaled as they sum 1
    """
    total = sum(factors)
    scaled_factors = []
    for factor in factors:
        scaled_factors.append(float(factor) / total)
    return scaled_factors


def order_containers_by_distance(user, containers):
    """
    Create a list of containers, ordered by distance from specified user.
    :param user:
    :param containers: list of object container
    :return: {fraction1: [distance, cont_id], ...} ordered by distance
    """
    cont_list = {}
    for container in containers:
        distance = obj_distance(user, container)
        cont_id = container.details["itemid"]
        cont_fraction = container.details["waste_fraction"]
        cont_instance_name = container.details["instance_name"]

        if cont_fraction in cont_list:
            pass
        else:
            cont_list[cont_fraction] = []

        cont_list[cont_fraction].append([distance, cont_instance_name, cont_id])

    for fraction, c_list in cont_list.items():
        c_list.sort()

    return cont_list


def nearest_container(user, fraction, containers):
    """
    Extract the name of nearest container from a list of containers
    :param fraction:
    :param user:
    :param containers:
    :return: string
    """
    return order_containers_by_distance(user, containers)[fraction][0][1]


def plausible_containers(user, containers):
    """
    Take the list of containers and choose the ones in "will" parameter range.
    :param user: User object
    :param containers: Container object unordered list
    :return: dict of plausible containers {fraction: [distance, cont_id], ...} ordered by distance
    """

    sorted_containers = order_containers_by_distance(user, containers)

    plausible_containers_dict = {}

    for fraction, cont_list in sorted_containers.items():
        nearest_cont = cont_list[0]
        min_distance = nearest_cont[0]
        max_distance = min_distance * settings.willFactor

        # print "maximum distance:", max_distance

        if fraction in plausible_containers_dict:
            pass
        else:
            plausible_containers_dict[fraction] = []

        for cont in cont_list:
            if cont[0] < max_distance:
                plausible_containers_dict[fraction].append(cont)
            else:
                break
    return plausible_containers_dict


def throw_factor(min_distance, container_distance):
    """
    Calculate the throw factor using a polygonal chain function, as interpolation of spline
    :param min_distance: float - distance between user and the nearest container
    :param container_distance: float - distance between user and container of the desired throw factor
    :return: float
    """
    max_distance = min_distance * settings.willFactor

    # thresold definition
    th1_dist = min_distance * (1 + (settings.willFactor - 1) * 0.05)
    th1_fact = 1.00
    th2_dist = min_distance * (1 + (settings.willFactor - 1) * 0.8)
    th2_fact = 0.25

    # print "th1 =", int(th1_dist)
    # print "th2 =", int(th2_dist)

    angular_coefficient = (th1_fact - th2_fact) / (th2_dist - th1_dist)

    if container_distance < min_distance:
        x_fact = "Error: No containers shouls be nearer than nearest container"
    elif container_distance < th1_dist:
        x_fact = th1_fact
    elif container_distance < th2_dist:
        x_fact = th1_fact - (container_distance - th1_dist) * angular_coefficient
    elif container_distance < max_distance:
        x_fact = th2_fact
    else:
        x_fact = 0

    return x_fact


def dumpclean(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print(k)
                dumpclean(v)
            else:
                print('%s : %s' % (k, v))
    elif type(obj) == list:
        print(obj)


def get_waste_production(user_type):
    prod_dict = {}
    i = 0
    while i < len(settings.fractions):
        prod_dict[settings.fractions[i]] = settings.standard_production[user_type][i]
        i += 1
    logging.debug("Production for %s is %s" % (user_type, prod_dict))
    return prod_dict


def csv_to_dict_2(csv_file):
    with open(csv_file, mode='r') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        dict_list = {}
        for line in reader:
            dict_list[line['itemid']] = line
    return dict_list


def csv_to_dict(csv_file):
    with open(csv_file, mode='r') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        dict_list = []
        for line in reader:
            dict_list.append(line)
    return dict_list


def create_users(inputFile):
    logging.info('Creating User instances...')
    users_list = []
    users_dict = csv_to_dict(inputFile)
    for user in users_dict:
        username = user['username']
        user_type = user['user_type']
        user['itemid'] = classes.User(user['username'], user['itemid'], user['instance_name'], user['lat'], user['lon'],
                                        user['user_type'], user['dim_factor'])
        users_list.append(user['username'])
        logging.debug('User %s (%s) created' % (username, user_type))


    # http://stackoverflow.com/questions/348196/creating-a-list-of-objects-in-python
    # for count in xrange(4):
    #     x = SimpleClass()
    #     x.attr = count
    #     simplelist.append(x)
    #
    # simplelist = [SimpleClass(count) for count in xrange(4)]

    return users_list


def create_containers(inputFile):
    logging.info('Creating Container instances...')
    conts_list = []
    conts_dict = csv_to_dict(inputFile)
    for cont in conts_dict:
        cont_name = cont['instance_name']
        cont['instance_name'] = classes.Container(cont['itemid'], cont['instance_name'], cont['lat'], cont['lon'], cont['parent'],
                                   cont['waste_fraction'], cont['con_type'], cont['capacity'])
        conts_list.append(cont['instance_name'])
        logging.debug('Container %s (%s - %s - %s - %s - %s - %s - %s - %s) created' % (cont_name, cont['itemid'], cont_name, cont['lat'], cont['lon'], cont['parent'],
                                   cont['waste_fraction'], cont['con_type'], cont['capacity']))
    return conts_list
