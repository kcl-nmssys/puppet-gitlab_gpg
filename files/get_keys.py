#!/usr/bin/python
#
# Get users' GPG keys from GitLab and import them into our keyring
# Part of puppet-gitlab_gpg - https://github.com/kcl-nmssys/puppet-gitlab_gpg

import gitlab
import gnupg
import hashlib
import os
import sys
import yaml

my_dir = os.path.realpath(__file__)

try:
    with open('config.yaml') as fh:
        config = yaml.load(fh, Loader=yaml.SafeLoader)
except:
    sys.stderr.write('Failed to load configuration file')
    sys.exit(1)

gl = gitlab.Gitlab('https://%s/' % config['gitlab_hostname'], private_token=config['gitlab_auth_token'])
users = gl.users.list()

for user in users:
    keys = user.gpgkeys.list()
    if len(keys) > 0:
        for key in keys:
            hash = hashlib.sha256(key.key).hexdigest()
            key_file = 'keys/%s.key' % hash
            if not os.path.exists(key_file):
                with open(key_file, 'w') as fh:
                    fh.write('%s\n' % key.key)
