import docker
import datetime

HOST_PATH = '/Users/crosserclaws/.docker'
HOST_FILENAME = '/host.txt'
items = []
with open(HOST_PATH + HOST_FILENAME, 'r') as f:
    for line in f:
        host, path = line.split()
        path = HOST_PATH + path[1:]
        items.append((host, path))

f = lambda path: docker.tls.TLSConfig(
        client_cert=( path + '/cert.pem', path + '/key.pem'),
        verify= path + '/ca.pem'
    )

g = lambda host: 'tcp://{}:2376'.format(host)

@auth.requires_membership('docker')
def ps():
    pss = []
    for host, path in items:
        client = docker.Client(base_url=g(host), tls=f(path))
        ps = client.containers(all=True, trunc=True)
        # Change the time format of Created
        for container in ps:
            utime = container['Created']
            container['Created'] = datetime.datetime.fromtimestamp(
                int(utime)
            ).strftime('%Y-%m-%d %H:%M:%S')
        pss.append((host, ps))

    return dict(pss=pss)