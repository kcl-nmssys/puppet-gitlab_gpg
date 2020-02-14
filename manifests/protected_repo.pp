# Protect a GitLab project - ensure all new commits are GPG-signed
#
# @param group_project
#   Group and project names, separated by a / e.g. my_group/my_project - defaults to title
# @param ensure
#   Whether to protect it or not, or to issue a warning

define gitlab_gpg::protected_repo (
  Pattern[/\A([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])\/([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])\z/] $group_project = $title,
  Pattern[/\A([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])\z/] $group,
  Pattern[/\A([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])\z/] $project,
  Enum['protected', 'unprotected', 'warn'] $ensure = 'protected',
) {

  if $ensure == 'protected' or $ensure == 'warn' {
    ensure_resource(
      'file',
      "/etc/gitlab_gpg/repos/${group}",
      {
        ensure => 'directory',
        owner  => 'root',
        group  => $::gitlab_gpg::git_group,
        mode   => '0750',
      }
    )

    file {
      "${::gitlab_gpg::repos_path}/${group_project}.git/custom_hooks":
        ensure => 'directory',
        owner  => 'root',
        group  => $::gitlab_gpg::git_group,
        mode   => '0750';

      "${::gitlab_gpg::repos_path}/${group_project}.git/custom_hooks/update":
        ensure => 'link',
        target => "${::gitlab_gpg::install_path}/bin/force_sign.py";

      "/etc/gitlab_gpg/repos/${group_project}.yaml":
        ensure  => 'present',
        owner   => 'root',
        group   => $::gitlab_gpg::git_group,
        mode    => '0440',
        content => to_yaml({'ensure' => $ensure});
    }
  } else {
    file {
      [
        "${::gitlab_gpg::repos_path}/${group_project}.git/custom_hooks/update",
        "/etc/gitlab_gpg/repos/${group_project}.yaml",
      ]:
        ensure => 'absent';
    }
  }
}
