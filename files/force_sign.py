#!/usr/bin/python
#
# Reject (or warn) pushes of unsigned commits to a GitLab repository
# Part of puppet-gitlab_gpg - https://github.com/kcl-nmssys/puppet-gitlab_gpg

import datetime
import json
import os
import subprocess
import sys
import syslog
import time
import yaml

def git_show(commit, format):
    output = ''
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

    if group_project.startswith('@hashed'):
        project_hash = os.path.basename(group_project)
        try:
            with open('/etc/gitlab_gpg/hashes.yaml') as fh:
                hashes = yaml.load(fh, Loader=yaml.SafeLoader)
        except:
            sys.stderr.write('Failed to load hashes file\n')
            sys.exit(1)
        if project_hash in hashes:
            group_project = hashes[project_hash]
        else:
            sys.stderr.write('Cannot determine group/project\n')
            sys.exit(1)

    if os.path.exists('/etc/gitlab_gpg/repos/%s.yaml' % group_project):
        try:
            with open('/etc/gitlab_gpg/repos/%s.yaml' % group_project) as fh:
                config.update(yaml.load(fh, Loader=yaml.SafeLoader))
        except:
            sys.stderr.write('Failed to load specific configuration file\n')
            sys.exit(1)
    else:
        group = group_project.split('/')[0]
        if os.path.exists('/etc/gitlab_gpg/groups/%s.yaml' % group):
            try:
                with open('/etc/gitlab_gpg/groups/%s.yaml' % group) as fh:
                    config.update(yaml.load(fh, Loader=yaml.SafeLoader))
            except:
                sys.stderr.write('Failed to load specific configuration file\n')
                sys.exit(1)
        else:
            sys.stderr.write('Cannot find configuration file for this group/project\n')
            sys.exit(1)

else:
    sys.stderr.write('Unexpected current directory\n')
    sys.exit(1)

branch = sys.argv[1]
rev_old = sys.argv[2]
rev_new = sys.argv[3]
username = os.environ['GL_USERNAME']

# Special 'hash' used when there are no previous commits
zeroes = '0000000000000000000000000000000000000000'

# Branch deletion
if rev_new == zeroes:
    syslog.syslog(syslog.LOG_INFO, 'Branch deleted: %s by %s' % (branch, username))
    sys.exit(0)

if rev_old == zeroes:
    git_rev_args = [rev_new, '--not', '--branches=*', '--no-merges']
else:
    git_rev_args = ['--no-merges', '%s..%s' % (rev_old, rev_new)]

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
    'message': 'B',
    'sig_status': 'G?'
}

messages = []
if config['ensure'] == 'protected':
    messages.append(config['reject_message'])
else:
    messages.append(config['warning_message'])

# New branch with no new commits
if len(commits) == 1 and commits[0] == '':
    sys.exit(0)

for commit in commits:
    meta = {}
    for field_name in fields.keys():
        meta[field_name] = git_show(commit, fields[field_name])
    if meta['sig_status'] in ['B', 'E', 'N', 'R']:
        message = 'Commit: %s\n' % commit
        message += 'Author: %s <%s>\n' % (meta['author_name'], meta['author_email'])
        message += 'Date: %s\n' % datetime.datetime.fromtimestamp(int(meta['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
        message += 'GPG status: %s (%s)\n' % (meta['sig_status'], sig_status[meta['sig_status']])
        message += 'Message: %s\n' % meta['message']
        messages.append(message)
        if config['ensure'] == 'protected':
            exit_status = 1
            json_message = json.dumps({
                'commit': commit,
                'author': {'name': meta['author_name'], 'email': meta['author_email']},
                'committer': {'name': meta['committer_name'], 'email': meta['committer_email']},
                'username': username,
                'timestamp': int(meta['timestamp']),
                'message': meta['message'],
                'gpg_status': meta['sig_status'],
            })
            syslog.syslog(syslog.LOG_WARNING, 'Rejected commit %s' % commit)
            syslog.syslog(syslog.LOG_WARNING, json_message)
            proc = subprocess.Popen(config['notify_bin'], stdin=subprocess.PIPE)
            proc.communicate(input=json_message)

if len(messages) > 1:
    for message in messages:
        print(message)

sys.exit(exit_status)
