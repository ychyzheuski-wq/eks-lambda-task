from aws_cdk import (
    Stack,
    aws_ssm as ssm,
    aws_ec2 as ec2,
    aws_eks as eks,
    CfnOutput
)

from aws_cdk.lambda_layer_kubectl_v32 import KubectlV32Layer
from constructs import Construct

class AwsCdkProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ssm_parameter = ssm.StringParameter(
            self, "ParameterAccountEnv",
            parameter_name="/platform/account/env",
            string_value="development",
            description="Setting the environment development / staging / production for the account." 
        )

        vpc = ec2.Vpc(
            self, "VPC", 
            ip_addresses=ec2.IpAddresses.cidr("10.102.0.0/16"),
            max_azs=2,
            subnet_configuration=[
                    ec2.SubnetConfiguration(
                        name="Public",
                        subnet_type=ec2.SubnetType.PUBLIC,
                        cidr_mask=24
                    ),
                    ec2.SubnetConfiguration(
                        name="Private",
                        subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                        cidr_mask=24
                    )
            ]
        )

        eks_cluster = eks.Cluster(
            self, "EKSCluster",
            vpc=vpc,
            version=eks.KubernetesVersion.V1_32,
            kubectl_layer=KubectlV32Layer(self, "kubectl"),
            default_capacity=1,
            default_capacity_instance=ec2.InstanceType("t3.medium"),
            endpoint_access=eks.EndpointAccess.PUBLIC,
            cluster_name="CustomResourceEksCluster"
        )

        CfnOutput(
            self, "ClusterNameOutput",
            value=eks_cluster.cluster_name,
            description="The EKS Cluster Name"
        )


