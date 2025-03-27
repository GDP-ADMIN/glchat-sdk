locals {
  repository = {
    name  = "gen-ai-external"
    owner = "GDP-ADMIN"
  }
  
  versions = [
    "3.11", "3.12"
  ]

  # Discover module names by listing directories in libs/ that match the pattern
  modules_dirs = distinct(flatten([for _, v in fileset("${path.module}/../libs", "**") : regex("([^/]*).*", dirname(v))]))
  modules_names = slice(local.modules_dirs, 1, length(local.modules_dirs))
  combined = flatten([
    for module in local.modules_names : [
      for version in local.versions : {
        module = module
        version = version
      }
    ]
  ])
}
