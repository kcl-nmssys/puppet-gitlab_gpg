# Main class for gitlab_gpg
#
# Default settings are in data/common.yaml
#
# @param api_package_name
#   Name of python package providing GitLab API functionality
# @param api_package_version
#   Version number of aforementioned package
# @param install_path
#   Path to directory for configuration and scripts
# @param repos_path
#   Path to GitLab repositories
# @param gpg_path
#   Path to gpg binary
# @param git_path
#   Path to git binary
# @param git_user
#   Name of gitlab git user
# @param git_group
#   Name of gitlab git user's primary group
# @param gitlab_hostname
#   FQDN of gitlab server (from its public URL)
# @param gitlab_auth_token
#   An authentication token for a GitLab admin user
# @param reject_message
#   Message displayed when pushing unsigned commits (in protected mode)
# @param warning_message
#   Message displayed when pushing unsigned commits (in warn mode)
# @param extra_gpg_keys
#   Extra GPG keys to import e.g. for former users
# @param protected_repos
#   Hash of protected repos, group => [project1, project2]
# @param notify_bin
#   Path to a program which notified when a push is rejected

class gitlab_gpg (
  String $api_package_name,
  String $api_package_version,
  String $install_path,
  String $repos_path,
  String $gpg_path,
  String $git_path,
  String $git_user,
  String $git_group,
  String $gitlab_hostname,
  String $gitlab_auth_token,
  String $reject_message,
  String $warning_message,
  Hash[String, String] $extra_gpg_keys,
  Hash[String, Array[String]] $protected_repos,
  String $notify_bin,
) {

  contain ::gitlab_gpg::install
  contain ::gitlab_gpg::config

  Class['::gitlab_gpg::install']
  -> Class['::gitlab_gpg::config']
}
