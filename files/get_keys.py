#!/usr/bin/python
#
# Get users' GPG keys from GitLab and import them into our keyring
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
if not args.mode or (args.mode != 'check' and args.mode != 'import'):
    sys.stderr.write('No --mode specified - must be check or import\n')
    sys.exit(1)

os.chdir(os.path.dirname(__file__))

try:
    with open('config.yaml') as fh:
        config = yaml.load(fh, Loader=yaml.SafeLoader)
except:
    sys.stderr.write('Failed to load configuration file\n')
    sys.exit(1)

gl = gitlab.Gitlab('https://%s/' % config['gitlab_hostname'], private_token=config['gitlab_auth_token'])
users = gl.users.list()

gpg = gnupg.GPG(gnupghome='%s/.gnupg' % pwd.getpwuid(os.getuid()).pw_dir)

current_keys = {}
for key in gpg.list_keys():
    current_keys[key['fingerprint']] = 1

need_import = False
import_status = 0

# First handle keys from GitLab
for user in users:
    keys = user.gpgkeys.list()
    if len(keys) > 0:
        for key in keys:
            key_file = 'keys/gitlab/%s_%d.pub' % (user.username, key.id)
            with open(key_file, 'w') as fh:
                fh.write('%s\n' % key.key)

            key_data = gpg.scan_keys(key_file)[0]
            if key_data['fingerprint'] not in current_keys:
                if args.mode == 'check':
                    need_import = True
                else:
                    import_result = gpg.import_keys(key.key)
                    if import_result.count > 0:
                        syslog.syslog(syslog.LOG_INFO, 'Imported key for user [%s]: [%s] [%s]' % (user.username, key_data['fingerprint'], ', '.join(key_data['uids'])))
                    else:
                        syslog.syslog(syslog.LOG_ERR, 'Failed importing key for user [%s]: [%s] [%s]' % (user.username, key_data['fingerprint'], ', '.join(key_data['uids'])))
                        import_status = 1

# Now handle any extra keys specified by Puppet
for file in os.listdir('keys/extra'):
    matched = re.match(r'^.+\.pub$', file)
    if matched:
        key_path = 'keys/extra/%s' % file
        key_data = gpg.scan_keys(key_path)[0]
        if key_data['fingerprint'] not in current_keys:
            if args.mode == 'check':
                need_import = True
            else:
                with open(key_path) as fh:
                    import_result = gpg.import_keys(fh.read())
                if import_result.count > 0:
                    syslog.syslog(syslog.LOG_INFO, 'Imported extra key [%s] [%s]' % (key_data['fingerprint'], ', '.join(key_data['uids'])))
                else:
                    syslog.syslog(syslog.LOG_ERR, 'Failed importing extra key [%s] [%s]' % (key_data['fingerprint'], ', '.join(key_data['uids'])))
                    import_status = 1

if args.mode == 'check':
    if need_import:
        sys.exit(0)
    sys.exit(1)

sys.exit(import_status)
