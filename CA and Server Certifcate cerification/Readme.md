# Certificate Creation #

## Creating a Certificate Authority Private Key and Certificate ##

To start, generate a private key for the CA using the openssl genrsa command:
- openssl genrsa 2048 > ca-key.pem
After that, you can use the private key to generate the X509 certificate for the CA using the *openssl req* command
- openssl req -new -x509 -nodes -days 365000 -key ca-key.pem -out ca.pem
The above commands create two files in the working directory: The ca-key.pem private key and the ca.pem X509 certificate are both are used by the CA to create self-signed X509 certificates below

## Creating a Private Key and a Self-signed Certificate ##

To start, generate a private key and create a certificate request using the *openssl req* command
- openssl req -newkey rsa:2048 -days 365000 -nodes -keyout server-key.pem -out server-req.pem
After that, process the key to remove the passphrase using the *openssl rsa* command
- openssl rsa -in server-key.pem -out server-key.pem
Lastly, using the certificate request and the CA's private key and X509 certificate, you can generate a self-signed X509 certificate from the certificate request using the openssl x509 command.
- openssl x509 -req -in server-req.pem -days 365000 -CA ca.pem -CAkey ca-key.pem -set_serial 01 -out server-cert.pem

## Certificate Verification ##

Once you have created the CA's X509 certificate and a self-signed X509 certificate, you can verify that the X509 certificate was correctly generated using the *openssl verify* command.
- openssl verify -CAfile ca.pem server-cert.pem
