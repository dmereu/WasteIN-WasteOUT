# coding: utf-8

from functions import *
import logging
# import settings


class User(object):
    def __init__(self, username, itemid, instance_name, lat, lon, user_type, dim_factor):
        self.details = {
            'username': username,
            'itemid': itemid,
            'instance_name': instance_name,
            'lat': lat,
            'lon': lon,
            'user_type': user_type,
            'dim_factor': dim_factor,
            'waste_production': get_waste_production(user_type),
            'available_containers': []

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

        user_type = self.details['user_type']
        user_factor = self.details['dim_factor']

        if user_type in unit_standard_production:  # Check if user type exists in standard production list
            user_std_production = unit_standard_production[user_type]  # Apply standard production

            #  Apply user factor to standard productions
            count = 0
            while count < len(user_std_production):
                user_std_production[count] = user_factor * user_std_production[count]
                count += 1

        else:
            return 'There are no specified waste production for "%s" production' % user_type


    def update_available_containers(self, containers):

        logging.info('Updating available containers for user "%s" ...' % self.details['username'])

        available_containers_dict = {}
        plausible_containers_dict = plausible_containers(self, containers)

        logging.info('Resuming plausible containers ...')

        for fraction, conts_list in plausible_containers_dict.items():

            logging.debug('User "%s" for fraction %s has %s plausible containers: %s' %
                          (self.details['username'], fraction, len(conts_list), conts_list))

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

        self.details['available_containers'] = available_containers_dict

    def throw_garbage(self, conts):
        logging.info('Throwing garbage ...')
        for fraction, cont_list in self.details['available_containers'].items():
            quantity_thrown = self.details['waste_production'][fraction]
            logging.debug('User %s has produced %s %s of %s' %
                          (self.details['username'], quantity_thrown, settings.std_prod_unit, fraction))
            for cont in cont_list:
                quantity_factor = cont[2]
                destination_container = cont[1]
                conts[destination_container].add_waste(quantity_thrown*quantity_factor)
                logging.debug('%s thrown %s %s to %s' %
                             (self.details['username'], settings.std_prod_unit,
                              quantity_factor*quantity_thrown, destination_container))


class Container(object):
    def __init__(self, itemid, instance_name, lat, lon, parent, waste_fraction, con_type, capacity):
        self.details = {
            'itemid': itemid,  # Unique identification code
            'instance_name': instance_name,
            'lat': lat,
            'lon': lon,
            'parent_island': parent,  # ItemID of parent Island
            'waste_fraction': waste_fraction,  # Type of container (may be a code)
            'typeOfContainer': con_type,  # Type of container (may be a code)
            'capacity': capacity,  # Container's net capacity, in the defined standard unit
            'wasteInside': 0.00  # Container's filling status, in the defined standard unit
        }

    def add_waste(self, how_much):
        self.details['wasteInside'] += how_much
        logging.debug('Adding %s %s to "%s" container' % (how_much, settings.std_prod_unit, self.details['itemid']))

    def get_details(self):
        print(self.details)

    def get_filling(self):
        logging.info('The container "%s" (%s) now contains %s %s' %
                     (self.details['instance_name'], self.details['itemid'],
                      self.details['wasteInside'], settings.std_prod_unit))


class Island(object):
    def __init__(self, itemid, lat, lon, parent):
        self.details = {
            'itemid': itemid,
            'lat': lat,
            'lon': lon,
            'parent_zone': parent  # Parent zone or neighborhood
        }