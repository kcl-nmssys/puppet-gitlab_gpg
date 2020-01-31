class gitlab_gpg::config {
  $configuration = {
    gitlab_hostname   => $::gitlab_gpg::gitlab_hostname,
    gitlab_auth_token => $::gitlab_gpg::gitlab_auth_token,
    extra_gpg_keys    => keys($::gitlab_gpg::extra_gpg_keys),
    notify_bin        => $::gitlab_gpg::notify_bin,
    install_path      => $::gitlab_gpg::install_path,
    repos_path        => $::gitlab_gpg::repos_path,
  }

  file {
    '/etc/gitlab_gpg/config.yaml':
      ensure    => 'present',
      owner     => 'root',
      group     => $::gitlab_gpg::git_group,
      mode      => '0440',
      content   => to_yaml($configuration),
      show_diff => false;
  }

  $::gitlab_gpg::protected_repos.each |$group, $projects| {
    ::gitlab_gpg::protected_repo {
      "${group}/${project}":
        ensure => 'protected';
    }
  }

  $::gitlab_gpg::trusted_keys.each |$username, $user_keys| {
    $user_keys.each |$key| {
      $md5 = md5($key)
      file {
        "${::gitlab_gpg::install_path}/keys/trusted/${username}_${md5}.pub":
          ensure  => 'present',
          owner   => 'root',
          group   => $::gitlab_gpg::git_group,
          mode    => '0640',
          content => "${key}\n",
          before  => Exec["${::gitlab_gpg::install_path}/bin/get_keys.py --import"];
      }
    }
  }

  exec {
    "${::gitlab_gpg::install_path}/bin/get_keys.py --mode import":
      user    => $::gitlab_gpg::git_user,
      unless  => "${::gitlab_gpg::install_path}/bin/get_keys.py --mode check",
      require => [File[$::gitlab_gpg::config_file]];
  }
}
