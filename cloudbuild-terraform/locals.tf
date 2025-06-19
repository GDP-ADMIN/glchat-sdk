locals {
  repository = {
    name                 = "glchat-sdk"
    owner                = "GDP-ADMIN"
    host-asia-southeast2 = "GDP-ADMIN3"
  }

  # Discover module names by listing directories in python/ that match the pattern
  libs_versions      = ["3.11", "3.12"]
  libs_modules_dirs  = distinct(flatten([for _, v in fileset("${path.module}/../libs", "**") : regex("([^/]*).*", dirname(v))]))
  libs_modules_names = slice(local.libs_modules_dirs, 1, length(local.libs_modules_dirs))
  libs_combined = flatten([
    for module in local.libs_modules_names : [
      for version in local.libs_versions : {
        module  = module
        version = version
      }
    ]
  ])

  # Discover module names by listing directories in python/ that match the pattern
  python_versions      = ["3.11", "3.12", "3.13"]
  python_modules_dirs  = distinct(flatten([for _, v in fileset("${path.module}/../python", "**") : regex("([^/]*).*", dirname(v))]))
  python_modules_names = slice(local.python_modules_dirs, 1, length(local.python_modules_dirs))
  python_combined = flatten([
    for module in local.python_modules_names : [
      for version in local.python_versions : {
        module  = module
        version = version
      }
    ]
  ])

  # Discover module names by listing directories in js/ that match the pattern
  js_modules_dirs  = distinct(flatten([for _, v in fileset("${path.module}/../js", "**") : regex("([^/]*).*", dirname(v))]))
  js_modules_names = slice(local.js_modules_dirs, 1, length(local.js_modules_dirs))
}
