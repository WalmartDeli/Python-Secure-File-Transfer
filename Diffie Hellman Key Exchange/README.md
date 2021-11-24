# Diffie Hellman Key Exchange Algorithm #

Diffie–Hellman key exchange establishes a shared secret between two parties that can be used for secret communication for exchanging data over a public network.

The simplest and the original implementation of the protocol uses the multiplicative group of integers modulo p, where p is prime, and g is a primitive root modulo p. These two values are chosen in this way to ensure that the resulting shared secret can take on any value from 1 to p–1. 

Alice and Bob publicly agree to use a modulus p = 23 and base g = 5 (which is a primitive root modulo 23).
Alice chooses a secret integer a = 4, then sends Bob A = g^a mod p
A = 5^4 mod 23 = 4
Bob chooses a secret integer b = 3, then sends Alice B = g^b mod p
B = 5^3 mod 23 = 10
Alice computes s = B^a mod p
s = 10^4 mod 23 = 18
Bob computes s = A^b mod p
s = 4^3 mod 23 = 18
Alice and Bob now share a secret (the number 18).

**Note: Run only the client.py code 
