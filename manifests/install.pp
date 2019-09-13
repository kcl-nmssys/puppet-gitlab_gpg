class gitlab_gpg::install {
  ensure_packages($::gitlab_gpg::os_packages)

  file {
    ['/etc/gitlab_gpg', '/etc/gitlab_gpg/repos', $::gitlab_gpg::install_path, "${::gitlab_gpg::install_path}/bin", "${::gitlab_gpg::install_path}/keys", "${::gitlab_gpg::install_path}/keys/extra"]:
      ensure => 'directory',
      owner  => 'root',
      group  => $::gitlab_gpg::git_group,
      mode   => '0550';

    ["${::gitlab_gpg::install_path}/keys/gitlab", "${::gitlab_gpg::git_user_home}/.gnupg"]:
      ensure => 'directory',
      owner  => $::gitlab_gpg::git_user,
      group  => $::gitlab_gpg::git_group,
      mode   => '0700';

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
