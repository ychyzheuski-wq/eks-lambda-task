
# AWS CDK EKS Platform with Dynamic Nginx Ingress

A Python-based AWS CDK project that deploys an EKS cluster with environment-aware ingress-nginx configuration using Lambda-backed CustomResources.

## Architecture

This project creates:

- **EKS Cluster** (Kubernetes v1.32) with Bottlerocket node group
- **SSM Parameter** for environment configuration (`/platform/account/env`)
- **Lambda Function** that reads SSM values and generates dynamic Helm chart values
- **Ingress-nginx Helm Chart** with environment-specific replica counts
- **VPC** with public/private subnets and necessary endpoints (SSM, S3)
- **IAM roles and policies** for secure access

## Features

- **Environment-aware scaling**: 
  - `development` → 1 ingress controller replica
  - `staging/production` → 2 ingress controller replicas
  - Any other value defaults to 1 ingress controller replica
- **Infrastructure as Code** using AWS CDK v2.215.0
- **Custom Resource** for dynamic configuration via Lambda
- **Secure networking** with VPC endpoints for SSM and S3
- **Professional naming** with `platform_infrastructure` structure
- **Unit tests** for Lambda function logic

## Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.10+
- Node.js (for CDK CLI)
- IAM user with proper permissions (not root account)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd eks-lambda-task/eks-lambda-task
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate 
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install CDK CLI (if not installed):**
   ```bash
   npm install -g aws-cdk
   ```

## Configuration

Before deploying, you need to configure the stack parameters in `app.py`. Update the `STACK_CONFIG` dictionary with your specific values:

```python
STACK_CONFIG = {
    "vpc_cidr": "10.103.0.0/16",                                    # VPC CIDR block
    "admin_user_arn": "arn:aws:iam::YOUR_ACCOUNT:user/YOUR_USER",   # Your IAM user ARN
    "environment": "development",                                   # Environment type
    "eks_cluster_name": "EksCluster"                               # EKS cluster name
}
```

**Important Notes:**
- Replace `YOUR_ACCOUNT` with your actual AWS account ID
- Replace `YOUR_USER` with your actual IAM username  
- The `admin_user_arn` must match the user you'll use for `aws configure`
- Different `environment` values will affect ingress-nginx replica count

## Deployment

1. **Get your IAM user ARN:**
   ```bash
   aws sts get-caller-identity
   # Copy the "Arn" value to use in app.py configuration
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   # Use the same IAM user that you specified in admin_user_arn
   ```

3. **Update configuration in app.py:**
   ```bash
   # Edit app.py and update STACK_CONFIG with your values
   # Especially the admin_user_arn field
   ```

4. **Bootstrap CDK (first time only):**
   ```bash
   cdk bootstrap
   ```

5. **Deploy the stack:**
   ```bash
   cdk deploy
   ```

6. **Connect to EKS cluster:**
   ```bash
   aws eks update-kubeconfig --region us-east-1 --name EksCluster
   kubectl get nodes
   kubectl get pods -A | grep nginx
   ```

## Testing

Run unit tests for the Lambda function logic:

```bash
source .venv/bin/activate

python -m pytest tests/unit/test_environment_config.py -v
```

## Project Structure

```
eks-lambda-task/
├── platform_infrastructure/           # CDK stack definition  
│   ├── __init__.py
│   └── eks_platform_stack.py         # Main EKS stack
├── lambda/                           # Lambda function code
│   ├── __init__.py
│   └── environment_config_handler.py # Environment config logic
├── tests/                           # Unit tests
│   └── unit/
│       ├── __init__.py
│       └── test_environment_config.py # Lambda function tests
├── app.py                          # CDK app entry point with configuration
├── requirements.txt                # Python dependencies
├── cdk.json                       # CDK configuration  
└── README.md                      # This file
```

## Configuration Details

### Environment Values

The SSM parameter `/platform/account/env` supports:

- `development` - Sets ingress controller replicas to 1
- `staging` - Sets ingress controller replicas to 2
- `production` - Sets ingress controller replicas to 2
- Any other value defaults to 1 replica

## Cleanup

To destroy the infrastructure:

```bash
cdk destroy
```