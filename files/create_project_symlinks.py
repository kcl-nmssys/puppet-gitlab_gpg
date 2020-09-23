#!/usr/bin/python
#
# Create project symlinks pointing to hashed directory structure
# Part of puppet-gitlab_gpg - https://github.com/kcl-nmssys/puppet-gitlab_gpg

import argparse
import gitlab
import hashlib
import os
import pwd
import re
import subprocess
import sys
import syslog
import yaml

def log_error(message):
    error_bin = config['error_bin']
    error_bin.append(message)
    subprocess.call(error_bin)
    syslog.syslog(syslog.LOG_ERR, message)

def die(message):
    log_error(message)
    sys.exit(1)

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

try:
    gl = gitlab.Gitlab('https://%s/' % config['gitlab_hostname'], private_token=config['gitlab_auth_token'])
    projects = gl.projects.list(all=True)
except Exception as e:
    log_error('Failed to get projects list from GitLab: %s' % (e,))
    sys.exit(1)

hashes = {}
hashes_file = '/etc/gitlab_gpg/hashes.yaml'

for project in projects:
    proj_hash = hashlib.sha256(str(project.id)).hexdigest()
    hash_path = '%s/@hashed/%s/%s/%s.git' % (config['repos_path'], proj_hash[0:2], proj_hash[2:4], proj_hash)
    proj_path = '%s/%s.git' % (config['repos_path'], project.path_with_namespace)
    hashes[proj_hash] = project.path_with_namespace.encode()

    if os.path.exists(hash_path) and not os.path.exists(proj_path):
        need_update = True

        if args.mode == 'update':
            group_path = os.path.dirname(proj_path)
            if not os.path.exists(group_path):
                try:
                    os.mkdir(group_path, 0o2750)
                    os.chown(group_path, pwd.getpwnam(config['git_user']).pw_uid, 0)
                except Exception as e:
                    log_error('Failed creating group directory %s: %s' % (group_path, e))
                    update_status += 1

            try:
                os.symlink(hash_path, proj_path)
            except Exception as e:
                log_error('Failed creating project symlink %s -> %s: %s' % (proj_path, hash_path, e))
                update_status += 1

if args.mode == 'update':
    try:
        with open(hashes_file + '.new', 'w') as fh:
            yaml.dump(hashes, fh, default_flow_style=False)
        os.rename(hashes_file + '.new', hashes_file)
    except Exception as e:
        log_error('Failed updating hashes file: %s' % (e,))
        update_status += 1

if args.mode == 'check':
    if need_update:
        sys.exit(0)

    try:
        with open(hashes_file) as fh:
            hashes_yaml = yaml.load(fh, Loader=yaml.SafeLoader)
        if hashes != hashes_yaml:
            sys.exit(0)
    except:
        sys.exit(0)

    sys.exit(1)

sys.exit(update_status)
