#!/usr/bin/python
#
# Reject (or warn) pushes of unsigned commits to a GitLab repository
# Part of puppet-gitlab_gpg - https://github.com/kcl-nmssys/puppet-gitlab_gpg

import os
import subprocess
import sys
import syslog
import yaml


try:
    with open('/etc/gitlab_gpg/config.yaml') as fh:
        config = yaml.load(fh, Loader=yaml.SafeLoader)
except:
    sys.stderr.write('Failed to load main configuration file\n')
    sys.exit(1)

cwd = os.getcwd()
if cwd.startswith(config['repos_path']):
    group_project = cwd[len(config['repos_path']):]
    try:
        with open('/etc/gitlab_gpg/repos/%s.yaml') as fh:
            config = config + yaml.load(fh, Loader=yaml.SafeLoader)
    except:
        sys.stderr.write('Failed to load specific configuration file\n')
        sys.exit(1)

branch = sys.argv[1]
rev_old = sys.argv[2]
rev_new = sys.argv[3]
username = os.environ['GL_USERNAME']

# Special 'hash' used when there are no previous commits
zeroes = '0000000000000000000000000000000000000000'

if rev_old == zeroes:
    git_rev_args = [rev_new, '--not', '--branches=*']
else:
    git_rev_args = ['%s..%s' % (rev_old, rev_new)]

try:
    commits = subprocess.check_output([config['git_path'], 'rev-list'] + git_rev_args).rstrip().split('\n')
except:
    sys.stderr.write('Failed to get commit list\n')
    sys.exit(1)

for commit in commits:


print(revs)
