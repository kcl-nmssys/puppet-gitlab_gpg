#!/usr/bin/python
#
# Reject (or warn) pushes of unsigned commits to a GitLab repository
# Part of puppet-gitlab_gpg - https://github.com/kcl-nmssys/puppet-gitlab_gpg

import datetime
import os
import subprocess
import sys
import syslog
import time
import yaml

def git_show(commit, format):
    try:
        output = subprocess.check_output([config['git_path'], 'show', commit, '-s', '--format=%%%s' % format])
    except:
        sys.stderr.write('Failed to get git data %s for commit %s' % (format, commit))
    return output.strip()

try:
    with open('/etc/gitlab_gpg/config.yaml') as fh:
        config = yaml.load(fh, Loader=yaml.SafeLoader)
except:
    sys.stderr.write('Failed to load main configuration file\n')
    sys.exit(1)

cwd = os.getcwd()
if cwd.startswith(config['repos_path']):
    group_project = cwd[len(config['repos_path']) + 1:-4]
    try:
        with open('/etc/gitlab_gpg/repos/%s.yaml' % group_project) as fh:
            config.update(yaml.load(fh, Loader=yaml.SafeLoader))
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

exit_status = 0

commit_meta = {}
sig_status = {
    'G': 'good signature',
    'U': 'good signature, unknown validity',
    'X': 'good signature, expired',
    'Y': 'good signature, expired key',
    'R': 'good signature, revoked key',
    'B': 'bad signature',
    'E': 'cannot check',
    'N': 'not signed',
}
fields = {
    'author_email': 'ae',
    'author_name': 'an',
    'committer_email': 'ce',
    'committer_name': 'cn',
    'timestamp': 'ct',
    'comment': 'B',
    'sig_status': 'G?'
}
for commit in commits:
    commit_meta[commit] = {}
    for field_name in fields.keys():
        commit_meta[commit][field_name] = git_show(commit, fields[field_name])
    if commit_meta['sig_status'] in ['B', 'E', 'N', 'R']:
        if config['ensure'] == 'protected':
            exit_status = 1
