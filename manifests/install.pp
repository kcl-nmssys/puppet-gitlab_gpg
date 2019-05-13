class gitlab_gpg::install {
  $pip_package = $facts['os']['family'] ? {
    'RedHat' => 'python2-pip',
    'Debian' => 'python-pip',
  }

  ensure_packages([$pip_package])

  package {
    $::gitlab_gpg::api_package_name:
      ensure => $::gitlab_gpg::api_package_version,
      provider => 'pip',
      require => Package[$pip_package];
  }

  file {
    $::gitlab_gpg::install_path:
      ensure => 'directory',
      owner => 'root',
      group => $::gitlab_gpg::git_group,
      mode => '0550';
  }
}
