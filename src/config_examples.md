# Configuration Guide for DevOps Deployment

This demonstrates basic configuration management patterns that your infrastructure should implement.

## SSM Parameter Store Configuration

The service uses AWS SSM Parameter Store for configuration management with environment variable fallbacks. This is a common DevOps pattern for managing configuration across environments.

### Required Parameters

Your Infrastructure as Code should create this SSM parameter:

```
/guild/hello-service/message
  Type: String  
  Description: The greeting message to display
  Example: "Hello from Production!"
  
Environment-specific examples:
  Dev: "Hello from Development!"
  Staging: "Hello from Staging!" 
  Production: "Hello from Production!"
```

## Environment Variable Fallbacks

When SSM parameters are unavailable, the service falls back to environment variables:

```bash
# Application Configuration (SSM fallback)
GREETING_MESSAGE="Hello from Guild!"

# Service Configuration
SERVICE_VERSION=1.0.0
LOG_LEVEL=INFO
ENVIRONMENT=dev
```

## DevOps Implementation Tasks

Your infrastructure deployment should handle:

1. **Create SSM Parameters**: Use your IaC tool to create environment-specific parameters
2. **Configure IAM Permissions**: Lambda execution role needs `ssm:GetParameter` access  
3. **Environment Variables**: Set fallback values via Lambda environment configuration
4. **Multi-Environment**: Support dev/staging/production with different parameter values

## Example Infrastructure Tasks

```bash
# Example parameter creation (your IaC should automate this)
aws ssm put-parameter \
  --name "/guild/hello-service/message" \
  --value "Hello from Development!" \
  --type "String"

# Production might use SecureString for sensitive data
aws ssm put-parameter \
  --name "/guild/hello-service/message" \
  --value "Hello from Production!" \
  --type "SecureString"
```

## Validation

The service logs configuration retrieval attempts:
- ✅ Successfully retrieved from SSM Parameter Store
- ⚠️ SSM parameter not found, using environment variable fallback
- ❌ Configuration failure (check IAM permissions)

Your deployment pipeline should verify configuration is working correctly.
