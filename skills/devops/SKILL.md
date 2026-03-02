---
name: devops
description: DevOps and cloud provisioning skill with Terraform/AWS integration
version: 1.0.0
dependencies: []
---

# DevOps Skill

Autonomous infrastructure provisioning with Terraform and cloud provider CLI integration.

## Features

- Terraform init/plan/apply workflow
- AWS/GCP resource lookups
- Vercel CLI integration for frontend deployments
- Human-in-the-loop approval for terraform apply
- Structured plan output for review

## Usage

```python
from provisioner import DevOpsProvisioner

prov = DevOpsProvisioner()

# Initialize Terraform
prov.terraform_init("/path/to/infra")

# Generate plan (requires human approval)
plan = prov.terraform_plan("/path/to/infra")
prov.save_plan_for_review(plan, "review_plan.txt")

# Apply after approval
prov.terraform_apply("/path/to/infra", auto_approve=False)

# Deploy to Vercel
prov.vercel_deploy("./website")
```

```bash
openpango devops plan --dir ./infra
openpango devops apply --dir ./infra --plan review_plan.txt
```
