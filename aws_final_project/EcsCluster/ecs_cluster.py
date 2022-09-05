from importlib.resources import path

import aws_cdk
import aws_cdk as _cdk
import boto3
from aws_cdk import Duration, RemovalPolicy, Stack
from aws_cdk import aws_certificatemanager as _cert
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_ecr as _ecr
from aws_cdk import aws_ecs as _ecs
from aws_cdk import aws_ecs_patterns as _patterns
from aws_cdk import aws_elasticloadbalancingv2 as _elb
from aws_cdk import aws_elasticloadbalancingv2_targets as _targets
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_route53 as _route53
from aws_cdk import aws_route53_targets as _route53targets
from aws_cdk import aws_ssm as _ssm
from constructs import Construct
from dotenv import dotenv_values


class EcsClusterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        config = dotenv_values(".env")
        # Parameters from .env

        tag = config['TAG']
        environment = config['ENV']
        first_name_last_name = config['FIRST_LAST_NAME']
        
        # Initializing VPC
        
        vpc_id = _ssm.StringParameter.value_from_lookup(self,
                                                        parameter_name='/VpcProvider/markomandic/vpcid'
                                                      )
        
        custom_vpc = _ec2.Vpc.from_lookup(self,
                                          "f{environment}-customvpc-{first_name_last_name}-masterclass",
                                          vpc_id=vpc_id
                                        )


        # Zone and certificate setup

        zone = _route53.HostedZone.from_lookup(self,
                                                "f{environment}-hostedzone-{first_name_last_name}-masterclass",
                                                domain_name="levi9masterclass.com",
                                            )

        cert = _cert.Certificate(self,
                                "f{environment}-certificate-{first_name_last_name}-masterclass",
                                domain_name="*.markomandic.levi9masterclass.com",
                                validation=_cert.CertificateValidation.from_dns(zone)
                              )


        # Initializing ECS cluster

        cluster = _ecs.Cluster(self, 
                              "f{environment}-ecscluster-{first_name_last_name}-masterclass",
                              vpc=custom_vpc,
                              enable_fargate_capacity_providers=True,
                              container_insights=True
                            )


        # Importing predefined ECR repository

        ecr_repository = _ecr.Repository.from_repository_name(self,
                                                    "markomandicecrrepo",
                                                    "markomandicecrrepo"
                                                    )
                                                    
        ecr_repository.grant_pull(grantee = _iam.ServicePrincipal(service = '_ecs.amazonaws.com'))

        
        ip_addrs=[]
        cf_client = boto3.client('cloudformation')
        response = cf_client.describe_stacks()
        for stack in response['Stacks']:
            if stack['StackName'] == "networking-stack-mm":
                stack_created = True
                break
            else:
                stack_created = False
        if stack_created:
            response = cf_client.describe_stacks(StackName = "networking-stack-mm")          
        
            outputs = response['Stacks'][0]['Outputs']
            
            for output in outputs:
                    if output['ExportName'] == 'dev-VpcEndpoint-MArkoMandic-masterclass':
                        api_endpoint_id = output['OutputValue']
            ec2_client = boto3.client('ec2')
            
            response = ec2_client.describe_vpc_endpoints(
                VpcEndpointIds = [
                    api_endpoint_id
                ]
            )
            
            network_interface_ids = response['VpcEndpoints'][0]['NetworkInterfaceIds']
            response = ec2_client.describe_network_interfaces(
                NetworkInterfaceIds = network_interface_ids
            )
        
            for i in response['NetworkInterfaces']:
                ip_addrs.append(_targets.IpTarget(i['PrivateIpAddress']))


        
        # ALB and ECS Security Group

        lb_securitygroup = _ec2.SecurityGroup(self, 
                                    "f{environment}-albsg-{first_name_last_name}-masterclass",
                                    vpc=custom_vpc,
                                    allow_all_outbound=True
                                    )

        lb_securitygroup.add_ingress_rule(_ec2.Peer.any_ipv4(), _ec2.Port.tcp(443))

        ecs_securitygroup = _ec2.SecurityGroup(self,
                                    "f{environment}-ecssg-{first_name_last_name}-masterclass",
                                    vpc=custom_vpc,
                                    allow_all_outbound=True)
        ecs_securitygroup.connections.allow_from(lb_securitygroup, _ec2.Port.all_traffic())


        # ECS Service / LoadBalancer / TaskDefinition

        ecs_fargate_service = _patterns.ApplicationLoadBalancedFargateService(self,
                                                                              "f{environment}-fargateservice-{first_name_last_name}-masterclass",
                                                                              protocol=_elb.ApplicationProtocol.HTTPS,
                                                                              certificate=cert,
                                                                              redirect_http=True,
                                                                              platform_version=_ecs.FargatePlatformVersion.VERSION1_4,
                                                                              cluster=cluster,
                                                                              cpu=256,
                                                                              memory_limit_mib=512,
                                                                              desired_count=1,
                                                                              task_subnets=_ec2.SubnetSelection(
                                                                                subnet_type=_ec2.SubnetType.PUBLIC
                                                                              ),
                                                                              assign_public_ip=True,
                                                                              security_groups=[ecs_securitygroup],                                                                            
                                                                              task_image_options=_patterns.ApplicationLoadBalancedTaskImageOptions(
                                                                                image=_ecs.ContainerImage.from_registry(f"446835144354.dkr.ecr.eu-west-1.amazonaws.com/markomandicecrrepo:{tag}"),
                                                                                container_port=80,                                                                       
                                                                                log_driver=_ecs.AwsLogDriver(
                                                                                  stream_prefix="mm"
                                                                                )
                                                                              ),
                                                                              capacity_provider_strategies=[_ecs.CapacityProviderStrategy(
                                                                                capacity_provider="FARGATE_SPOT",
                                                                                weight=1,
                                                                              ),_ecs.CapacityProviderStrategy(
                                                                                capacity_provider="FARGATE",
                                                                                weight=2
                                                                              )
                                                                              ],
                                                                              public_load_balancer=True
                                                                            )



        ecs_fargate_service.load_balancer.add_security_group(lb_securitygroup)
        
        ecs_fargate_service.task_definition.add_to_task_role_policy( _iam.PolicyStatement(
                 actions=["dynamodb:*"],
                 effect= _iam.Effect.ALLOW,
                 resources=["*"]
                )
        )


        api_target_group = ecs_fargate_service.listener.add_targets("f{environment}-apitg-{first_name_last_name}-masterclass", port=443,targets=ip_addrs,protocol=_elb.ApplicationProtocol.HTTPS, priority=2 ,conditions=[_elb.ListenerCondition.path_patterns(['/prod/api/*'])])
        
        # Granting ECS permissions for ECR

        ecs_fargate_service.task_definition.add_to_execution_role_policy(_iam.PolicyStatement(
                                resources=["*"],
                                actions= [
                                          "ecr:GetAuthorizationToken",
                                          "ecr:BatchCheckLayerAvailability",
                                          "ecr:GetDownloadUrlForLayer",
                                          "ecr:GetRepositoryPolicy",
                                          "ecr:DescribeRepositories",
                                          "ecr:ListImages",
                                          "ecr:DescribeImages",
                                          "ecr:BatchGetImage",
                                          "ecr:GetLifecyclePolicy",
                                          "ecr:GetLifecyclePolicyPreview",
                                          "ecr:ListTagsForResource",
                                          "ecr:DescribeImageScanFindings",
                                          "logs:CreateLogStream","logs:PutLogEvents"
                                        ],
                                ))
        api_target_group.configure_health_check(
            healthy_http_codes="403",
            healthy_threshold_count=5,
            interval=Duration.seconds(60),
            timeout=Duration.seconds(20),
            unhealthy_threshold_count=2,
            path="/api/v1/"
        )

        # ECS Health Check

        ecs_fargate_service.target_group.configure_health_check(
            healthy_http_codes="200,301,302",
            healthy_threshold_count=5,
            interval=Duration.seconds(60),
            timeout=Duration.seconds(20),
            unhealthy_threshold_count=2,
            path="/"
        )

        # Route53 A record
        
        _route53.ARecord(self,
                        "api.markomandic.levi9masterclass",
                         record_name="api.markomandic.levi9masterclass.com",
                         target=_route53.RecordTarget.from_alias(
                            _route53targets.LoadBalancerTarget(ecs_fargate_service.load_balancer),
                         ),
                         ttl=aws_cdk.Duration.seconds(300),
                         zone=zone)
