from aws_cdk import (
    Duration,
    CfnOutput,
    aws_iam as _iam,
    App,
)
from aws_cdk import Duration, RemovalPolicy, Stack
from constructs import Construct
from dotenv import dotenv_values

class GithubConnection(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        config = dotenv_values(".env")
        # Parameters from .env

        github_org = config['GITHUB_ORG']
        github_repo = config['GITHUB_REPO']
        environment = config['ENV']
        first_name_last_name = config['FIRST_LAST_NAME']


        github_provider = _iam.OpenIdConnectProvider(self , 
                                                    "f{environment}-ghprovider-{first_name_last_name}-masterclass",
                                                    url="https://token.actions.githubusercontent.com",
                                                    client_ids=["sts.amazonaws.com"]    
                                                )

        principle = _iam.OpenIdConnectPrincipal(github_provider).with_conditions(
            conditions={
                "StringLike": {
                    'token.actions.githubusercontent.com:sub':
                        f'repo:{github_org}/{github_repo}:*'
                }
            }
        )

        principle.add_to_principal_policy(
            _iam.PolicyStatement(
                effect=_iam.Effect.ALLOW,
                actions=["sts:AssumeRoleWithWebIdentity"],
                resources=["*"]
            )
        )

        principle.add_to_principal_policy(
            _iam.PolicyStatement(
                effect=_iam.Effect.ALLOW,
                actions=["cloudformation:*"],
                resources=["*"]
            )
        )

        principle.add_to_principal_policy(
            _iam.PolicyStatement(
                effect=_iam.Effect.ALLOW,
                actions=["ec2:*"],
                resources=["*"]
            )
        )

        principle.add_to_principal_policy(
            _iam.PolicyStatement(
                effect=_iam.Effect.ALLOW,
                actions=["sts:*"],
                resources=["*"]
            )
        )

        principle.add_to_principal_policy(
            _iam.PolicyStatement(
                effect=_iam.Effect.ALLOW,
                actions=["ecr:*"],
                resources=["*"]
            )
        )

        _iam.Role(self, 
                 "f{environment}-deploymentrole-{first_name_last_name}-masterclass",
                  assumed_by=principle,
                  role_name=f"{github_org}-{github_repo}-deploy",
                  max_session_duration=Duration.seconds(3600),
                  inline_policies={
                      "DeploymentPolicy": _iam.PolicyDocument(
                          statements=[
                              _iam.PolicyStatement(
                                  actions=['sts:AssumeRole'],
                                  resources=[f'arn:aws:iam::802288441694:role/cdk-*'],
                                  effect=_iam.Effect.ALLOW
                              ),
                              _iam.PolicyStatement(
                                  actions=['cloudformation:*'],
                                  resources=['*'],
                                  effect=_iam.Effect.ALLOW
                              ),
                              _iam.PolicyStatement(
                                  actions=['ec2:*'],
                                  resources=['*'],
                                  effect=_iam.Effect.ALLOW
                              ),
                              _iam.PolicyStatement(
                                  actions=['sts:*'],
                                  resources=['*'],
                                  effect=_iam.Effect.ALLOW
                              ),
                              _iam.PolicyStatement(
                                  actions=['ecr:*'],
                                  resources=['*'],
                                  effect=_iam.Effect.ALLOW
                              )
                          ]
                      )
                  },
            )

        CfnOutput(self, "DeploymentRoleArn", value=f"arn:aws:iam::982195495700:role/{github_org}-{github_repo}-deploy")