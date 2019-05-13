require 'puppetlabs_spec_helper/rake_tasks'
require 'puppet-syntax/tasks/puppet-syntax'
require 'puppet_blacksmith/rake_tasks' if Bundler.rubygems.find_name('puppet-blacksmith').any?
require 'puppet-strings/tasks' if Bundler.rubygems.find_name('puppet-strings').any?

PuppetLint.configuration.ignore_paths = ['vendor/**/*']
PuppetLint.configuration.disable_checks = ['relative', 'arrow_alignment', 'documentation']
PuppetLint.configuration.fail_on_warnings = false
PuppetLint.configuration.with_context = true
PuppetLint.configuration.show_ignored = true
PuppetLint.configuration.relative = true

PuppetLint::RakeTask.new :lint do |config|
  # List of checks to disable
  config.disable_checks = ['relative', 'arrow_alignment', 'documentation']

  # Should the task fail if there were any warnings, defaults to false
  config.fail_on_warnings = false

  # Print out the context for the problem, defaults to false
  config.with_context = true

  # Show ignored problems in the output, defaults to false
  config.show_ignored = true

  # Compare module layout relative to the module root
  config.relative = true
end