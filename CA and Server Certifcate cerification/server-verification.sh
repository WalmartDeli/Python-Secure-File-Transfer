#!/bin/bash

#modify the location where the server certificate is uploaded. 
openssl verify -CAfile ca.pem server-cert.pem