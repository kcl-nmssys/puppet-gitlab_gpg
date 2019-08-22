class gitlab_gpg::config {
  $configuration = {
    gitlab_hostname   => $::gitlab_gpg::gitlab_hostname,
    gitlab_auth_token => $::gitlab_gpg::gitlab_auth_token,
    extra_gpg_keys    => keys($::gitlab_gpg::extra_gpg_keys),
  }

  file {
    $::gitlab_gpg::config_file:
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

  $::gitlab_gpg::extra_gpg_keys.each |$id, $key| {
    file {
      "${::gitlab_gpg::install_path}/keys/${id}.pub":
        ensure  => 'present',
        owner   => 'root',
        group   => $::gitlab_gpg::git_group,
        mode    => '0640',
        content => "${key}\n",
        before  => Exec["${::gitlab_gpg::install_path}/bin/get_keys.py --import"];
    }
  }

  exec {
    "${::gitlab_gpg::install_path}/bin/get_keys.py --mode import":
      user   => $::gitlab_gpg::git_user,
      unless => "${::gitlab_gpg::install_path}/bin/get_keys.py --mode check";
  }
}
