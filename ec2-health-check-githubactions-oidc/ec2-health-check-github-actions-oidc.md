# Automated EC2 VM Health Monitoring using GitHub Actions, AWS OIDC & AWS Systems Manager

## Project Overview

This project demonstrates an enterprise-grade SRE automation pattern that executes health checks on AWS EC2 instances without requiring SSH access, bastion hosts, or long-lived AWS credentials.

The solution leverages:

- GitHub Actions
- AWS OIDC Authentication
- AWS IAM Roles
- AWS Systems Manager (SSM)
- EC2
- Shell Scripting

---

## Architecture

```text
GitHub Repository
        ↓
GitHub Actions
        ↓
AWS OIDC Authentication
        ↓
GitHubActionsSSMRole
        ↓
AWS Systems Manager
        ↓
EC2 Instance
        ↓
Execute health_check.sh
        ↓
Return Output
        ↓
GitHub Actions Logs
```

---

## Business Problem

Traditional operational workflow:

```text
Engineer
   ↓
SSH into EC2
   ↓
Run Script
   ↓
Collect Output
   ↓
Prepare Report
```

Challenges:

- Manual effort
- SSH key management
- Limited auditability
- Difficult to scale
- Security concerns

---

## Solution Benefits

### Security

- No AWS access keys stored in GitHub
- Uses GitHub OIDC federation
- Temporary credentials only
- Least privilege IAM access

### Operations

- No SSH required
- Fully auditable
- Centralized execution
- Scalable to multiple instances

### Automation

- Triggered directly from GitHub
- Supports scheduled execution
- Can be extended for fleet management

---

## Repository Structure

```text
AI-Assisted-DevOps-Zero-to-Hero
│
├── .github
│   └── workflows
│       └── run-vm-health-check.yml
│
├── vm-health-monitor
│   └── scripts
│       └── health_check.sh
│
├── docs
│
├── README.md
│
└── .gitignore
```

---

## AWS Configuration

### Step 1: Create OIDC Identity Provider

Navigate to:

```text
IAM
→ Identity Providers
→ Add Provider
```

Configuration:

```text
Provider Type:
OpenID Connect

Provider URL:
https://token.actions.githubusercontent.com

Audience:
sts.amazonaws.com
```

---

### Step 2: Create GitHubActionsSSMRole

Navigate:

```text
IAM
→ Roles
→ Create Role
```

Select:

```text
Trusted Entity:
Web Identity
```

Provider:

```text
token.actions.githubusercontent.com
```

Audience:

```text
sts.amazonaws.com
```

---

## IAM Trust Policy

Replace account ID, repository owner, and repository name as needed.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GitHubActionsOIDCTrust",
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:parameshnaathi/AI-Assisted-DevOps-Zero-to-Hero:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

---

## GitHubActionsSSMRole Policy

Attach the following inline policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSSMSendCommand",
      "Effect": "Allow",
      "Action": [
        "ssm:SendCommand"
      ],
      "Resource": [
        "arn:aws:ssm:*:*:document/AWS-RunShellScript",
        "arn:aws:ec2:*:*:instance/*"
      ]
    },
    {
      "Sid": "AllowSSMCommandStatusRead",
      "Effect": "Allow",
      "Action": [
        "ssm:GetCommandInvocation",
        "ssm:ListCommandInvocations",
        "ssm:ListCommands"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## EC2 Configuration

Attach the following AWS managed policy to the EC2 IAM Role:

```text
AmazonSSMManagedInstanceCore
```

Navigate:

```text
EC2
→ Instance
→ Actions
→ Security
→ Modify IAM Role
```

---

## GitHub Repository Variables

Navigate:

```text
Repository
→ Settings
→ Secrets and Variables
→ Actions
→ Variables
```

Create:

### AWS_ROLE_ARN

```text
arn:aws:iam::<AWS_ACCOUNT_ID>:role/GitHubActionsSSMRole
```

### AWS_REGION

Example:

```text
us-east-1
```

---

## Health Check Script

Location:

```text
vm-health-monitor/scripts/health_check.sh
```

Checks:

- CPU Utilization
- Memory Utilization
- Disk Utilization

Threshold:

```text
Healthy < 60%
Not Healthy > 60%
```

Sample Output:

```text
====================================
 VM Health Check Report
====================================
Hostname      : ip-172-31-10-25
Checked At    : Thu May 22 10:45:00 UTC 2026
CPU Usage     : 15%
Memory Usage  : 28%
Disk Usage    : 32%
Health Status : Healthy
Reason        : All metrics are within threshold
====================================
```

---

## GitHub Actions Workflow Responsibilities

### Authenticate

```text
GitHub OIDC
↓
AWS IAM Role
```

### Execute

```text
AWS Systems Manager
↓
Run Command
```

### Clone Repository

```bash
git clone
```

### Execute Script

```bash
./health_check.sh explain
```

### Return Results

```text
GitHub Actions Logs
```

---

## Running the Workflow

Navigate:

```text
GitHub Repository
→ Actions
→ Run VM Health Check on AWS EC2
→ Run Workflow
```

Input:

```text
EC2 Instance ID
```

Example:

```text
i-0581f7713dbdb27b2
```

---

## Validation

### Verify OIDC Authentication

```bash
aws sts get-caller-identity
```

Expected:

```json
{
  "Account": "683728592362",
  "Arn": "arn:aws:sts::683728592362:assumed-role/GitHubActionsSSMRole/GitHubActions"
}
```

---

### Verify SSM Registration

```bash
aws ssm describe-instance-information
```

Your EC2 instance should appear in the output.

---

## Troubleshooting

### OIDC Provider Missing

Error:

```text
No OpenIDConnect provider found
```

Resolution:

```text
Create GitHub OIDC Provider in AWS IAM
```

---

### AssumeRoleWithWebIdentity Failed

Error:

```text
Not authorized to perform sts:AssumeRoleWithWebIdentity
```

Resolution:

```text
Verify IAM Trust Policy
Verify GitHub Repository Owner
Verify Branch Name
Verify AWS_ROLE_ARN Variable
```

---

### git Not Found

Error:

```text
git: command not found
```

Resolution:

```text
Install git dynamically using SSM
```

---

### Script Not Found

Error:

```text
health_check.sh not found
```

Resolution:

```text
Auto-discover script path after repository clone
```

---

## Future Enhancements

### Fleet-wide Execution

Execute against all instances using tags:

```bash
--targets Key=tag:Environment,Values=Prod
```

---

### Teams Notifications

```text
GitHub Actions
        ↓
Microsoft Teams
```

---

### CloudWatch Metrics

```text
Health Script
        ↓
CloudWatch
        ↓
Grafana Dashboard
```

---

### Scheduled Execution

```yaml
on:
  schedule:
    - cron: '0 */6 * * *'
```

Runs every 6 hours.

---

## Key Learnings

- GitHub Actions
- AWS OIDC Authentication
- IAM Trust Relationships
- AWS Systems Manager (SSM)
- EC2 Automation
- Infrastructure as Code Concepts
- SRE Automation Patterns
- Cloud Security Best Practices
- Remote Command Orchestration
- CI/CD Integration

---

## Resume-Worthy Project Summary

Designed and implemented a secure, passwordless infrastructure automation framework using GitHub Actions, AWS OIDC, IAM Roles, and AWS Systems Manager to remotely execute operational health checks on EC2 instances without SSH access. Automated deployment, authentication, execution, and reporting workflows while following modern cloud security and least-privilege principles.