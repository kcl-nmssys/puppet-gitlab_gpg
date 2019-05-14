#!/usr/bin/python
#
# Get users' GPG keys from GitLab and import them into our keyring
# Part of puppet-gitlab_gpg - https://gitlab.nms.kcl.ac.uk/cm-puppet/puppet-gitlab_gpg
# Xand Meaden, May 2019

import gitlab
import yaml
