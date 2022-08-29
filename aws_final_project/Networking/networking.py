import aws_cdk as _cdk
from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_sns_subscriptions as subs
from aws_cdk import aws_ssm as _ssm
from constructs import Construct
from dotenv import dotenv_values


class NetworkingtStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        config = dotenv_values(".env")
        # Parameters from .env

        environment = config['ENV']
        first_name_last_name = config['FIRST_LAST_NAME']
        vpc_cidr = config['VPC_CIDR']
        cidr_mask = config['CIDR_MASK']

        
        # VPC
        
        custom_vpc = _ec2.Vpc(self,
                              "custom_vpc",
                              max_azs=3,
                              nat_gateways=0,
                              vpc_name=f"{environment}-vpc-{first_name_last_name}-custom_vpc",
                              cidr=vpc_cidr,
                              subnet_configuration=[
                                  _ec2.SubnetConfiguration(
                                      name="MMPublicSubnet",
                                      subnet_type=_ec2.SubnetType.PUBLIC,
                                      cidr_mask=int(cidr_mask) 
                                      ),
                                  _ec2.SubnetConfiguration(
                                      name="MMPrivateSubnet",
                                      subnet_type=_ec2.SubnetType.PRIVATE_ISOLATED,
                                      cidr_mask=int(cidr_mask)  
                                      )
                                  ],
                            )        
        
        # VPC Endpoint for API Gateway
        
        self.vpc_endpoint = _ec2.InterfaceVpcEndpoint(self,
                                                 "APIendpoint",
                                                 vpc=custom_vpc,
                                                 service=_ec2.InterfaceVpcEndpointAwsService.APIGATEWAY
                                            )

        

        # Exporting vpc_id and endpoint_id for later use

        vpcid = _ssm.StringParameter(self,
                                     'vpc_id',
                                     parameter_name= '/VpcProvider/markomandic/vpcid',
                                     string_value= custom_vpc.vpc_id
                                    )

        CfnOutput(self, "endpoint_id", value=self.vpc_endpoint.vpc_endpoint_id, export_name="dev-VpcEndpoint-markomandic-masterclass")

    