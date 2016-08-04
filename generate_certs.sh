#!/bin/bash

set -e

export PUBLIC_IP=$(hostname -I | awk -F " " '{ print $1 }')
export DOMAIN=$(hostname)
export SUBJECT=/C=TW/ST=Taiwan/L=Taipei/O=Cepave/OU=Develop
export tmp=`mktemp -d`
trap "rm -rf $tmp" EXIT

openssl genrsa -out server.key 2048
openssl req -new -key server.key -out $tmp/server.csr -subj "/CN=$DOMAIN$SUBJECT"
echo subjectAltName = DNS:$(hostname).docker.owl.com,DNS:$(hostname),DNS:$(hostname -f),IP:$PUBLIC_IP,IP:127.0.0.1 > $tmp/extfile.cnf
openssl x509 -req -days 365 -in $tmp/server.csr -signkey server.key -out server.crt -extfile $tmp/extfile.cnf

echo "Please start web2py like this: python web2py.py -a 'AdminPwd' -c server.crt -k server.key -i 0.0.0.0 -p 8000"
echo "Remember to access the webpage through 'HTTPS'."
