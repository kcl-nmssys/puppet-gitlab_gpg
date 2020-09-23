class gitlab_gpg::config {
  $configuration = {
    gitlab_hostname    => $::gitlab_gpg::gitlab_hostname,
    gitlab_auth_token  => $::gitlab_gpg::gitlab_auth_token,
    notify_bin         => $::gitlab_gpg::notify_bin,
    error_bin          => $::gitlab_gpg::error_bin,
    install_path       => $::gitlab_gpg::install_path,
    repos_path         => $::gitlab_gpg::repos_path,
    git_path           => $::gitlab_gpg::git_path,
    manage_gitlab_keys => $::gitlab_gpg::manage_gitlab_keys,
    reject_message     => $::gitlab_gpg::reject_message,
    warning_message    => $::gitlab_gpg::warning_message,
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
    $projects.each |$project, $ensure| {
      ::gitlab_gpg::protected_repo {
        "${group}/${project}":
          group   => $group,
          project => $project,
          ensure  => $ensure;
      }
    }
  }

  $::gitlab_gpg::protected_groups.each |$group, $ensure| {
    ::gitlab_gpg::protected_group {
      $group:
        ensure => $ensure;
    }
  }

  $::gitlab_gpg::trusted_keys.each |$username, $user_keys| {
    file {
      "${::gitlab_gpg::install_path}/keys/trusted/${username}.pub":
        ensure  => 'present',
        owner   => 'root',
        group   => $::gitlab_gpg::git_group,
        mode    => '0640',
        content => "${user_keys}\n",
        before  => Exec["${::gitlab_gpg::install_path}/bin/manage_keys.py --mode update"];
    }
  }

  exec {
    "${::gitlab_gpg::install_path}/bin/manage_keys.py --mode update":
      user    => $::gitlab_gpg::git_user,
      onlyif  => "${::gitlab_gpg::install_path}/bin/manage_keys.py --mode check",
      require => [File[$::gitlab_gpg::config_file]];

    "${::gitlab_gpg::install_path}/bin/create_project_symlinks.py --mode update":
      user    => $::gitlab_gpg::git_user,
      onlyif  => "${::gitlab_gpg::install_path}/bin/create_project_symlinks.py --mode check",
      require => [File[$::gitlab_gpg::config_file]];
  }
}
