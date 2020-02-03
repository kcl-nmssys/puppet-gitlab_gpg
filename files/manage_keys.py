#!/usr/bin/python
#
# Import GPG keys into GitLab and git user's keyring
# Part of puppet-gitlab_gpg - https://github.com/kcl-nmssys/puppet-gitlab_gpg

import argparse
import gitlab
import gnupg
import os
import pwd
import re
import sys
import syslog
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('--mode')
args = parser.parse_args()
if not args.mode or args.mode not in ['check', 'update']:
    sys.stderr.write('No --mode specified - must be check or update\n')
    sys.exit(1)

try:
    with open('/etc/gitlab_gpg/config.yaml') as fh:
        config = yaml.load(fh, Loader=yaml.SafeLoader)
except:
    sys.stderr.write('Failed to load configuration file\n')
    sys.exit(1)

os.chdir(config['install_path'])

need_update = False
update_status = 0
trusted = {}
current_keys_keyring = {}
current_keys_gitlab = {}

# See what's in our keyring already
gpg = gnupg.GPG(gnupghome='%s/.gnupg' % pwd.getpwuid(os.getuid()).pw_dir)
for key in gpg.list_keys():
    current_keys_keyring[key['fingerprint']] = 1

# See what's in GitLab already
gl = gitlab.Gitlab('https://%s/' % config['gitlab_hostname'], private_token=config['gitlab_auth_token'])
users = gl.users.list()
for user in users:
    keys = user.gpgkeys.list()
    if len(keys) > 0:
        for key in keys:
            key_file = 'keys/gitlab/%s_%d.pub' % (user.username, key.id)
            with open(key_file, 'w') as fh:
                fh.write('%s\n' % key.key)

            key_data = gpg.scan_keys(key_file)[0]
            current_keys_gitlab[key_data['fingerprint']] = {'user': user.username, 'key': key.id}

# Import any trusted keys
for file in os.listdir('keys/trusted'):
    matched = re.match(r'^([a-zA-Z0-9_.-]+)\.pub$', file)
    if matched:
        username = matched.group(1)
        key_path = 'keys/trusted/%s' % file
        keys_data = gpg.scan_keys(key_path)
        for key_data in keys_data:
            trusted[key_data['fingerprint']] = 1
            if key_data['fingerprint'] not in current_keys_keyring:
                if args.mode == 'check':
                    need_update = True
                else:
                    with open(key_path) as fh:
                        import_result = gpg.import_keys(fh.read())
                    if import_result.count > 0:
                        syslog.syslog(syslog.LOG_INFO, 'Imported key [%s] [%s] into keyring' % (key_data['fingerprint'], ', '.join(key_data['uids'])))
                    else:
                        syslog.syslog(syslog.LOG_ERR, 'Failed importing key [%s] [%s] into keyring' % (key_data['fingerprint'], ', '.join(key_data['uids'])))
                        import_status = 1

            if key_data['fingerprint'] not in current_keys_gitlab:
                if args.mode == 'check':
                    need_update = True
                else:
                    user = gl.users.list(username=username)[0]
                    user.gpgkeys.create({'key': gpg.export_keys(key_data['fingerprint'])})
                    syslog.syslog(syslog.LOG_INFO, 'Imported key [%s] [%s] into GitLab' % (key_data['fingerprint'], username))

# Remove any unexpected keys from GitLab
if config['manage_gitlab_keys']:
    for fingerprint in current_keys_gitlab.keys():
        if fingerprint not in trusted:
            if args.mode == 'check':
                need_update = True
            else:
                user = gl.users.list(username=current_keys_gitlab[fingerprint][user])[0]
                user.gpgkeys.delete(current_keys_gitlab[fingerprint][key])
                syslog.syslog(syslog.LOG_INFO, 'Deleted key [%s] [%s] from GitLab' % (fingerprint, current_keys_gitlab[fingerprint][user]))

# Remove any unexpected keys from keyring
for fingerprint in current_keys_keyring:
    if fingerprint not in trusted:
        gpg.delete_keys(fingerprint)
        syslog.syslog(syslog.LOG_INFO, 'Deleted key [%s] from keyring' % (fingerprint,))

if args.mode == 'check':
    if need_update:
        sys.exit(0)
    sys.exit(1)

sys.exit(update_status)
