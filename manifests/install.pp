class gitlab_gpg::install {
  case $facts['os']['family'] {
    'RedHat': {
      $os_packages = ['python2-pip', 'python2-requests', 'PyYAML', 'python2-gnupg', 'python2-gitlab']
    }
    'Debian': {
      $os_packages = ['python-pip', 'python-requests', 'python-yaml', 'python-gnupg', 'python-gitlab']
    }
  }

  ensure_packages($os_packages)

  file {
    [$::gitlab_gpg::install_path, "${::gitlab_gpg::install_path}/bin", "${::gitlab_gpg::install_path}/keys", "${::gitlab_gpg::install_path}/keys/gitlab", "${::gitlab_gpg::install_path}/extra"]:
      ensure => 'directory',
      owner  => 'root',
      group  => $::gitlab_gpg::git_group,
      mode   => '0550';

    "${::gitlab_gpg::install_path}/bin/force_sign.py":
      ensure => 'present',
      owner  => 'root',
      group  => $::gitlab_gpg::git_group,
      mode   => '0550',
      source => 'puppet:///modules/gitlab_gpg/force_sign.py';

    "${::gitlab_gpg::install_path}/bin/get_keys.py":
      ensure => 'present',
      owner  => 'root',
      group  => $::gitlab_gpg::git_group,
      mode   => '0550',
      source => 'puppet:///modules/gitlab_gpg/get_keys.py';
  }
}
