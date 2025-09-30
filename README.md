# Guild Lambda Deployment Pattern
Deploys a Lambda service (`src/hello_app.py`) handling GET/POST requests to `/hello` with configurable greetings, extensible across test/stage/prod in us-west-2.

## Features
- **Simple**: Modular CDK stack, minimal setup.
- **Operational**: SSM config, structured logs, CloudWatch alarms, 14-day retention.
- **Secure**: Least-privilege IAM, API throttling.
- **CI/CD**: GitHub Actions for test/lint/deploy/validation.
- **AIOps Bonus**: Provisioned Concurrency autoscaling (70% target).
- **Multi-Account**: CDK context for test/stage/prod.

## Prerequisites
- AWS account (us-west-2, test).
- Fork of https://github.com/GuildChallenges/devops-engineering-take-home.
- Python 3.9+, AWS CLI, Node.js (CDK), GitHub Actions.
- Secrets: `AWS_ROLE_ARN`, `AWS_ACCOUNT_ID_TEST`.

## Setup & Deploy
1. **Clone**:
```bash
   git clone https://github.com/kdahal/devops-engineering-take-home.git
   cd devops-engineering-take-home
```
## Install:
```bash
pip install -r src/requirements.txt
cd iac && pip install -r requirements.txt && npm install -g aws-cdk
```
## Deploy (Test):
```bash
cd iac
cdk bootstrap aws://<account-id>/us-west-2
cdk deploy --context env=test
```
## Test:
```bash
curl https://<api-url>/hello
curl -X POST https://<api-url>/hello -d '{"name": "Engineer"}' -H "Content-Type: application/json"
cd src && python -m pytest test_validation.py -v
```
## CI/CD
- **File**: .github/workflows/action.yml
- **Triggers**: Push/PR to main, manual dispatch.
- **Steps**: Checkout, setup Python/CDK, test (pytest), lint (black/flake8), security check, deploy, validate API.
- **Multi-Env**: Deploy to stage/prod: cd iac && cdk deploy --context env=stage or cdk deploy --context env=prod.

## Operational Features
- **Config**: SSM /guild/hello-service/message (env-specific); fallback env var.
- **Monitoring**: CloudWatch alarms (errors >5/min, latency >2s p95); structured logs.
- **Security**: IAM scoped to SSM read, Lambda basic execution; API data tracing.
- **Scaling**: Provisioned Concurrency alias, autoscaling (70% target, 300s/600s cooldowns).

## Extending
- **Stage/Prod**: Add stacks in app.py (e.g., LambdaStack(app, "Stage", env_name="stage")).
- **Enhancements**: X-Ray, canary deploys, Graviton2 runtime.
- **Cost**: Adjust Lambda memory/timeout.

## Trade-Offs
- **CDK**: AWS-native, Python-based for simplicity (vs. Terraform for multi-cloud).
- **Scope**: Core + AIOps in 2hrs; omits canary for simplicity.
- **Security**: OIDC for CI/CD; access keys as fallback.

Questions? [kumar.dahal@outlook.com]. Enjoy building! 🚀