#!/usr/bin/env python3
import os
import aws_cdk as cdk
from platform_infrastructure.eks_platform_stack import EksPlatformStack

STACK_CONFIG = {
    "vpc_cidr": "10.103.0.0/16",
    "admin_user_arn": "arn:aws:iam::994967120617:user/ychyzheuski",
    "environment": "development",
    "eks_cluster_name": "EksCluster"
}

app = cdk.App()

EksPlatformStack(
    app, "EksPlatformStack",
    config=STACK_CONFIG
)

app.synth()
