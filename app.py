#!/usr/bin/env python3

from platform import node
import aws_cdk as cdk
import os

from aws_final_project.Networking.networking import NetworkingtStack
from aws_final_project.LambdaApiDynamo.lambda_api_dynamo import LambdaApiDynamoStack
from aws_final_project.EcsCluster.ecs_cluster import EcsClusterStack
from aws_final_project.Pipeline.pipeline import PipelineStack
from dotenv import dotenv_values


config = dotenv_values(".env")
env_EU = cdk.Environment(account="802288441694", region="eu-west-1")


app = cdk.App()
networkingstack = NetworkingtStack(app, "networking-stack-mm", env=env_EU)
LambdaApiDynamoStack(app, "lambda-api-dynamo-stack-mm", networkingstack.vpc_endpoint ,env=env_EU)
PipelineStack(app, "pipeline-stack", env=env_EU)
EcsClusterStack(app, "ecs-cluster-stack-mm",env=env_EU)


app.synth()
