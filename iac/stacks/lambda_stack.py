from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as actions,
    Duration,
    Tags,
    RemovalPolicy
)
from constructs import Construct

class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Tags for resource organization
        Tags.of(self).add("Project", "GuildHelloService")
        Tags.of(self).add("Environment", env_name)

        # SSM Parameter for greeting message (per config_examples.md)
        greeting_param = ssm.StringParameter(
            self, "GreetingParameter",
            parameter_name=f"/guild/hello-service/message",
            string_value=f"Hello from {env_name.title()}!",
            description=f"Greeting message for {env_name} environment"
        )

        # Lambda function (uses src/hello_app.py)
        lambda_function = _lambda.Function(
            self, "GuildHelloFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="hello_app.lambda_handler",
            code=_lambda.Code.from_asset("../src"),
            timeout=Duration.seconds(30),
            memory_size=128,  # Optimized for simple workload
            environment={
                "GREETING_MESSAGE": "Hello from Guild!",  # Fallback
                "SERVICE_VERSION": "1.0.0",
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": env_name
            }
        )

        # Grant IAM permissions (least privilege per operational_requirements.md)
        greeting_param.grant_read(lambda_function)
        lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[greeting_param.parameter_arn]
            )
        )
        lambda_function.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        # API Gateway for HTTP endpoint
        api = apigateway.RestApi(
            self, "GuildApi",
            rest_api_name=f"Guild Hello API - {env_name}",
            description=f"HTTP endpoint for Guild Hello service in {env_name}",
            deploy_options=apigateway.StageOptions(
                stage_name=env_name,
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,  # For observability
                throttling_burst_limit=100,
                throttling_rate_limit=50
            )
        )

        # Integrate Lambda with API Gateway
        integration = apigateway.LambdaIntegration(lambda_function)
        hello_resource = api.root.add_resource("hello")
        hello_resource.add_method("POST", integration)  # Matches handler's body parsing
        hello_resource.add_method("GET", integration)   # Flexible

        # AIOps Stretch: Provisioned Concurrency with autoscaling (~70% target)
        version = lambda_function.current_version
        alias = _lambda.Alias(self, "ProdAlias", version=version, alias_name="prod")
        alias.add_provisioned_concurrency(100)  # Min provisioned

        # Target-tracking scaling policy
        scaling = alias.auto_scale_provisioned_concurrency()
        scaling.scale_on_utilization(
            target_utilization_percent=70,
            scale_out_cooldown=Duration.seconds(300),  # 5min scale-out
            scale_in_cooldown=Duration.seconds(600)    # 10min scale-in
        )

        # Monitoring & Alarms
        error_alarm = lambda_function.metric_errors(
            period=Duration.minutes(1),
            threshold=5,  # >5 errors/min
            evaluation_periods=2
        ).create_alarm(
            self, "HighErrorRateAlarm",
            threshold=5,
            evaluation_periods=2,
            alarm_description="High Lambda error rate"
        )
        error_alarm.add_alarm_action(actions.EmsAction("arn:aws:sns:us-west-2:123456789012:GuildAlerts"))  # Placeholder SNS ARN; replace with Guild's alerting topic in prod

        # Latency alarm (warning)
        latency_alarm = lambda_function.metric_duration(
            statistic="p95",
            period=Duration.minutes(1),
            threshold=Duration.seconds(2000)  # >2s p95
        ).create_alarm(
            self, "HighLatencyAlarm",
            threshold=2000,
            evaluation_periods=1,
            alarm_description="High Lambda latency"
        )

        # Log retention (14 days for cost/debug balance)
        _lambda.LogGroup(
            self, "LambdaLogGroup",
            log_group_name=lambda_function.log_group.log_group_name,
            retention=Duration.days(14),
            removal_policy=RemovalPolicy.DESTROY  # For test env
        )

        # Outputs
        self.export_value(api.url, "ApiEndpoint")
        