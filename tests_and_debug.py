# coding: utf-8

from classes import *
from pprint import pprint
import time
import logging

start_time = time.time()

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

def run_model():
    logging.info('Model Started.')
    users = create_users("users.csv")
    conts = create_containers("containers.csv")

    # users[0].update_available_containers(conts)
    pprint(csv_to_dict("containers.csv"))
    print()


    # logging.debug(pprint(users[0].details))
    # users[0].throw_garbage()
    # conts["cont1"].add_waste(0.1)
    # print(conts[0].details['wasteInside'])


    # for sel_user in users:
    #     sel_user.update_available_containers(conts)
    #     sel_user.throw_garbage()
    #     print(sel_user.details["instance_name"], "processed.")


run_model()

print("--- %s milliseconds ---" % (round((1000 * (time.time() - start_time)), 5)))
