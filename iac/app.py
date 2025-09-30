#!/usr/bin/env python3
from aws_cdk import App
from stacks.lambda_stack import LambdaStack

app = App()

# Deploy to env based on context (test/stage/prod)
env_name = app.node.try_get_context("env") or "test"
LambdaStack(
    app, 
    f"GuildLambdaStack-{env_name.title()}",
    env={"region": "us-west-2"},
    env_name=env_name  # Passed to stack for config
)

app.synth()
