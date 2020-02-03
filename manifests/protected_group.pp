# Protect a GitLab group - ensure all new commits in all contined projects are GPG-signed
#
# @param group
#   Group name - defaults to title
# @param ensure
#   Whether to protect it or not, or to issue a warning

define gitlab_gpg::protected_group (
  Pattern[/\A([a-zA-Z0-9_\.][a-zA-Z0-9_\-\.]*[a-zA-Z0-9_\-]|[a-zA-Z0-9_])\z/] $group = $title,
  Enum['protected', 'unprotected', 'warn'] $ensure = 'protected',
) {

  if $ensure == 'protected' or $ensure == 'warn' {
    file {
      "/etc/gitlab_gpg/groups/${group}.yaml":
        ensure  => 'present',
        owner   => 'root',
        group   => $::gitlab_gpg::git_group,
        mode    => '0440',
        content => to_yaml({'ensure' => $ensure});
    }

    exec {
      "${::gitlab_gpg::install_path}/bin/protect_group.py --ensure present --mode update --group ${group}":
        user    => 'root',
        unless  => "${::gitlab_gpg::install_path}/bin/protect_group.py --ensure present --mode check --group ${group}",
        require => File["${::gitlab_gpg::install_path}/bin/protect_group.py"];
    }
  } else {
    file {
      "/etc/gitlab_gpg/groups/${group}.yaml":
        ensure => 'absent';
    }

    exec {
      "${::gitlab_gpg::install_path}/bin/protect_group.py --ensure absent --mode update --group ${group}":
        user    => 'root',
        unless  => "${::gitlab_gpg::install_path}/bin/protect_group.py --ensure absent --mode check --group ${group}",
        require => File["${::gitlab_gpg::install_path}/bin/protect_group.py"];
    }
  }
}
