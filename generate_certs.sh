#!/bin/bash

openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

echo "Please start web2py like this: python web2py.py -a 'AdminPwd' -c server.crt -k server.key -i 0.0.0.0 -p 8000"
echo "Remember to access the webpage through 'HTTPS'."
