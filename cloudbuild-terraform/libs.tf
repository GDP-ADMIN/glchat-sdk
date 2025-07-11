module "gcb_gen_ai_external_pr_sdk" {
  source     = "s3::https://s3.amazonaws.com/gl-terraform-modules/terraform-gcp-gcb/terraform-gcp-gcb-1.0.0.zip"
  location   = var.region
  project_id = local.project_id.gdplabs
  for_each   = { for idx, val in local.libs_combined : "${val.module}-${val.version}" => val }

  name        = lower(replace("${local.repository["name"]}-pr-${each.value.module}-${each.value.version}", ".", "-"))
  description = "Gen AI External SDK"
  owner       = local.repository["host-asia-southeast2"]
  repo_name   = local.repository["name"]
  substitutions = {
    "_MODULE"   = each.value.module
    "_VERSION"  = each.value.version
    "_LANGUAGE" = "libs"
  }
  filename       = "cloudbuild-pr.yml"
  included_files = ["libs/${each.value.module}/**"]
  trigger_config = {
    trigger_type    = "PR"
    branch_regex    = ".*"
    tag_regex       = null
    comment_control = "COMMENTS_ENABLED_FOR_EXTERNAL_CONTRIBUTORS_ONLY"
  }
}

# module "gcb_gen_ai_external_push_sdk" {
#   source     = "s3::https://s3.amazonaws.com/gl-terraform-modules/terraform-gcp-gcb/terraform-gcp-gcb-1.0.0.zip"
#   location   = var.region
#   project_id = local.project_id.gdplabs
#   for_each   = { for idx, val in local.libs_combined : "${val.module}-${val.version}" => val }

#   name        = lower(replace("${local.repository["name"]}-push-${each.value.module}-${each.value.version}", ".", "-"))
#   description = "Gen AI External SDK"
#   owner       = local.repository["host-asia-southeast2"]
#   repo_name   = local.repository["name"]
#   substitutions = {
#     "_MODULE"   = each.value.module
#     "_VERSION"  = each.value.version
#     "_LANGUAGE" = "libs"
#   }
#   filename       = "cloudbuild.yml"
#   included_files = ["libs/${each.value.module}/**"]
#   trigger_config = {
#     trigger_type    = "PUSH"
#     branch_regex    = "^main$"
#     tag_regex       = null
#     comment_control = null
#   }
# }

module "gcb_gen_ai_external_push_tag_sdk" {
  source     = "s3::https://s3.amazonaws.com/gl-terraform-modules/terraform-gcp-gcb/terraform-gcp-gcb-1.0.0.zip"
  location   = var.region
  project_id = local.project_id.gdplabs
  for_each   = { for idx, val in local.libs_combined : "${val.module}-${val.version}" => val }

  name        = lower(replace("${local.repository["name"]}-push-tag-${each.value.module}-${each.value.version}", ".", "-"))
  description = "Gen AI External SDK"
  owner       = local.repository["host-asia-southeast2"]
  repo_name   = local.repository["name"]
  substitutions = {
    "_MODULE"   = each.value.module
    "_VERSION"  = each.value.version
    "_LANGUAGE" = "libs"
  }
  filename       = "cloudbuild.yml"
  trigger_config = {
    trigger_type    = "PUSH"
    branch_regex    = null
    tag_regex       = "${replace(each.value.module, "-", "_")}-v*"
    comment_control = null
  }
}
