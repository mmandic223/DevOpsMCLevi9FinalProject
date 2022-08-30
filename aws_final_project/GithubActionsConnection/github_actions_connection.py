from aws_cdk import (
    Duration,
    CfnOutput,
    aws_iam as iam,
    App,
)
from aws_cdk import Duration, RemovalPolicy, Stack
from constructs import Construct

class GithubConnection(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        github_org="mmandic223"
        github_repo="DevOpsMCLevi9FinalProject"

        github_provider = iam.OpenIdConnectProvider(self , "ghprovider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"]    
        )

        principle = iam.OpenIdConnectPrincipal(github_provider).with_conditions(
            conditions={
                "StringLike": {
                    'token.actions.githubusercontent.com:sub':
                        f'repo:{github_org}/{github_repo}:*'
                }
            }
        )

        principle.add_to_principal_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["sts:AssumeRoleWithWebIdentity"],
                resources=["*"]
            )
        )

        principle.add_to_principal_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["cloudformation:*"],
                resources=["*"]
            )
        )

        iam.Role(self, "deployment_role",
            assumed_by=principle,
            role_name=f"{github_org}-{github_repo}-deploy",
            max_session_duration=Duration.seconds(3600),
            inline_policies={
                "DeploymentPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=['sts:AssumeRole'],
                            resources=[f'arn:aws:iam::802288441694:role/cdk-*'],
                            effect=iam.Effect.ALLOW
                        ),
                        iam.PolicyStatement(
                            actions=['cloudformation:*'],
                            resources=['*'],
                            effect=iam.Effect.ALLOW
                        )
                    ]
                )
            },
        )

        CfnOutput(self, "DeploymentRoleArn", value=f"arn:aws:iam::982195495700:role/{github_org}-{github_repo}-deploy")