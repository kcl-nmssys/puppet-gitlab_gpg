#!/usr/bin/python
#
# Setup custom_hooks directory and symlink for all projects within a group
# Part of puppet-gitlab_gpg - https://github.com/kcl-nmssys/puppet-gitlab_gpg

import argparse
import os
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--mode')
parser.add_argument('--group')
parser.add_argument('--ensure')
args = parser.parse_args()
if not args.mode or args.mode not in ['check', 'update']:
    sys.stderr.write('Invalid --mode specified - must be check or update\n')
    sys.exit(1)
if not args.group or not re.match(r'^([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])$', args.group):
    sys.stderr.write('Invalid --group option\n')
    sys.exit(1)
if not args.ensure or args.ensure not in ['absent', 'present']:
    sys.stderr.write('Invalid --ensure specified - must be absent or present\n')
    sys.exit(1)

try:
    with open('/etc/gitlab_gpg/config.yaml') as fh:
        config = yaml.load(fh, Loader=yaml.SafeLoader)
except:
    sys.stderr.write('Failed to load configuration file\n')
    sys.exit(1)

hook_link_src = '%/force_sign.py' % (config['install_path'],)

group_dir = '%s/%s' % (config['repos_path'], args.group)
if not os.path.exists(group_dir):
    sys.stderr.write('Cannot locate group directory\n')
    sys.exit(1)

need_update = 0
with os.scandir(group_dir) as dh_g:
    for entry in dh_g:
        if re.match(r'^([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])\.git$', entry.name) and not re.match(r'^([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])\.wiki\.git$', entry.name):
            hook_dir = '%s/custom_hooks' % (group_dir,)
            hook_link = '%s/update' % (hook_dir,)

            if args.ensure == 'present':
                if os.path.isdir(hook_dir):
                    if not (os.path.islink(hook_link) and os.readlink(hook_link == hook_link_src)):
                        need_update += 1
                        if args.mode == 'update':
                            if os.path.exists(hook_link):
                                try:
                                    os.unlink(hook_link)
                                except Exception as e:
                                    sys.stderr.write('Failed deleting incorrect custom_hooks entity %s: %s\n' % (hook_link, e))
                                    sys.exit(1)
                            try:
                                os.symlink(hook_link_src, hook_link)
                            except Exception as e:
                                sys.stderr.write('Failed creating symlink %s: %s\n' % (hook_link, e))
                                sys.exit(1)

                else:
                    need_update += 1
                    if args.mode == 'update':
                        try:
                            os.mkdir(hook_dir, 0755)
                            os.symlink(hook_link_src, hook_link)
                        except Exception as e:
                            sys.stderr.write('Failed creating directory and symlink %s: %s\n' % (hook_link, e))
                            sys.exit(1)
            else:
                if os.path.islink(hook_link) and os.readlink(hook_link == hook_link_src):
                    need_update += 1
                    if args.mode == 'update':
                        try:
                            os.unlink(hook_link)
                        except Exception as e:
                            sys.stderr.write('Failed to remove link %s: %s\n' % (hook_link, e))
                            sys.exit(1)

if args.mode == 'update':
    sys.exit(need_update)
