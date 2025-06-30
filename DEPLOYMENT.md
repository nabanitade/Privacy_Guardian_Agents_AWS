# Privacy Guardian Agents - Deployment Guide

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [AWS Deployment](#aws-deployment)
- [Testing](#testing)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)
- [Security Considerations](#security-considerations)

## Overview

Privacy Guardian Agents is a multi-agent privacy enforcement system built for the AWS Lambda Hackathon. This guide covers deployment options for local development and AWS cloud environments with comprehensive AWS integration.

## Prerequisites

### Required Software
- Python 3.9+
- Node.js 18+
- Docker (for containerized deployment)
- AWS CLI
- AWS SAM CLI

### Required AWS Services
- AWS Account with billing enabled
- AWS Bedrock (for Claude 3.7 Sonnet)
- AWS Lambda
- Amazon S3
- Amazon DynamoDB
- AWS API Gateway
- AWS EventBridge
- Amazon CloudWatch
- AWS Secrets Manager
- AWS IAM
- AWS Step Functions
- AWS CloudFormation
- AWS CloudTrail
- AWS GuardDuty
- AWS Config
- AWS Systems Manager
- Amazon CloudFront
- Amazon Route 53
- Amazon SQS
- Amazon SNS

## Environment Setup

### 1. Clone and Setup Repository
```bash
git clone <repository-url>
cd Privacy_Guardian_Agents-aws
```

### 2. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install
```

### 3. AWS Authentication
```bash
# Authenticate with AWS
aws configure

# Verify authentication
aws sts get-caller-identity
```

### 4. Environment Variables
Create a `.env` file in the project root:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Bedrock AI Configuration
BEDROCK_MODEL=anthropic.claude-3-7-sonnet-20250219-v1:0
BEDROCK_MAX_TOKENS=2000
BEDROCK_TEMPERATURE=0.1

# S3 Configuration
S3_BUCKET_NAME=privacy-guardian-reports
STORAGE_REGION=us-east-1

# DynamoDB Configuration
DYNAMODB_TABLE=privacy_scan_results

# Secret Manager Configuration
SECRET_NAME=privacy-guardian-secrets

# CloudWatch Configuration
CLOUDWATCH_NAMESPACE=PrivacyGuardian

# Application Configuration
LOG_LEVEL=INFO
WEB_SERVER_PORT=8080
ENVIRONMENT=development
```

## Local Development

### 1. Start Local Development Server
```bash
# Start the web server
python web_server.py

# Or use the deployment script
./deploy.sh local
```

### 2. Run Privacy Scan
```bash
# Using the orchestrator (recommended)
source venv/bin/activate
python agent_orchestrator.py --project-path tests/java/

# Using individual agent CLI
python agents/privacy_scan_agent.py tests/java/ --verbose

# Using Python directly
python -c "
from agents.privacy_scan_agent import PrivacyScanAgent
from agents.bedrock_analysis_agent import BedrockAnalysisAgent
from agents.compliance_agent import ComplianceAgent
from agents.fix_suggestion_agent import FixSuggestionAgent
from agents.report_agent import ReportAgent

# Initialize agents
privacy_agent = PrivacyScanAgent()
bedrock_agent = BedrockAnalysisAgent()
compliance_agent = ComplianceAgent()
fix_agent = FixSuggestionAgent()
report_agent = ReportAgent()

# Run scan
result = privacy_agent.scan_codebase('tests/')
print(result)
"

# Using the test script
python test_deployment.py
```

### 3. Access Web Interface
Open your browser and navigate to `http://localhost:8080`

## AWS Deployment

### Option 1: SAM Deployment (Recommended)

#### 1. Build and Deploy
```bash
# Use the deployment script
./deploy.sh deploy

# Or manually:
# Build TypeScript RuleEngine
cd lambda_functions
./build_rule_engine.sh
cd ..

# Build and deploy with SAM
sam build
sam deploy --guided
```

#### 2. Access Deployed Service
The deployment script will output the API Gateway URL. You can also find it in the AWS Console under API Gateway.

### Option 2: Manual Lambda Deployment

#### 1. Deploy Functions
```bash
# Use the deployment script
./deploy.sh deploy

# Or manually deploy each function:
aws lambda create-function \
  --function-name agent-orchestrator-development \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --handler agent_orchestrator.lambda_handler \
  --zip-file fileb://lambda_functions.zip \
  --region us-east-1

aws lambda create-function \
  --function-name rule-engine-bridge-development \
  --runtime nodejs18.x \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --handler rule_engine_bridge.handler \
  --zip-file fileb://lambda_functions.zip \
  --region us-east-1
```

#### 2. Test Functions
```bash
# Test agent orchestrator
aws lambda invoke --function-name agent-orchestrator-development \
  --cli-binary-format raw-in-base64-out \
  --payload '{"source_code":"test code","scan_id":"test-001"}' \
  response.json

# Test rule engine bridge
aws lambda invoke --function-name rule-engine-bridge-development \
  --cli-binary-format raw-in-base64-out \
  --payload '{"source_code":"test code","file_type":"java"}' \
  bridge-response.json
```

### Option 3: ECS Deployment

#### 1. Create ECS Cluster
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name privacy-guardian-cluster

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### 2. Deploy to ECS
```bash
# Create service
aws ecs create-service \
  --cluster privacy-guardian-cluster \
  --service-name privacy-guardian-service \
  --task-definition privacy-guardian:1 \
  --desired-count 2
```

## Resource Setup

### 1. DynamoDB Setup
```bash
# Create DynamoDB table
aws dynamodb create-table \
  --table-name privacy-scan-results \
  --attribute-definitions AttributeName=scan_id,AttributeType=S \
  --key-schema AttributeName=scan_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Create GSI for violation tracking
aws dynamodb update-table \
  --table-name privacy-scan-results \
  --attribute-definitions AttributeName=violation_type,AttributeType=S \
  --global-secondary-index-updates \
    "[{\"Create\":{\"IndexName\":\"violation-type-index\",\"KeySchema\":[{\"AttributeName\":\"violation_type\",\"KeyType\":\"HASH\"}],\"Projection\":{\"ProjectionType\":\"ALL\"}}}]" \
  --region us-east-1
```

### 2. S3 Setup
```bash
# Create storage bucket
aws s3 mb s3://privacy-guardian-reports --region us-east-1

# Set bucket permissions
aws s3api put-bucket-policy --bucket privacy-guardian-reports --policy file://bucket-policy.json

# Create folder structure
aws s3 mkdir s3://privacy-guardian-reports/reports
aws s3 mkdir s3://privacy-guardian-reports/logs
aws s3 mkdir s3://privacy-guardian-reports/artifacts
```

### 3. Secrets Manager Setup
```bash
# Create secrets
aws secretsmanager create-secret \
  --name privacy-guardian-bedrock-key \
  --description "AWS Bedrock API key for Privacy Guardian Agents" \
  --secret-string "your-bedrock-api-key"

# Grant access to Lambda role
aws secretsmanager put-resource-policy \
  --secret-id privacy-guardian-bedrock-key \
  --resource-policy file://secret-policy.json
```

### 4. CloudWatch Setup
```bash
# Create custom metrics namespace
aws cloudwatch put-metric-data \
  --namespace "PrivacyGuardian" \
  --metric-data MetricName=Violations,Value=0,Unit=Count

# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "PrivacyGuardianDashboard" \
  --dashboard-body file://cloudwatch-dashboard.json
```

### 5. IAM Setup
```bash
# Create Lambda execution role
aws iam create-role \
  --role-name privacy-guardian-lambda-role \
  --assume-role-policy-document file://lambda-trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name privacy-guardian-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name privacy-guardian-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name privacy-guardian-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy \
  --role-name privacy-guardian-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

### 6. EventBridge Setup
```bash
# Create event bus for agent communication
aws events create-event-bus --name privacy-guardian-events

# Create rules for agent communication
aws events put-rule \
  --name privacy-scan-events \
  --event-bus-name privacy-guardian-events \
  --event-pattern file://event-pattern.json

# Create targets for rules
aws events put-targets \
  --rule privacy-scan-events \
  --event-bus-name privacy-guardian-events \
  --targets file://targets.json
```

## Testing

### 1. Run Test Suite
```bash
# Python tests
python -m pytest tests/

# TypeScript tests
npm test

# Integration tests
python test_deployment.py

# Agent-specific tests
python agents/privacy_scan_agent.py tests/java/ --verbose
```

### 2. Manual Testing
```bash
# Test privacy scan
curl -X POST http://localhost:8080/scan \
  -H "Content-Type: application/json" \
  -d '{"path": "tests/", "languages": ["python", "javascript"]}'

# Test specific agent
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"violations": [{"type": "pii", "severity": "high"}]}'

# Test orchestrator
python agent_orchestrator.py --project-path tests/java/ --agent-status
```

### 3. AWS Testing
```bash
# Test deployed Lambda function
aws lambda invoke --function-name agent-orchestrator-development \
  --cli-binary-format raw-in-base64-out \
  --payload '{"source_code":"public class TestClass {\n    private String email = \"test@example.com\";\n    private String apiKey = \"sk-1234567890abcdef\";\n    private String ssn = \"123-45-6789\";\n    \n    public void processData() {\n        System.out.println(\"Processing data\");\n    }\n}","scan_id":"test-scan-001","project_path":"test.java"}' \
  response.json

# Test API Gateway endpoint
curl -X POST https://your-api-gateway-url/scan \
  -H "Content-Type: application/json" \
  -d '{"source_code":"test code","scan_id":"test-001"}'
```

### 4. Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 100 -c 10 -p test_payload.json -T application/json http://localhost:8080/scan
```

## Monitoring & Troubleshooting

### 1. CloudWatch Logs
```bash
# View application logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/agent-orchestrator"

# View specific agent logs
aws logs filter-log-events \
  --log-group-name "/aws/lambda/agent-orchestrator-development" \
  --filter-pattern "PrivacyScanAgent" \
  --start-time $(date -d '1 hour ago' +%s)000

# View Bedrock AI logs
aws logs filter-log-events \
  --log-group-name "/aws/lambda/bedrock-analysis-agent-development" \
  --filter-pattern "bedrock" \
  --start-time $(date -d '1 hour ago' +%s)000
```

### 2. CloudWatch Metrics
```bash
# View custom metrics
aws cloudwatch list-metrics --namespace "PrivacyGuardian"

# View Lambda metrics
aws cloudwatch list-metrics --namespace "AWS/Lambda"

# Create alerting policies
aws cloudwatch put-metric-alarm \
  --alarm-name "PrivacyViolationsHigh" \
  --alarm-description "High number of privacy violations detected" \
  --metric-name "Violations" \
  --namespace "PrivacyGuardian" \
  --statistic "Sum" \
  --period 300 \
  --threshold 10 \
  --comparison-operator "GreaterThanThreshold"
```

### 3. DynamoDB Analytics
```bash
# View scan results
aws dynamodb scan --table-name privacy-scan-results --limit 10

# Query by violation type
aws dynamodb query \
  --table-name privacy-scan-results \
  --index-name violation-type-index \
  --key-condition-expression "violation_type = :vt" \
  --expression-attribute-values '{":vt":{"S":"pii"}}'
```

### 4. Common Issues

#### Authentication Issues
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check IAM permissions
aws iam get-role --role-name privacy-guardian-lambda-role

# Check Bedrock permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::YOUR_ACCOUNT:role/privacy-guardian-lambda-role \
  --action-names bedrock:InvokeModel
```

#### API Quota Issues
```bash
# Check Lambda quotas
aws lambda get-account-settings

# Check Bedrock quotas
aws bedrock list-foundation-models

# Check DynamoDB quotas
aws dynamodb describe-limits
```

#### Memory Issues
```bash
# Monitor Lambda memory usage
aws cloudwatch get-metric-statistics \
  --namespace "AWS/Lambda" \
  --metric-name "Duration" \
  --dimensions Name=FunctionName,Value=agent-orchestrator-development \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

#### Bedrock AI Issues
```bash
# Check Bedrock model availability
aws bedrock list-foundation-models --region us-east-1

# Check Bedrock operations
aws bedrock list-model-invocation-logs --region us-east-1

# Verify model access
aws bedrock get-foundation-model --modelIdentifier anthropic.claude-3-7-sonnet-20250219-v1:0
```

## Security Considerations

### 1. IAM Security
- Use least privilege principle
- Rotate access keys regularly
- Use IAM roles for Lambda functions
- Grant minimal required permissions

### 2. Network Security
- Enable VPC for private resources
- Use security groups appropriately
- Configure firewall rules
- Use private subnets

### 3. Data Security
- Encrypt data at rest and in transit
- Use customer-managed encryption keys
- Implement proper access controls
- Enable audit logging for all services

### 4. Secret Management
- Store sensitive data in Secrets Manager
- Use environment variables for configuration
- Avoid hardcoding secrets in code
- Implement secret rotation

### 5. Bedrock Security
- Use IAM authentication
- Enable audit logging for AI operations
- Implement rate limiting
- Monitor AI usage and costs

## CI/CD Integration

### 1. GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS Lambda
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup AWS
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    - name: Deploy to Lambda
      run: |
        sam build
        sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
```

### 2. GitLab CI
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - python -m pytest tests/
    - npm test
    - python test_deployment.py

build:
  stage: build
  script:
    - sam build

deploy:
  stage: deploy
  script:
    - sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
```

### 3. AWS CodePipeline
```yaml
# buildspec.yml
version: 0.2
phases:
  install:
    runtime-versions:
      python: 3.9
      nodejs: 18
  pre_build:
    commands:
      - npm install
      - pip install -r requirements.txt
  build:
    commands:
      - sam build
  post_build:
    commands:
      - sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
```

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review CloudWatch logs for error messages
3. Consult the project documentation
4. Open an issue in the project repository
5. Check AWS Bedrock documentation for AI-specific issues

## License

This project is licensed under the MIT License - see the LICENSE file for details. 