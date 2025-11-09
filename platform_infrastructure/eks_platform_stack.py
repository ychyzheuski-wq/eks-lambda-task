from aws_cdk import (
    Stack,
    aws_ssm as ssm,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_iam as iam,
    aws_lambda as _lambda,
    custom_resources as cr,
    CustomResource,
    CfnOutput,
    Duration
)

from aws_cdk.lambda_layer_kubectl_v32 import KubectlV32Layer
from constructs import Construct

class EksPlatformStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, 
                 config: dict,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ssm_parameter = ssm.StringParameter(
            self, "ParameterAccountEnv",
            parameter_name="/platform/account/env",
            string_value=config["environment"],
            description="Setting the environment development / stage / production for the account." 
        )

        vpc = ec2.Vpc(
            self, "VPC", 
            ip_addresses=ec2.IpAddresses.cidr(config["vpc_cidr"]),
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

        vpc.add_interface_endpoint("SsmEndpoint", service=ec2.InterfaceVpcEndpointAwsService.SSM)

        s3_endpoint = vpc.add_gateway_endpoint(
            "S3Gateway", 
            service=ec2.GatewayVpcEndpointAwsService.S3
        )
        s3_endpoint.add_to_policy(
            iam.PolicyStatement(
                principals=[iam.AnyPrincipal()],
                actions=["s3:*"],
                resources=["*"]
            )
        )

        eks_cluster = eks.Cluster(
            self, "EKSCluster",
            vpc=vpc,
            version=eks.KubernetesVersion.V1_32,
            kubectl_layer=KubectlV32Layer(self, "kubectl"),
            default_capacity=0,
            endpoint_access=eks.EndpointAccess.PUBLIC,
            cluster_name=config["eks_cluster_name"]
        )

        eks_cluster.add_nodegroup_capacity(
            "BottlerocketNodes",
            instance_types=[ec2.InstanceType("t3.medium")],
            min_size=1,
            max_size=2,
            desired_size=1,
            ami_type=eks.NodegroupAmiType.BOTTLEROCKET_X86_64,
            nodegroup_name="bottlerocket-nodegroup"
        )

        eks_cluster.aws_auth.add_user_mapping(
            iam.User.from_user_arn(
                self,
                "admin-user",
                config["admin_user_arn"]
            ),
            groups=["system:masters"]
        )

        lambda_sg = ec2.SecurityGroup(
            self, "CustomResourceLambdaSG",
            vpc=vpc,
            description="Security group for Custom Resource Lambda"
        )

        lambda_handler = _lambda.Function(
            self, "EnvironmentConfigHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="environment_config_handler.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.minutes(4),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[lambda_sg]
        )

        lambda_handler.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=["*"],
                effect=iam.Effect.ALLOW
            )
        )

        custom_resource_provider = cr.Provider(
            self, "CustomResourceProvider",
            on_event_handler=lambda_handler,
            log_group=None
        )

        helm_values_resource = CustomResource(
            self, "HelmValuesCustomResource",
            service_token=custom_resource_provider.service_token,
            resource_type="Custom::HelmValueGenerator",
            properties={
                "SsmParameterName": ssm_parameter.parameter_name, 
                "SSMValueTrigger": ssm_parameter.string_value
            }
        )

        replica_count = helm_values_resource.get_att("ReplicaCount")
        
        helm_values = {
            "controller": {
                "replicaCount": replica_count, 
                "electionId": "ingress-controller-leader"
            }
        }

        nginx_ingress_helm = eks.HelmChart(
            self, "NginxIngressHelm",
            cluster=eks_cluster,
            chart="ingress-nginx",
            repository="https://kubernetes.github.io/ingress-nginx",
            namespace="default",
            values=helm_values,
            release="nginx-ingress"
        )

        CfnOutput(
            self, "ClusterNameOutput",
            value=eks_cluster.cluster_name,
            description="The EKS Cluster Name"
        )