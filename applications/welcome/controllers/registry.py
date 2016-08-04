#!/usr/bin/env python

import sys
import yaml
import requests
from os.path import expanduser

# Init
_HOME = expanduser("~")
_configPath = _HOME + '/.docker/dockmon.yml'

def readConfig(filePath=_configPath):
  with open(filePath, 'r') as f:
    return yaml.load(f)

config = readConfig()['registry']
protocol = 'https://' if config['ssl']['isHttps'] else 'http://'
host = protocol + config['domain']
hostUrl = host + '/v2/'

# Functions
def list():
    msg = ''
    form = _getForm(_listRegistry(hostUrl))

    # Handle form
    if form.process().accepted:
        msgList = []
        formData = dict(form.vars)
        for name, flag in formData.iteritems():
            if flag:
                repo, tag = name.split(':')
                msgList.append( delManifest(hostUrl, repo, tag) )
        msg = '\n'.join(msgList)
        # Update the info
        if msg:
            form = _getForm(_listRegistry(hostUrl))
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form is invalid'
    else:
        response.flash = 'please fill the form'

    return dict(host=host, form=form, vars=form.vars, dels=msg)

def _listRegistry(hostUrl):
    repDict = {}
    repoList = _getRepos(hostUrl)
    if repoList:
        for idx, repo in enumerate(repoList):
            tagList = _getTags(hostUrl, repo)
            repDict[repo] = tagList
    return repDict

def _getForm(regDict):
    rowList = []
    rowList.append( TR(TH('IMAGE'), TH('DELETE')) )
    for repo, tagList in regDict.iteritems():
        if tagList is None:
            continue
        for tag in tagList:
            name = repo + ':' + tag
            rowList.append(TR(name, INPUT(_type='checkbox', _name=name)))
    rowList.append(TR('', INPUT(_type='submit', _value='SUBMIT')))
    form = FORM(TABLE(*rowList))
    form.add_button('Refresh', URL('list'))
    return form

def _getRepos(hostUrl):
    method = requests.get
    url = hostUrl + '_catalog'
    kw = { 'url': url }

    r = _handleRequest(200, method, **kw)
    if r is not None:
        return r.json()['repositories']
    return None

def _getTags(hostUrl, repoStr):
    method = requests.get
    url = '{}{}/tags/list'.format(hostUrl, repoStr)
    kw = { 'url': url }

    r = _handleRequest(200, method, **kw)
    if r is not None:
        return r.json()['tags']
    return None

def delManifest(hostUrl, repoStr, tagStr):
    digest = getDigest(hostUrl, repoStr, tagStr)
    if digest is None:
        return None

    method = requests.delete
    url = '{}{}/manifests/{}'.format(hostUrl, repoStr, digest)
    kw = { 'url': url }

    r = _handleRequest(202, method, **kw)
    if r is not None:
        return "[DEL][{}:{}] {}".format(repoStr, tagStr, digest)
    return None

def getDigest(hostUrl, repoStr, tagStr):
    method = requests.head
    url = '{}{}/manifests/{}'.format(hostUrl, repoStr, tagStr)
    v2Headers = { 'Accept': 'application/vnd.docker.distribution.manifest.v2+json' }
    kw = { 'url': url, 'headers': v2Headers }

    r = _handleRequest(200, method, **kw)
    if r is not None:
        return r.headers['docker-content-digest']
    return None

def _handleRequest(code, requestMethod, **kwargs):
    try:
        if config['login']['isAuth']:
            _setAuth(kwargs)
        cert = config['ssl'].get('certs', None) if config['ssl']['isHttps'] else None

        r = requestMethod(verify=cert, **kwargs)
        if r.status_code == code:
            return r
        print r.status_code, r.text
    except requests.exceptions.RequestException as e:
        print '[Request Error]', e
    return None

def _getAuth(domainName):
    return config['login']['auths'].get(domainName, {}).get('auth')

def _setAuth(kwDict):
    auth = _getAuth(config['domain'])
    if auth is None:
        print '[Error] No Auth data.'

    # Always assign the updated headers to kwargs
    authDict = { 'Authorization': ('Basic ' + auth) }
    headers = kwDict.get('headers', {})
    headers.update(authDict)
    kwDict['headers'] = headers