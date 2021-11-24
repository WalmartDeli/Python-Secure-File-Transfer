# Diffie Hellman client side
import random
from Server_DH import *

# D.H. parameters
g = 2           #primitive root
p = 65521       #commonly agreed prime integer

# Alice - client
# Alice picks a random exponent a between 1 and p:
# (this is Alice's private number)
a = random.randint(1, p)
# Alice computes her public number A = g^a mod p:
A = g**a % p

##################Exchange Bob public key#################

# Alice computes the shared secret, which is B^a (from her point of view)
shared_secret_Alices_POV = B**a % p
#print(shared_secret_Alices_POV)
#print("client \n")
