import resource
from cgitb import handler
from weakref import proxy

import aws_cdk as _cdk
from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_apigateway as _api
from aws_cdk import aws_certificatemanager as _cert
from aws_cdk import aws_dynamodb as _dynamodb
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as _log
from aws_cdk import aws_route53 as _route53
from constructs import Construct
from dotenv import dotenv_values


class LambdaApiDynamoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,  vpc_endpoint=_ec2.InterfaceVpcEndpoint,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        config = dotenv_values(".env")
        # Parameters from .env

        environment = config['ENV']
        first_name_last_name = config['FIRST_LAST_NAME']

        # DynamoDB Table

        table = _dynamodb.Table(self, 
                                "Table",
                                partition_key=_dynamodb.Attribute(name="id", 
                                type=_dynamodb.AttributeType.STRING),
                                table_name=f"{environment}-dynamotable-{first_name_last_name}-masterclass",
                            )

        
        # GET Method Lambda

        lambda_func_get = _lambda.Function(self, 
                                           'lambda_api_get_func',
                                           runtime=_lambda.Runtime.PYTHON_3_9,
                                           code=_lambda.AssetCode("./aws_final_project/Functions/LambdaGet"),
                                           handler='lambda_dynamo.lambda_handler',
                                           environment={
                                                "ddbtablename": f"{table.table_name}",
                                            },
                                    )

        # GET Method Lambda LG

        lambda_lg_get = _log.LogGroup(self, 
                                      "lambda_mm_loggroup_get",
                                      log_group_name=f"/aws/lambda/{lambda_func_get.function_name}",
                                      removal_policy=RemovalPolicy.DESTROY,
                                )


        # POST Method Lambda

        lambda_func_post = _lambda.Function(self, 
                                            'lambda_api_post_func',
                                            runtime=_lambda.Runtime.PYTHON_3_9,
                                            code=_lambda.AssetCode("./aws_final_project/Functions/LambdaPost"),
                                            handler='lambda_dynamo.lambda_handler',
                                            environment={
                                                "ddbtablename": f"{table.table_name}",
                                            },
                                    )

        

        # POST Method Lambda LG

        lambda_lg_post = _log.LogGroup(self, 
                                       "lambda_mm_loggroup_post",
                                       log_group_name=f"/aws/lambda/{lambda_func_post.function_name}",
                                       removal_policy=RemovalPolicy.DESTROY
                                )
        

        # Granting lambda permissions for DynamoDB

        table.grant_read_write_data(lambda_func_get)
        table.grant_read_write_data(lambda_func_post)



        # Api policy

        rest_api_policy = _iam.PolicyDocument(
            statements=[_iam.PolicyStatement(
                actions=["execute-api:Invoke"],
                principals=[_iam.AnyPrincipal()],
                resources=["arn:aws:execute-api:{0}:{1}:*/prod/GET/*".format(self.region, self.account),
                           "arn:aws:execute-api:{0}:{1}:*/prod/POST/*".format(self.region, self.account)
                           ],
                effect=_iam.Effect.ALLOW,
                )], 
                )



        # API Gateway

        api_gateway =_api.RestApi(self, 
                       "RestLambdaApi",
                       policy=rest_api_policy,
                       cloud_watch_role=True,
                       rest_api_name=f"{environment}-apigw-{first_name_last_name}",
                       description="Lambda backed API with GET and POST methods connected to dynamodb",
                       deploy_options=_api.StageOptions(
                        logging_level=_api.MethodLoggingLevel.INFO,
                        tracing_enabled=True,
                        data_trace_enabled=True,
                        stage_name="prod"
                        ),
                       endpoint_configuration=_api.EndpointConfiguration(
                            vpc_endpoints=[vpc_endpoint],
                            types=[_api.EndpointType.PRIVATE]
                            )                           
                       )
        
        log_group_api = _log.LogGroup(self,
                                        'LogsForApiGateway',
                                        log_group_name=f"/aws/api/{environment}-apigw-{first_name_last_name}",
                                        retention=_log.RetentionDays.FIVE_DAYS,
                                        removal_policy=RemovalPolicy.DESTROY
                                        )

        info = _api.MethodLoggingLevel.INFO

        deploy_options= _api.StageOptions(stage_name="prod", logging_level= info,
                                                                                 access_log_destination=_api.LogGroupLogDestination(log_group_api),
                                                                                 access_log_format= _api.AccessLogFormat.custom(f"{_api.AccessLogField.context_request_id()} {_api.AccessLogField.context_error_message()} {_api.AccessLogField.context_error_message_string()} {_api.AccessLogField.context_http_method()} {_api.AccessLogField.context_domain_name} {_api.AccessLogField.context_protocol()}")
                                                            )


        # Creating Resources for Gateway

        post = api_gateway.root.resource_for_path("/api/v1/masterclass")
        get = api_gateway.root.resource_for_path("/api/v1/masterclass")


        # Integrating LambdaIntegration

        get.add_method("GET", _api.LambdaIntegration(lambda_func_get , proxy=True)) # GET /items
        post.add_method("POST", _api.LambdaIntegration(lambda_func_post , proxy=True)) # POST /items


        CfnOutput(self, "apiid", value=api_gateway.rest_api_id, export_name=f"{environment}-apigateway-id-{first_name_last_name}")
