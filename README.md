
# Welcome to our CDK Python project!

## Levi9 DevOps Masterclass Final Project Marko Mandic

**![Architecure image](https://raw.githubusercontent.com/mandicm223/devops-mc-project/main/Screenshot%20from%202022-08-11%2010-04-59.png)**

Your final task will be to create automation from diagram on Ireland region (eu-west-1) and all resources have to be created with IaaC using CloudFormation in YAML format, AWS SAM or CDK with python library.
### Resources:

1. **VPC**: 
    - Three public subnets in each AZ
    - Three private subnets in each AZ
    - Without NAT Gateway 
    - Routing tables setup in order to match public/private subnets needs
    - NACL for private and private subnets

2. **DynamoDB Table**
    - Two Lambda Functions (Runtime: python3.9):
    - First lambda functions to write some data in DynamoDB
    - Secondary lambda functions to pull data from DynamoDB

3. **VPC Endpoint for Private API**:
    - Service: com.amazonaws.eu-west-1.execute-api

4. **API Gateway (REST API Private)**:
    - Start with initial path “/api/v1/”
    - API must have one POST method with first lambda integration and GET method with second lambda integration. For both methods use lambda proxy integration.
    - CloudWatch logging for API  

5. **ECR repository for storing docker image**:
    - Create a docker image that contains Swagger UI with swagger.json file where you described for your REST API. https://swagger.io/tools/swagger-ui.

6. **ECS cluster**:
    - Enable container insightsoCapacity providers should be Fargate and Fargate Spot

7. **Task Definition**:
    - Create task definition with your swagger docker image on Fargate
    - Use optimal computer capacity (Check allowed values for CPU and memory https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html) and be aware of port mapping.

8. **EcsService**:
    - Run service from your task definition on Fargate SpotoRun service on your VPC on private subnets
    - Service has to be behind ALB

9. **ACM**:
    - Request a public certificate for “*.${firstnamelastname}.levi9masterclass.com” and add DNS validation in Route 53 hosted zone levi9masterclass.com

10. **ALB:oTwo listeners http and httpsoCreate redirections from http to https**
    - Create two target groupsfor REST API and EscService on https listener.
    - Configure listener rules for https listener. The default rule should forward traffic EscService target group, for second rule specify URL path for api traffic“/api/*” to forward the traffic on REST API target group (Use vpc endpoint IP addresses).

11. **Route53**:
    - Create Route 53 record api.${firstnamelastname}.levi9masterclass.comfor your ALB in hosted zone levi9masterclass.com

**Set up a continuous integration and continuous delivery (CI/CD) pipeline for deployingfinal task on AWS environment using the AWS tools such as CodeCommt, CodePipeline and CodeBulid.**

### Use the following naming convention for your resource names:

12. **${Environment}-${ResourceNameShort} -${FirstNameLastName}-${description}** 
    - Note: for Environment name use “dev”

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

