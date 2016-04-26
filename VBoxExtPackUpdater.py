#!/usr/bin/env python2

import requests
from bs4 import BeautifulSoup
from urlparse import urljoin
import hashlib
import tempfile
import subprocess
import os
import re
# from IPython import embed

# https://www.virtualbox.org/download/hashes/5.0.18/SHA256SUMS
HASH_BASE_URL = ('https://www.virtualbox.org/download/hashes/{version}/'
                 'SHA256SUMS')

# http://download.virtualbox.org/virtualbox/5.0.18/Oracle_VM_VirtualBox_Extension_Pack-5.0.18-106667.vbox-extpack
DL_BASE_URL = 'http://download.virtualbox.org/virtualbox/'


def getLatestVersion():
    r = requests.get(urljoin(DL_BASE_URL, 'LATEST.TXT'))
    return r.text.strip()


def getInstalledVersion():
    version = subprocess.check_output(['VBoxManage', '--version'])
    # needed, as some VBoxManage warnings also go to stdout
    return re.search('^(\d+\.\d+\.\d+)r\d+$', version, re.MULTILINE).group(1)


def getSHA256SUMS(version):
    r = requests.get(
        HASH_BASE_URL.format(version=version),
        allow_redirects=False
    )
    return r.text


def loadExtPack(version):
    extpack_dir = urljoin(
        DL_BASE_URL, version
    ) + '/'
    r = requests.get(extpack_dir)
    soup = BeautifulSoup(r.text, 'lxml')
    extpack_name = filter(
        lambda x: x.endswith('.vbox-extpack'),
        [x['href'] for x in soup.findAll('a')]
    )[0]
    extpack_url = urljoin(extpack_dir, extpack_name)
    r = requests.get(extpack_url)
    return {'filename': extpack_name, 'data': r.content}


def verifyExtPack(extpack, SHA256SUMS):
    ist_sha256 = hashlib.sha256(extpack['data']).hexdigest()
    regex = '^([^\s]+)[\s*]+{filename}$'.format(
        filename=re.escape(extpack['filename'])
    )
    soll_sha256 = re.match(regex, SHA256SUMS, re.MULTILINE).group(1)
    return soll_sha256 == ist_sha256


def installExtPack(extpack):
    tmp_dir = tempfile.mkdtemp()
    tmp_file = os.path.join(tmp_dir, extpack['filename'])
    with open(tmp_file, 'w+b') as f:
        f.write(extpack['data'])
#    subprocess.call(['sha256sum', tmp_file])
    subprocess.call([
        'sudo', 'VBoxManage', 'extpack', 'install', tmp_file
    ])
    os.remove(tmp_file)
    os.rmdir(tmp_dir)


def buildKernelModules():
    subprocess.call(['sudo', '/sbin/rcvboxdrv', 'setup'])


if __name__ == '__main__':
    version = getInstalledVersion()
#    version = getLatestVersion()
    SHA256SUMS = getSHA256SUMS(version)
    extpack = loadExtPack(version)
    if verifyExtPack(extpack, SHA256SUMS):
        installExtPack(extpack)
#    buildKernelModules()
