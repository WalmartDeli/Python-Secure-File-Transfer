# Diffie Hellman server side

import random

# D.H. parameters
g = 2           #primitive root
p = 65521       #commonly agreed prime integer

# Bob - server
# Bob picks a random exponent b between 1 and p:
# (this is Bob's private number)
b = random.randint(1, p)

# Bob computes his public number B = g^b mod p:
B = g**b % p

################Exchange alice public key################

from Client_DH import *

# Bob computes the shared secret, which is A^b (from his point of view)
shared_secret_Bobs_POV = A**b % p
#print(shared_secret_Bobs_POV)
#print("server \n")

###############Compare values###########################

if (shared_secret_Alices_POV == shared_secret_Bobs_POV):
    print("Shared secret key matched.")
else:
    print("Shared secret key did not match.")
    exit()

exit()
