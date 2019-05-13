class gitlab_gpg::config {
  $configuration = {
    gitlab_hostname => $::gitlab_gpg::gitlab_hostname,
    gitlab_auth_token => $::gitlab_gpg::gitlab_auth_token,
    extra_gpg_keys => $::gitlab_gpg::extra_gpg_keys,
  }

  file {
    $::gitlab_gpg::config_file:
      ensure => 'present',
      owner => 'root',
      group => $::gitlab_gpg::git_group,
      mode => '0440',
      content => to_yaml($configuration),
      show_diff => false;
  }
}
