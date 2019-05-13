define gitlab_gpg::protected_repo (
  Pattern[/\A([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])/([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])\z/] $group_project = $title,
  Enum['protected', 'unprotected'] $ensure = 'protected',
) {

  file {
    "${::gitlab_gpg::repos_path}/${group_project}.git/custom_hooks":
      ensure => 'directory',
      owner => 'root',
      group => $::gitlab_gpg::git_group,
      mode => '0750';

    "${::gitlab_gpg::repos_path}/${group_project}.git/custom_hooks/pre-receive":
      ensure => 'link',
      target => "${::gitlab_gpg::install_path}/bin/force_sign.py";
  }
}
