import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_cdk_project.aws_cdk_project_stack import AwsCdkProjectStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_cdk_project/aws_cdk_project_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsCdkProjectStack(app, "aws-cdk-project")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
