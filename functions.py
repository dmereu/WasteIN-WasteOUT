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

    logging.debug('Distance between is %s meters' % meters)

    return meters


def obj_distance(obj1, obj2):
    """
    Calculate the distance between two objects in earth surface with aversine function
    :param obj1:
    :param obj2:
    :return: float
    """
    logging.debug('Calculating distance between %s and %s ...' % (obj1.details['itemid'], obj2.details['itemid']))
    distance = aversine(obj1.details['lon'], obj1.details['lat'], obj2.details['lon'], obj2.details['lat'])
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
    logging.debug('Scaling factors %s to %s' % (factors, scaled_factors))
    return scaled_factors


def order_containers_by_distance(user, containers):
    """
    Create a list of containers, ordered by distance from specified user.
    :param user:
    :param containers: list of object container
    :return: {fraction1: [distance, cont_id], ...} ordered by distance
    """

    cont_dict = {}
    for cont_name, container in containers.items():
        distance = obj_distance(user, container)
        cont_id = container.details['itemid']
        cont_fraction = container.details['waste_fraction']
        cont_instance_name = container.details['instance_name']

        if cont_fraction in cont_dict:
            pass
        else:
            cont_dict[cont_fraction] = []

        cont_dict[cont_fraction].append([distance, cont_instance_name, cont_id])

    for fraction, c_list in cont_dict.items():
        c_list.sort()

    logging.debug('Sorted containers by distance %s' % (cont_dict))

    return cont_dict


def nearest_container(user, fraction, containers):
    """
    Extract the name of nearest container from a list of containers
    :param fraction:
    :param user:
    :param containers:
    :return: string
    """
    nearest = order_containers_by_distance(user, containers)[fraction][0][1]
    logging.debug('The nearest container to user "%s" for the fraction "%s" is "%s"' % (user, fraction, nearest))
    return nearest


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

    angular_coefficient = (th1_fact - th2_fact) / (th2_dist - th1_dist)

    if container_distance < min_distance:
        x_fact = 'Error: No containers should be nearer than nearest container'
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
    logging.debug('Production for %s is %s' % (user_type, prod_dict))
    return prod_dict


def csv_to_dict(csv_file, primary_key='itemid'):
    with open(csv_file, mode='r') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        if primary_key not in reader.fieldnames:
            logging.error('Cannot create dict from csv. Primary key "%s" not found' % primary_key)
            exit()
        dict_list = {}
        for line in reader:
            dict_list[line[primary_key]] = line
    return dict_list


def create_users(input_file, primary_key):
    logging.info('Creating User instances...')
    users_dict = {}
    users_temp_dict = csv_to_dict(input_file, primary_key)
    for itemid, attributes in users_temp_dict.items():
        username = attributes['username']
        user_type = attributes['user_type']
        dim_factor = attributes['dim_factor']
        itemid = classes.User(attributes['username'], attributes['itemid'], attributes['instance_name'], attributes['lat'], attributes['lon'],
                                attributes['user_type'], attributes['dim_factor'])
        users_dict[username] = itemid
        logging.debug('User %s (%s) created with dim_factor = %s' % (username, user_type, dim_factor))

    return users_dict


def create_containers(input_file, primary_key='itemid'):
    logging.info('Creating Container instances...')
    conts_dict = {}
    conts_temp_dict = csv_to_dict(input_file, primary_key)
    for itemid, attributes in conts_temp_dict.items():
        cont_name = attributes['instance_name']
        itemid = classes.Container(attributes['itemid'], attributes['instance_name'], attributes['lat'], attributes['lon'], attributes['parent'],
                                   attributes['waste_fraction'], attributes['con_type'], attributes['capacity'])
        conts_dict[cont_name] = itemid
        logging.debug('Container %s (%s | %s | %s | %s | %s | %s | %s) created' % (cont_name, attributes['itemid'], attributes['lat'], attributes['lon'], attributes['parent'],
                                                                                   attributes['waste_fraction'], attributes['con_type'], attributes['capacity']))
    return conts_dict
