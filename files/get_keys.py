#!/usr/bin/python
#
# Get users' GPG keys from GitLab and import them into our keyring
# Part of puppet-gitlab_gpg - https://github.com/kcl-nmssys/puppet-gitlab_gpg

import gitlab
import gnupg
import os
import pwd
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

gpg = gnupg.GPG(gnupghome='%s/.gnupg' % pwd.getpwuid(os.getuid()).pw_dir)

current_keys = {}
for key in gpg.list_keys():
    current_keys[key['fingerprint']] = 1

for user in users:
    keys = user.gpgkeys.list()
    if len(keys) > 0:
        for key in keys:
            key_file = 'keys/%s_%d.key' % (user.username, key.id)
            with open(key_file, 'w') as fh:
                fh.write('%s\n' % key.key)

            key_data = gpg.scan_keys(key_file)
            if key_data[0]['fingerprint'] not in current_keys:
                import_result = gpg.import_keys(key.key)
                print('Imported key %s for user %s' % (import_result.fingerprints[0], user.username))
