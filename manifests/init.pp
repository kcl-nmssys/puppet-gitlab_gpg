# Main class for gitlab_gpg
#
# Default settings are in data/common.yaml
#
# @param os_packages
#   List of OS packages required
# @param install_path
#   Path to directory for configuration and scripts
# @param repos_path
#   Path to GitLab repositories
# @param git_path
#   Path to git binary
# @param git_user
#   Name of gitlab git user
# @param git_group
#   Name of gitlab git user's primary group
# @param git_user_home
#   Path to git user's home directory
# @param gitlab_hostname
#   FQDN of gitlab server (from its public URL)
# @param gitlab_auth_token
#   An authentication token for a GitLab admin user
# @param reject_message
#   Message displayed when pushing unsigned commits (in protected mode)
# @param warning_message
#   Message displayed when pushing unsigned commits (in warn mode)
# @param trusted_keys
#   Hash of trusted GPG public keys, gitlab_username => concatenated base64 keys
# @param protected_repos
#   Hash of protected repos, group => [project1, project2]
# @param notify_bin
#   Path to a program which notified when a push is rejected
# @param manage_gitlab_keys
#   Whether to manage users' keys in GitLab

class gitlab_gpg (
  Array[String] $os_packages,
  String $install_path,
  String $repos_path,
  String $git_path,
  String $git_user,
  String $git_group,
  String $git_user_home,
  String $gitlab_hostname,
  String $gitlab_auth_token,
  String $reject_message,
  String $warning_message,
  Hash[Pattern[/\A[a-zA-Z0-9_.-]+\z/], String] $trusted_keys,
  Hash[Pattern[/\A([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])\z/], Hash[Pattern[/\A([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])\z/], Enum['protected', 'unprotected', 'warn']]] $protected_repos,
  Hash[Pattern[/\A([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])\z/], Enum['protected', 'unprotected', 'warn']] $protected_groups,
  String $notify_bin,
  Boolean $manage_gitlab_keys,
) {

  contain ::gitlab_gpg::install
  contain ::gitlab_gpg::config

  Class['::gitlab_gpg::install']
  -> Class['::gitlab_gpg::config']
}
