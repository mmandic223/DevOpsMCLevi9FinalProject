import re

from aws_cdk import Duration, Stack
from aws_cdk import aws_codebuild as _codebuild
from aws_cdk import aws_codecommit as _codecommit
from aws_cdk import aws_codepipeline as _codepipeline
from aws_cdk import aws_codepipeline_actions as _actions
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subs
from aws_cdk import aws_sqs as sqs
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct
from datetime import datetime
from dotenv import dotenv_values
from aws_cdk import aws_events_targets as _targets


class PipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Parameters from .env
        
        config = dotenv_values(".env")
        

        environment = config['ENV']
        first_name_last_name = config['FIRST_LAST_NAME']

        
        # Initialazing CodeCommit Repo
        
        repo = _codecommit.Repository(self, "mm-repo",
                                      repository_name=f"{environment}-{first_name_last_name}-masterclass-repo",
                                      description="Najjaci repo na svetu",
                                    )

        # Build project for Docker BuildPhase
        
        # project_docker_dev = _codebuild.Project(self,
        #                                     "code-build-mm-project-docker-dev",
        #                                     build_spec=_codebuild.BuildSpec.from_source_filename('aws_final_project/Codebuild/buildspecdev.yaml'),
        #                                     environment=_codebuild.BuildEnvironment(
        #                                        build_image=_codebuild.LinuxBuildImage.STANDARD_5_0,
        #                                        compute_type=_codebuild.ComputeType.SMALL,
        #                                        privileged=True
        #                                     ),
        #                                     source=_codebuild.Source.code_commit(
        #                                        repository=repo,
        #                                        branch_or_ref="refs/heads/devel"
        #                                     ),
        #                                 )


        # project_docker_dev.role.add_to_principal_policy(_iam.PolicyStatement(
        #     actions=[   "cloudformation:Describe*",
        #                 "ec2:Describe*",
        #                 "cloudformation:CreateStack",
        #                 "cloudformation:CreateChangeSet",
        #                 "cloudformation:DeleteChangeSet",
        #                 "cloudformation:DeleteStack",
        #                 "cloudformation:ExecuteChangeSet",
        #                 "cloudformation:UpdateStack",
        #                 "cloudformation:SetStackPolicy",
        #                 "cloudformation:ValidateTemplate",
        #                 "cloudformation:GetTemplate",
        #                 "cloudformation:DeleteChangeSet"],
        #     effect=_iam.Effect.ALLOW,
        #     resources=["*"]
        # ))

        
        # # Other Permissions

        # project_docker_dev.role.add_to_principal_policy(_iam.PolicyStatement(
        #     actions=["sts:Assumerole"],
        #     effect=_iam.Effect.ALLOW,
        #     resources=["*"]
        # ))

        # project_docker_dev.role.add_to_principal_policy(_iam.PolicyStatement(
        #     actions=["ecr:*"],
        #     effect=_iam.Effect.ALLOW,
        #     resources=["*"]
        # ))
        
        # # project_deploy.role.add_to_principal_policy(_iam.PolicyStatement(
        # #     actions=["sts:Assumerole"],
        # #     effect=_iam.Effect.ALLOW,
        # #     resources=["*"]
        # # ))


        # # Initializing Artifacts
        
        # sourceOutput_dev = _codepipeline.Artifact()

        
        # # Initializing Pipeline

        # pipeline_dev = _codepipeline.Pipeline(self,
        #                                   "markomandic-pipeline-dev",
        #                                   )

        
        # # Describing Pipeline

        # action1_dev = _actions.CodeCommitSourceAction(
        #         action_name="codecommit-action-dev",
        #         repository=repo,
        #         output=sourceOutput_dev
        #     )

        # action2_dev = _actions.CodeBuildAction(
        #         action_name="codebuilddocker-action-dev",
        #         input=sourceOutput_dev,
        #         project=project_docker_dev
        #     )

        # pipeline_dev.add_stage(
        #     stage_name="CodeCommitSource-dev",
        #     actions=[action1_dev]
        # )

        # pipeline_dev.add_stage(
        #     stage_name="Docker-dev",
        #     actions=[action2_dev]
        # )

        # ###########################################################################################################################################################3
    
        # Build project for Docker BuildPhase
        
        project_docker = _codebuild.Project(self,
                                            "code-build-mm-project-docker",
                                            build_spec=_codebuild.BuildSpec.from_source_filename('aws_final_project/Codebuild/buildspecprod.yaml'),
                                            environment=_codebuild.BuildEnvironment(
                                               build_image=_codebuild.LinuxBuildImage.STANDARD_5_0,
                                               compute_type=_codebuild.ComputeType.SMALL,
                                               privileged=True
                                            ),
                                            source=_codebuild.Source.code_commit(
                                               repository=repo,
                                               branch_or_ref="refs/heads/master"
                                            ),
                                        )


        # Initializing Artifacts
        
        sourceOutput = _codepipeline.Artifact()

        
        # Initializing Pipeline

        pipeline = _codepipeline.Pipeline(self,
                                          "markomandic-pipeline",
                                          )

        
        # Describing Pipeline

        action1 = _actions.CodeCommitSourceAction(
                action_name="codecommit-action",
                repository=repo,
                output=sourceOutput
            )

        action2 = _actions.CodeBuildAction(
                action_name="codebuilddocker-action",
                input=sourceOutput,
                project=project_docker
            )

        # action3 = _actions.CodeBuildAction(
        #         action_name="codebuild-deploy-action",
        #         input=sourceOutput,
        #         project=project_deploy
        #     )

        pipeline.add_stage(
            stage_name="CodeCommitSource",
            actions=[action1]
        )

        pipeline.add_stage(
            stage_name="Docker",
            actions=[action2]
        )

        # pipeline.add_stage(
        #     stage_name="Deploy",
        #     actions=[action3]
        # )

        # pipeline.add_to_role_policy(_iam.PolicyStatement(
        #     principals=[_iam.ServicePrincipal('events.amazonaws.com')],
        #     actions=["sts:Assumerole"],
        #     effect=_iam.Effect.ALLOW,
        #     resources=["*"]
        # ))

        # pipeline.add_to_role_policy(_iam.PolicyStatement(
        #     principals=[_iam.ServicePrincipal('events.amazonaws.com')],
        #     actions=["codepipeline:StartPipelineExecution"],
        #     effect=_iam.Effect.ALLOW,
        #     resources=["*"]
        # ))

        # repo.on_pull_request_state_change("On PR change", target=_targets.CodePipeline(pipeline))

