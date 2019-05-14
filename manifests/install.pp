class gitlab_gpg::install {
  case $facts['os']['family'] {
    'RedHat': {
      $os_packages = ['python2-pip', 'PyYAML']
    }
    'Debian': {
      $os_packages = ['python-pip', 'python-yaml']
    }
  }

  ensure_packages($os_packages)

  package {
    $::gitlab_gpg::api_package_name:
      ensure => $::gitlab_gpg::api_package_version,
      provider => 'pip',
      require => Package[$os_packages];
  }

  file {
    [$::gitlab_gpg::install_path, "${::gitlab_gpg::install_path}/bin", "${::gitlab_gpg::install_path}/keys"]:
      ensure => 'directory',
      owner => 'root',
      group => $::gitlab_gpg::git_group,
      mode => '0550';

    "${::gitlab_gpg::install_path}/bin/force_sign.py":
      ensure => 'present',
      owner => 'root',
      group => $::gitlab_gpg::git_group,
      mode => '0550';

    "${::gitlab_gpg::install_path}/bin/get_keys.py":
      ensure => 'present',
      owner => 'root',
      group => $::gitlab_gpg::git_group,
      mode => '0550';
  }
}
