# coding: utf-8

"""

This software benchmarks the position of waste containers in a waste management system.
Objects and methods simulate a scenario of waste containers fillment at a determined time.
The model take the User waste production and throw it in a list of containers
according to distance-driven factors.

Provided external input sources (file or DB):

1 - Standard waste production per user type (domestic, commercial, industrial, ... ):
    1.1 - Organic
    1.2 - Aluminium
    1.3 - Glass
    1.4 - Paper
    1.5 - Cooking oils
    1.6 - Textiles

2 - Users dataset containing at least:
    2.1 - User type (domestic, commercial, industrial, ... )
    2.2 - Dimension factor (square meter, units, ... )
    2.3 - Geographic coordinates

3 - Containers dataset containing at least:
    3.1 - Capacity
    3.2 -
    3.3 - Geographic coordinates

"""

import math

"""
willFactor describes the user range, needed to build the plausible container list.
It determinates the maximum distance of a plausible container.
"""
willFactor = 4.0
if willFactor < 1: exit("Error: willFactor must be greater than 1")


def aversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    with aversine methods (Formula dell'emisenoverso)
    Distance between center of the earth and one pole of 6356,988 Km (Wikipedia)
    :param lon1: Longitude of Object 1
    :param lat1: Latitude of Object 1
    :param lon2: Longitude of Object 2
    :param lat2: Latitude of Object 2
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    meters = 6356988 * c
    return meters


def obj_distance(obj1, obj2):
    """
    Calculate the distance between two objects in earth with aversine function
    :param obj1:
    :param obj2:
    :return: float
    """
    distance = aversine(obj1.details["lon"], obj1.details["lat"], obj2.details["lon"], obj2.details["lat"])
    return distance


def scale_to_1(factors):
    """
    Scale a list components to sum 1
    :param factors: list of numbers
    :return: list of input numbers scaled as they sum 1
    """
    total = sum(factors)
    scaled_factors = []
    for factor in factors:
        scaled_factors.append(float(factor)/total)
    return scaled_factors


def order_containers_by_distance(user, containers):
    """
    Create a list of containers, ordered by distance from specified user.
    :param user:
    :param containers: list of object container
    :return: [distance, cont_id] ordered by distance
    """
    av_cont = []
    for container in containers:
        distance = obj_distance(user, container)
        cont_id = container.details["itemid"]
        av_cont.append([distance, cont_id])
    av_cont.sort()
    return av_cont


def nearest_container(user, containers):
    """
    Extract the id of nearest container from a list of containers
    :param user:
    :param containers:
    :return: string
    """
    return order_containers_by_distance(user, containers)[0][1]


def plausible_containers(user, containers):
    """
    Take the list of containers and choose the ones in "will" parameter range.
    :param user: User object
    :param containers: Container object unordered list
    :return: list of plausible containers [distance, cont_id] ordered by distance
    """

    sorted_containers = order_containers_by_distance(user, containers)

    the_nearest_container = sorted_containers[0]
    min_distance = the_nearest_container[0]
    max_distance = min_distance * willFactor

    plausible_containers_list = []
    for container in sorted_containers:
        if container[0] < max_distance:
            plausible_containers_list.append(container)
        else:
            break
    return plausible_containers_list


def throw_factor(min_distance, container_distance):
    """
    Calculate the throw factor using a polygonal chain function, as interpolation of spline
    :param min_distance: float - distance between user and the nearest container
    :param container_distance: float - distance between user and container of the desired throw factor
    :return: float
    """
    max_distance = min_distance * willFactor

    # thresold definition
    th1_dist = min_distance * (1 + (willFactor - 1) * 0.1)
    th1_fact = 1.00
    th2_dist = min_distance * (1 + (willFactor - 1) * 0.5)
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


class User(object):
    def __init__(self, itemid, lat, lon, user_type, dim_factor, available_containers):
        self.details = {
            "itemid": itemid,
            "lat": lat,
            "lon": lon,
            "user_type": user_type,
            "dim_factor": dim_factor,
            "available_containers": available_containers  # [[distance, cont_id, factor], ... ]
        }

    def production(self):
        """
        It represent the waste production for a time-cycle (i.e. 1 week).
        Depending of the user type, wasteProd variable is valorized with a list of values.
        This list represent Organic, Aluminum, Paper, Glass, Textiles, Cooking Oils quantity.
        Factor represent the scale of production. In a family it can be assumed to be the people in a family.
        :return: dict -
        """

        # unit_std_production will be imported as external source by file or DB
        unit_std_production = {
            # "userTypeName": [Organic, Aluminium, Paper, Glass, Textiles, Cooking Oils]
            "domestic": [1, 0.2, 0.4, 0.7, 0.1, 0.15],  # Each person in a family
            "restaurant": [10, 3, 8, 15, 1, 10]  # Every 50 m2 of restaurant commercial surface
        }

        user_type = self.details["user_type"]
        user_factor = self.details["dim_factor"]

        if user_type in unit_std_production:  # Check if user type exists in standard production list
            user_std_production = unit_std_production[user_type]  # Apply standard production

            #  Apply user factor to standard productions
            count = 0
            while count < len(user_std_production):
                user_std_production[count] = user_factor * user_std_production[count]
                count += 1

        else:
            return "There are no specified waste production for \"%s\" production" % user_type

        # Generate the production dictionary
        production_quantity = {
            "organic": user_std_production[0],
            "aluminium": user_std_production[1],
            "paper": user_std_production[2],
            "glass": user_std_production[3],
            "textiles": user_std_production[4],
            "oils": user_std_production[5]
        }

        return production_quantity

    def update_available_containers(self, containers):
        available_containers_list = []
        plausible_containers_list = plausible_containers(self, containers)
        min_distance = plausible_containers_list[0][0]

        throw_factor_sum = 0
        for container in plausible_containers_list:
            container_throw_factor = throw_factor(min_distance, container[0])
            available_containers_list.append([container[0], container[1], container_throw_factor])
            throw_factor_sum += container_throw_factor

        i = 0
        while i < len(available_containers_list):
            available_containers_list[i][2] = available_containers_list[i][2]/throw_factor_sum
            i += 1

        self.details["available_containers"] = available_containers_list


class Island(object):
    def __init__(self, itemid, lat, lon, parent):
        self.details = {
            "itemid": itemid,
            "lat": lat,
            "lon": lon,
            "parent_zone": parent  # Parent zone or neighborhood
        }


class Container(object):
    def __init__(self, itemid, lat, lon, parent, con_type, capacity, waste):
        self.details = {
            "itemid": itemid,
            "lat": lat,
            "lon": lon,
            "parent_island": parent,  # ItemID of parent Island
            "typeOfContainer": con_type,  # Type of container (may be a code)
            "capacity": capacity,  # Container's net capacity, in cubic meters
            "wasteInside": waste  # Container's filling status, in cubic meters
        }

    def add_waste(self, waste):
        self.details["wasteInside"] += waste
        print "Adding %s mc to \"%s\" container" % (waste, self.details["id"])

    def get_details(self):
        print self.details

    def get_filling(self):
        print "The container \"%s\" contains %s mc" % (self.details["id"], self.details["wasteInside"])


utente1 = User("Corrales.C08", 37.27696237, -6.99043453, "domestic", 1, [])
utente2 = User("Corrales.C11", 37.27782446, -6.99183455, "domestic", 2, [])

contenitore1 = Container("CS.20", 37.27562032, -6.99183339, "isola", "campana", 3.00, 0.00)
contenitore2 = Container("CS.21", 37.27688321, -6.99208453, "isola", "campana", 3.00, 0.00)
contenitore3 = Container("CS.22", 37.27528418, -6.99333553, "isola", "campana", 3.00, 0.00)

contenitori = [contenitore1, contenitore2, contenitore3]

# contenitore1.get_filling()  # Stampa la quantità contenuta
# contenitore1.add_waste(0.3)  # Aggiunge 0.35 mc al contenuto
# contenitore1.get_filling()  # Stampa la quantita' contenuta aggiornata

# print "Distanza Utente1 - Contenitore3: %.2f metri" % obj_distance(utente1, contenitore3)

print "Il contenitore più vicino a utente1 è", nearest_container(utente1, contenitori)

print "Contenitori ordinati per distanza crescente:", order_containers_by_distance(utente1, contenitori)

print "Contenitori plausibili:", plausible_containers(utente1, contenitori)

print "Produzione utente1:", utente1.production()

print "Produzione utente2:", utente2.production()

# print probability_factor(utente1, contenitore2, contenitore3)

# av_cont = [[10, "dist10", 10], [20, "dist20", 20], [5, "dist5", 5]]
#
# print av_cont
#
# av_cont.sort()
#
# print av_cont

print utente1.details["available_containers"]
utente1.update_available_containers(contenitori)
print utente1.details["available_containers"]
