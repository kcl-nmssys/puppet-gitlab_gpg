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
# @param extra_gpg_keys
#   Extra GPG keys to import e.g. for former users
# @param protected_repos
#   Hash of protected repos, group => [project1, project2]

class gitlab_gpg (
  String $api_package_name,
  String $api_package_version,
  String $install_path,
  String $repos_path,
  String $git_path,
  String $git_user,
  String $git_group,
  String $gitlab_hostname,
  String $gitlab_auth_token,
  Hash[Pattern[/\A[0-9A-F]{16}\z/], String] $extra_gpg_keys,
  Hash[String, Array[String]] $protected_repos,
) {

  $config_file = "${install_path}/config.yaml"

  contain ::gitlab_gpg::install
  contain ::gitlab_gpg::config

  Class['::gitlab_gpg::install']
  -> Class['::gitlab_gpg::config']
}
