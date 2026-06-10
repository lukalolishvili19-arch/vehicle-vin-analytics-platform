# Terraform variables
# TODO: Define input variables

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}
