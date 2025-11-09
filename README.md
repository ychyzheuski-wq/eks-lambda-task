
# AWS CDK EKS Project with Dynamic Nginx Ingress

A Python-based AWS CDK project that deploys an EKS cluster with environment-aware ingress-nginx configuration using Lambda-backed CustomResources.

## Architecture

This project creates:

- **EKS Cluster** with Bottlerocket node group
- **SSM Parameter** for environment configuration (`/platform/account/env`)
- **Lambda Function** that reads SSM values and generates dynamic Helm chart values
- **Ingress-nginx Helm Chart** with environment-specific replica counts
- **VPC** with public/private subnets and necessary endpoints

## Features

- **Environment-aware scaling**: 
  - `development` → 1 ingress controller replica
  - `staging/production` → 2 ingress controller replicas
  - Any other value defaults to 1 ingress controller replica
- **Infrastructure as Code** using AWS CDK
- **Custom Resource** for dynamic configuration
- **Secure networking** with VPC endpoints for SSM and S3

## Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.10+
- Node.js (for CDK CLI)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd aws-cdk-project
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

## Deployment

1. **Configure AWS credentials:**
   ```bash
   aws configure
   # OR use AWS SSO/assume role as needed
   ```

2. **Bootstrap CDK (first time only):**
   ```bash
   cdk bootstrap
   ```

3. **Deploy the stack:**
   ```bash
   cdk deploy
   ```

4. **Connect to EKS cluster:**
   ```bash
   aws eks update-kubeconfig --region us-east-1 --name EksCluster
   ```

## Testing

Run unit tests for the Lambda function:

```bash
python -m pytest tests/unit/test_ssm_lambda.py -v
```

## Project Structure

```
aws-cdk-project/
├── aws_cdk_project/           # CDK stack definition
│   ├── __init__.py
│   └── aws_cdk_project_stack.py
├── lambda/                    # Lambda function code
│   └── ssm_reader_handler.py
├── tests/                     # Unit tests
│   └── unit/
│       └── test_ssm_lambda.py
├── app.py                     # CDK app entry point
├── requirements.txt           # Python dependencies
├── cdk.json                   # CDK configuration
└── README.md
```

## Configuration

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