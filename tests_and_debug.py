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