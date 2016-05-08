#!/usr/bin/env python2

import argparse
import hashlib
import os
import re
import subprocess
import tempfile
import requests
from bs4 import BeautifulSoup

HASH_URL = 'https://www.virtualbox.org/download/hashes/{version}/SHA256SUMS'
DL_BASE_URL = 'http://download.virtualbox.org/virtualbox/{version}/'


def get_installed_version():
    version = subprocess.check_output(['VBoxManage', '--version'])
    # needed, as some/all(?) VBoxManage warnings go to stdout
    return re.search('^(\d+\.\d+\.\d+)', version, re.MULTILINE).group(1)


def get_sha256sums(version):
    r = requests.get(HASH_URL.format(version=version), allow_redirects=False)
    return r.text


def load_ext_pack(version):
    extpack_dir = DL_BASE_URL.format(version=version)
    r = requests.get(extpack_dir)
    soup = BeautifulSoup(r.text, 'html.parser')
    extpack_name = filter(
        lambda x: x.endswith('.vbox-extpack'),
        [x['href'] for x in soup.findAll('a')]
    )[0]
    extpack_url = extpack_dir + extpack_name
    r = requests.get(extpack_url)
    return {'filename': extpack_name, 'data': r.content}


def verify_ext_pack(extpack, sha256sums):
    computed_sha256 = hashlib.sha256(extpack['data']).hexdigest()
    regex = '^([^\s]+)[\s*]+{filename}$'.format(
        filename=re.escape(extpack['filename'])
    )
    good_sha256 = re.match(regex, sha256sums, re.MULTILINE).group(1)
    return computed_sha256 == good_sha256


def install_ext_pack(extpack):
    tmp_dir = tempfile.mkdtemp()
    tmp_file = os.path.join(tmp_dir, extpack['filename'])
    with open(tmp_file, 'w+b') as f:
        f.write(extpack['data'])
#    subprocess.call(['sha256sum', tmp_file])
    subprocess.call(['sudo', 'VBoxManage', 'extpack', 'install', tmp_file])
    os.remove(tmp_file)
    os.rmdir(tmp_dir)


def build_kernel_modules():
    subprocess.call(['sudo', 'rcvboxdrv', 'setup'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-kernel-modules', action="store_true")
    args = parser.parse_args()
    if args.build_kernel_modules:
        build_kernel_modules()
    version = get_installed_version()
    sha256sums = get_sha256sums(version)
    extpack = load_ext_pack(version)
    if verify_ext_pack(extpack, sha256sums):
        install_ext_pack(extpack)
