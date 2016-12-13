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

from classes import *
import time
import logging

start_time = time.time()

logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def run_model():
    logging.info('Model Started.')

    users = create_users(settings.users_file_name, settings.users_file_prkey)
    conts = create_containers(settings.containers_file_name, settings.containers_file_prkey)

    for key, sel_user in users.items():
        logging.info('Processing user "%s" (%s)...' % (sel_user.details['instance_name'], sel_user.details['username']))
        sel_user.update_available_containers(conts)
        sel_user.throw_garbage(conts)
        logging.info('User "%s" (%s) fully processed' % (sel_user.details['instance_name'], sel_user.details['username']))

        logging.debug('*** Checking containers fillment ...')
        for key, cont in conts.items():
            cont.get_filling()


run_model()

logging.info('--- Total elaboration time: %s milliseconds ---' % round((1000 * (time.time() - start_time)), 5))


