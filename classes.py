# coding: utf-8

"""
This software benchmarks the position of waste containers in a waste management system.
Objects and methods simulate a scenario of waste containers fillment at a determined time.
The model take the User waste production and throw it in a list of containers generated
according to distance-function that determinates throw-factor.

Provided external input sources (file or DB):

1 - Standard (mean) waste production for each user type (domestic, commercial, ... ) in a standard time (e.g. 1 week):
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
    3.2 - Fraction collected
    3.3 - Geographic coordinates

"""

from functions import *
import logging
import settings # NON FUNZIONA!??


"""
willFactor describes the user action-range, useful to build the plausible container list.
It determinates the maximum distance of a plausible container.
"""
willFactor = 4.0
if willFactor < 1:
    exit("Error: willFactor must be greater than 1")

"""
SETTINGS:
Define the fractions' labels
Then, the production of usertypes, in cubic meters per week [mc/week].
"""

fractions = ['organic', 'aluminum', 'paper', 'glass', 'textiles', 'coocking_oil']

unit_std_production = {
    # "userTypeName": [Organic, Aluminium, Paper, Glass, Textiles, Cooking Oils]
    "domestic": [1, 0.2, 0.4, 0.7, 0.1, 0.15],  # Each person in a family
    "restaurant": [10, 3, 8, 15, 1, 10]  # Every 50 m2 of restaurant commercial surface
}


class User(object):
    def __init__(self, username, itemid, instance_name, lat, lon, user_type, dim_factor):
        self.details = {
            "username": username,
            "itemid": itemid,
            "instance_name": instance_name,
            "lat": lat,
            "lon": lon,
            "user_type": user_type,
            "dim_factor": dim_factor,
            "waste_production": get_waste_production(user_type),
            "available_containers": []

            # available_containers = {
            #     waste_fraction: [[distance, cont_id, factor], ... ],
            #     ...
            # }
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
        unit_standard_production = settings.standard_production['user_type']

        user_type = self.details["user_type"]
        user_factor = self.details["dim_factor"]

        if user_type in unit_standard_production:  # Check if user type exists in standard production list
            user_std_production = unit_standard_production[user_type]  # Apply standard production

            #  Apply user factor to standard productions
            count = 0
            while count < len(user_std_production):
                user_std_production[count] = user_factor * user_std_production[count]
                count += 1

        else:
            return "There are no specified waste production for \"%s\" production" % user_type

        # Generate the production dictionary
        # production_quantity = {
        #     "organic": user_std_production[0],
        #     "aluminium": user_std_production[1],
        #     "paper": user_std_production[2],
        #     "glass": user_std_production[3],
        #     "textiles": user_std_production[4],
        #     "oils": user_std_production[5]
        # }
        #
        # return production_quantity

    def update_available_containers(self, containers):
        available_containers_dict = {}
        plausible_containers_dict = plausible_containers(self, containers)

        for fraction, conts_list in plausible_containers_dict.items():
            min_distance = conts_list[0][0]
            throw_factor_sum = 0

            if fraction in available_containers_dict:
                pass
            else:
                available_containers_dict[fraction] = []

            for cont in conts_list:
                cont_throw_factor = throw_factor(min_distance, cont[0])
                available_containers_dict[fraction].append([cont[0], cont[1], cont_throw_factor])
                throw_factor_sum += cont_throw_factor

            i = 0
            while i < len(available_containers_dict[fraction]):
                available_containers_dict[fraction][i][2] = available_containers_dict[fraction][i][2]/throw_factor_sum
                i += 1

        self.details["available_containers"] = available_containers_dict

    def throw_garbage(self):
        # logging.debug("Available containers: %s" % self.details["available_containers"])
        for fraction, cont_list in self.details["available_containers"].items():
            logging.debug("fraction: %s", fraction)
            logging.debug("cont_list: %s", cont_list)
            for cont in cont_list:
                logging.debug("cont: %s", cont)
                logging.debug("User Waste Production: %s", self.details["waste_production"])
                quantity_thrown = self.details["waste_production"][fraction]
                quantity_factor = cont[2]
                destination_container = cont[1]

                eval(destination_container).add_waste(quantity_thrown*quantity_factor)


class Container(object):
    def __init__(self, itemid, instance_name, lat, lon, parent, waste_fraction, con_type, capacity):
        self.details = {
            "itemid": itemid,  # Unique identification code
            "instance_name": instance_name,
            "lat": lat,
            "lon": lon,
            "parent_island": parent,  # ItemID of parent Island
            "waste_fraction": waste_fraction,  # Type of container (may be a code)
            "typeOfContainer": con_type,  # Type of container (may be a code)
            "capacity": capacity,  # Container's net capacity, in cubic meters
            "wasteInside": 0.00  # Container's filling status, in cubic meters
        }

    def add_waste(self, how_much):
        self.details["wasteInside"] += how_much
        print("Adding %s mc to \"%s\" container" % (how_much, self.details["itemid"]))

    def get_details(self):
        print(self.details)

    def get_filling(self):
        print("The container \"%s\" now contains %s mc" % (self.details["itemid"], self.details["wasteInside"]))


class Island(object):
    def __init__(self, itemid, lat, lon, parent):
        self.details = {
            "itemid": itemid,
            "lat": lat,
            "lon": lon,
            "parent_zone": parent  # Parent zone or neighborhood
        }
