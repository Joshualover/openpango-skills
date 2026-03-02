"""
DevOps Provisioner for OpenPango
Terraform and cloud provider integration with HITL approval
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime


class DevOpsProvisioner:
    """Infrastructure provisioning with Terraform and cloud CLIs."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = Path(workspace_dir or os.path.expanduser(
            "~/.openclaw/workspace/infra"
        ))
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self._require_approval = True
    
    def _run_command(self, cmd: list, cwd: str = None, capture: bool = True) -> dict:
        """Run a shell command and return result."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=capture,
                text=True,
                timeout=300
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 300s",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def terraform_init(self, infra_dir: str) -> dict:
        """Initialize Terraform in the given directory."""
        infra_path = Path(infra_dir)
        if not infra_path.exists():
            infra_path.mkdir(parents=True, exist_ok=True)
            # Create basic main.tf if doesn't exist
            main_tf = infra_path / "main.tf"
            if not main_tf.exists():
                main_tf.write_text("""# Terraform configuration
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
""")
        
        return self._run_command(["terraform", "init"], cwd=str(infra_path))
    
    def terraform_plan(self, infra_dir: str, out_file: str = None) -> dict:
        """
        Generate Terraform execution plan.
        
        Args:
            infra_dir: Path to Terraform configuration
            out_file: Optional path to save plan file
        
        Returns:
            Plan result with stdout/stderr
        """
        infra_path = Path(infra_dir)
        cmd = ["terraform", "plan", "-no-color"]
        
        if out_file:
            cmd.extend(["-out", out_file])
        
        result = self._run_command(cmd, cwd=str(infra_path))
        
        # Parse plan summary
        if result["success"]:
            output = result["stdout"]
            if "Plan:" in output:
                summary_line = [l for l in output.split('\n') if 'Plan:' in l][0]
                result["plan_summary"] = summary_line.strip()
        
        return result
    
    def save_plan_for_review(self, plan_result: dict, review_file: str) -> str:
        """Save terraform plan output for human review."""
        review_path = Path(review_file)
        
        review_content = f"""# Terraform Plan Review
Generated: {datetime.utcnow().isoformat()}Z

## Plan Summary
{plan_result.get('plan_summary', 'N/A')}

## Detailed Changes
{plan_result.get('stdout', 'No output')}

---
## Approval Required
This plan will modify infrastructure. Review carefully before approving.

To approve: openpango devops apply --plan {review_file}
To reject: Delete this file or run 'openpango devops reject --plan {review_file}'
"""
        
        review_path.write_text(review_content)
        return str(review_path)
    
    def terraform_apply(self, infra_dir: str, plan_file: str = None, 
                       auto_approve: bool = False) -> dict:
        """
        Apply Terraform configuration.
        
        Args:
            infra_dir: Path to Terraform configuration
            plan_file: Optional plan file to apply
            auto_approve: Skip human approval (DANGEROUS)
        
        Returns:
            Apply result
        """
        if self._require_approval and not auto_approve:
            raise RuntimeError(
                "HITL approval required. Use --auto-approve flag or set "
                "OPENPANGO_DEVOPS_AUTO_APPROVE=1 (not recommended for production)"
            )
        
        infra_path = Path(infra_dir)
        cmd = ["terraform", "apply", "-no-color"]
        
        if plan_file:
            cmd.append(plan_file)
        else:
            cmd.append("-auto-approve")
        
        return self._run_command(cmd, cwd=str(infra_path))
    
    def vercel_deploy(self, project_dir: str, prod: bool = False) -> dict:
        """
        Deploy to Vercel.
        
        Args:
            project_dir: Path to project
            prod: Deploy to production (default: preview)
        
        Returns:
            Deployment result
        """
        cmd = ["vercel", "deploy", "--yes"]
        if prod:
            cmd.append("--prod")
        
        return self._run_command(cmd, cwd=project_dir)
    
    def aws_lookup(self, resource_type: str, filters: dict = None) -> dict:
        """
        Look up AWS resources.
        
        Args:
            resource_type: EC2, S3, RDS, etc.
            filters: Optional filters
        
        Returns:
            Resource list
        """
        cmd = ["aws", resource_type.lower(), "describe"]
        
        if filters:
            for key, value in filters.items():
                cmd.extend(["--filters", f"Name={key},Values={value}"])
        
        return self._run_command(cmd)
    
    def require_approval(self, require: bool = True):
        """Enable/disable HITL approval requirement."""
        self._require_approval = require


# CLI integration
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="DevOps Provisioner CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Plan command
    plan_parser = subparsers.add_parser("plan", help="Generate Terraform plan")
    plan_parser.add_argument("--dir", default="./infra", help="Infrastructure directory")
    plan_parser.add_argument("--out", help="Output plan file")
    
    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply Terraform plan")
    apply_parser.add_argument("--dir", default="./infra", help="Infrastructure directory")
    apply_parser.add_argument("--plan", help="Plan file to apply")
    apply_parser.add_argument("--auto-approve", action="store_true", help="Skip approval")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy to Vercel")
    deploy_parser.add_argument("--dir", default="./website", help="Project directory")
    deploy_parser.add_argument("--prod", action="store_true", help="Deploy to production")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Terraform")
    init_parser.add_argument("--dir", default="./infra", help="Infrastructure directory")
    
    args = parser.parse_args()
    
    prov = DevOpsProvisioner()
    
    if args.command == "init":
        result = prov.terraform_init(args.dir)
        print("Terraform initialized" if result["success"] else f"Error: {result['stderr']}")
    
    elif args.command == "plan":
        result = prov.terraform_plan(args.dir, args.out)
        if result["success"]:
            print(f"Plan generated: {result.get('plan_summary', 'See output')}")
            if args.out:
                prov.save_plan_for_review(result, args.out)
                print(f"Plan saved for review: {args.out}")
            print(result["stdout"])
        else:
            print(f"Error: {result['stderr']}")
    
    elif args.command == "apply":
        try:
            result = prov.terraform_apply(args.dir, args.plan, args.auto_approve)
            print("Infrastructure deployed" if result["success"] else f"Error: {result['stderr']}")
        except RuntimeError as e:
            print(f"Approval required: {e}")
    
    elif args.command == "deploy":
        result = prov.vercel_deploy(args.dir, args.prod)
        print("Deployed to Vercel" if result["success"] else f"Error: {result['stderr']}")


if __name__ == "__main__":
    main()
