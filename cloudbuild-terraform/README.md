## CloudBuild Terraform

This folder contains Terraform files for creating a Cloud Build trigger.

## Prerequisites
1. The `tf-key.json` file must be in the `key` folder. You can generate it from a [Google Cloud Platform service account](https://cloud.google.com/iam/docs/service-accounts-create).
    ```
    cloudbuild-terraform|main⚡ ⇒ tree -L 2
    .
    ├── README.md
    ├── key
    │   └── tf-key.json <-- here
    ├── locals.tf
    ├── main.gdplabs.auto.tfvars
    ├── main.tf
    ├── main_backend.tf
    ├── main_locals.tf
    ├── main_provider.tf
    ├── main_variables.tf
    ├── outputs.tf
    └── terragrunt.hcl
    ```
   
2. Terraform version >= v1.9.0.
3. To apply Terraform
    ```
    # Initialize the Terraform module and remote backend
    terragrunt init

    # Plan the infrastructure
    terragrunt plan

    # Apply the infrastructure
    terragrunt apply
    ```
