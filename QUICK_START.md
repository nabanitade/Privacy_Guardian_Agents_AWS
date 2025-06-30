# 🚀 Privacy Guardian Agents - Quick Start Guide

## Overview

Privacy Guardian Agents is a multi-agent privacy enforcement system built with AWS Lambda for the AWS Lambda Hackathon. This guide will help you deploy and run the system locally or in the cloud with comprehensive AWS integration.

## Prerequisites

- Python 3.8+
- Node.js 18+
- AWS CLI installed and configured
- AWS SAM CLI installed
- AWS account with appropriate permissions
- AWS Bedrock access (for Claude 3.7 Sonnet)

## 🏠 Local Development (Recommended for Testing)

### 1. Setup Local Environment

```bash
# Clone the repository
git clone <repository-url>
cd Privacy_Guardian_Agents-aws

# Install Node.js dependencies
npm install

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set your AWS region
export AWS_DEFAULT_REGION="us-east-1"

# Setup local development environment
./deploy_aws.sh development
```

### 2. Configure Environment Variables

Edit the `.env` file created in the previous step:

```bash
# AWS Configuration
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# AWS Bedrock Configuration (Claude 3.7 Sonnet)
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v1:0
BEDROCK_MAX_TOKENS=2000
BEDROCK_TEMPERATURE=0.1

# AWS Services Configuration
S3_BUCKET_NAME=privacy-guardian-reports
DYNAMODB_TABLE_NAME=privacy_guardian_scan_results

# Application Configuration
LOG_LEVEL=INFO
WEB_SERVER_PORT=8080
```

### 3. AWS Authentication

```bash
# Configure AWS CLI
aws configure

# Set your AWS region
aws configure set region us-east-1

# Verify AWS credentials
aws sts get-caller-identity
```

### 4. Run Locally

```bash
# Test the system
python agent_orchestrator.py --project-path tests/java/

# Start the web server
python web_server.py
```

The application will be available at `http://localhost:8080`

## ☁️ AWS Deployment

### Option 1: AWS Lambda (Recommended for Production)

```bash
# Deploy to AWS Lambda
./deploy_aws.sh production
```

This will:
- Create AWS Lambda functions for each agent
- Setup API Gateway with REST endpoints
- Create S3 bucket for report storage
- Setup DynamoDB table for analytics
- Configure EventBridge for agent communication
- Setup CloudWatch for monitoring
- Provide you with API endpoints

### Option 2: Local Testing with SAM CLI

```bash
# Test locally with SAM CLI
sam local invoke AgentOrchestratorFunction --event events/test-event.json

# Start local API Gateway
sam local start-api
```

### Option 3: Setup AWS Resources Only

```bash
# Setup AWS resources without deployment
./deploy_aws.sh setup
```

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

### 1. Install Dependencies

```bash
# Node.js dependencies
npm install

# Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup AWS

```bash
# Install AWS CLI
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

# Configure AWS
aws configure

# Set region
aws configure set region us-east-1

# Verify setup
aws sts get-caller-identity
```

### 3. Create DynamoDB Table

```bash
# Create DynamoDB table
aws dynamodb create-table \
    --table-name privacy_guardian_scan_results \
    --attribute-definitions AttributeName=scan_id,AttributeType=S \
    --key-schema AttributeName=scan_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

### 4. Create S3 Bucket

```bash
# Create S3 bucket
aws s3 mb s3://privacy-guardian-reports --region us-east-1

# Set bucket permissions
aws s3api put-bucket-encryption \
    --bucket privacy-guardian-reports \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'

# Create folder structure
aws s3 mkdir s3://privacy-guardian-reports/reports
aws s3 mkdir s3://privacy-guardian-reports/logs
aws s3 mkdir s3://privacy-guardian-reports/artifacts
```

### 5. Setup AWS Secrets Manager

```bash
# Create secrets
aws secretsmanager create-secret \
    --name privacy-guardian-bedrock-key \
    --description "AWS Bedrock API Key for Privacy Guardian Agents" \
    --secret-string "your-bedrock-api-key"

# Grant access to Lambda functions
aws secretsmanager put-resource-policy \
    --secret-id privacy-guardian-bedrock-key \
    --resource-policy '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "secretsmanager:GetSecretValue",
                "Resource": "*"
            }
        ]
    }'
```

### 6. Setup EventBridge (Optional)

```bash
# Create EventBridge bus
aws events create-event-bus --name privacy-guardian-events

# Create rules for agent communication
aws events put-rule \
    --name privacy-scan-events \
    --event-bus-name privacy-guardian-events \
    --event-pattern '{"source": ["privacy.guardian.agents"]}'
```

### 7. Set Environment Variables

```bash
export AWS_DEFAULT_REGION="us-east-1"
export S3_BUCKET_NAME="privacy-guardian-reports"
export DYNAMODB_TABLE_NAME="privacy_guardian_scan_results"
export BEDROCK_MODEL="anthropic.claude-3-5-sonnet-20241022-v1:0"
export BEDROCK_MAX_TOKENS="2000"
export BEDROCK_TEMPERATURE="0.1"
```

### 8. Run the Application

```bash
# Test the orchestrator
python agent_orchestrator.py --project-path tests/java/

# Test individual agent
python lambda_functions/privacy_scan_agent.py tests/java/ --verbose

# Run web server
python web_server.py

# Or run orchestrator directly
python agent_orchestrator.py --project-path ./your-codebase
```

## 🎯 Usage Examples

### Web Interface

1. Open `http://localhost:8080` (local) or your API Gateway URL
2. Upload a codebase or provide a project path
3. Click "Start Scan" to begin privacy analysis
4. View real-time results and download reports

### Command Line

```bash
# Scan a specific project
python agent_orchestrator.py --project-path ./my-app

# Scan with specific options
python agent_orchestrator.py \
  --project-path ./my-app \
  --disable-ai \
  --agent-status

# Test individual agent
python lambda_functions/privacy_scan_agent.py ./my-app --verbose

# Check agent status
python agent_orchestrator.py --agent-status
```

### API Usage

```bash
# Start a scan
curl -X POST "http://localhost:8080/api/scan" \
  -H "Content-Type: application/json" \
  -d '{"project_path": "./my-app"}'

# Get scan status
curl "http://localhost:8080/api/status/SCAN_ID"

# Download report
curl "http://localhost:8080/api/report/SCAN_ID" --output report.pdf

# Check agent status
curl "http://localhost:8080/api/agents/status"
```

## 📊 Monitoring and Analytics

### DynamoDB Analytics

After running scans, you can query analytics in DynamoDB:

```bash
# View scan results
aws dynamodb scan \
    --table-name privacy_guardian_scan_results \
    --filter-expression "begins_with(scan_id, :prefix)" \
    --expression-attribute-values '{":prefix": {"S": "scan-"}}'

# Query specific scan
aws dynamodb get-item \
    --table-name privacy_guardian_scan_results \
    --key '{"scan_id": {"S": "scan-123"}}'
```

### CloudWatch Monitoring

View custom metrics in AWS CloudWatch:

```bash
# View Lambda function metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Duration \
    --dimensions Name=FunctionName,Value=agent-orchestrator-development \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 3600 \
    --statistics Average

# View custom metrics
aws cloudwatch list-metrics \
    --namespace PrivacyGuardian/Agents
```

### CloudWatch Logs

View structured logs:

```bash
# View application logs
aws logs filter-log-events \
    --log-group-name /aws/lambda/agent-orchestrator-development \
    --start-time 1640995200000

# View specific agent logs
aws logs filter-log-events \
    --log-group-name /aws/lambda/privacy-scan-agent-development \
    --filter-pattern "PrivacyScanAgent"

# View AWS Bedrock logs
aws logs filter-log-events \
    --log-group-name /aws/lambda/bedrock-analysis-agent-development \
    --filter-pattern "bedrock"
```

### AWS Bedrock Monitoring

```bash
# Check Bedrock model availability
aws bedrock list-foundation-models \
    --region us-east-1 \
    --query 'modelSummaries[?contains(modelId, `claude`)]'

# Check Bedrock usage
aws bedrock list-model-invocation-logs \
    --region us-east-1
```

## 🔐 Security and Secrets

### Secrets Manager

Store sensitive configuration in AWS Secrets Manager:

```bash
# Create secrets
aws secretsmanager create-secret \
    --name privacy-guardian-bedrock-key \
    --description "AWS Bedrock API Key" \
    --secret-string "your-api-key"

# Access in code
secret = self.fetch_secret("privacy-guardian-bedrock-key")
```

### IAM Permissions

Ensure your Lambda functions have these roles:
- `AWSLambdaBasicExecutionRole` (for CloudWatch Logs)
- `AmazonS3ReadWriteAccess` (for S3 report storage)
- `AmazonDynamoDBFullAccess` (for DynamoDB analytics)
- `AmazonBedrockFullAccess` (for Bedrock AI)
- `AmazonEventBridgeFullAccess` (for event communication)

### Service Account Setup

```bash
# Create IAM role for Lambda
aws iam create-role \
    --role-name PrivacyGuardianLambdaRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'

# Attach policies
aws iam attach-role-policy \
    --role-name PrivacyGuardianLambdaRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
    --role-name PrivacyGuardianLambdaRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadWriteAccess

aws iam attach-role-policy \
    --role-name PrivacyGuardianLambdaRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy \
    --role-name PrivacyGuardianLambdaRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

## 🚨 Troubleshooting

### Common Issues

1. **AWS Bedrock not available**
   - Check your IAM permissions have `AmazonBedrockFullAccess`
   - Verify billing is enabled on your AWS account
   - Check API quotas in AWS Console
   - Verify `AWS_DEFAULT_REGION` is set correctly

2. **DynamoDB permissions error**
   - Ensure your Lambda role has DynamoDB permissions
   - Check that the table exists: `aws dynamodb describe-table --table-name privacy_guardian_scan_results`
   - Verify table schema and indexes

3. **S3 access denied**
   - Verify bucket exists: `aws s3 ls s3://privacy-guardian-reports`
   - Check IAM permissions on the bucket
   - Ensure Lambda role has S3 permissions

4. **Agent communication issues**
   - Check that all Lambda functions are deployed
   - Verify event flow in CloudWatch logs
   - Ensure correlation IDs are being passed correctly
   - Check EventBridge rules and targets

5. **TypeScript RuleEngine import error**
   - Ensure Node.js dependencies are installed: `npm install`
   - Check if `rule_engine_cli.js` exists: `ls -la rule_engine_cli.js`
   - Verify Node.js version is 18+

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python web_server.py
```

### Health Check

Check agent status:

```bash
# Check all agents
python agent_orchestrator.py --agent-status

# Check specific agent
curl "http://localhost:8080/api/agents/status"

# Check event history
python agent_orchestrator.py --event-history CORRELATION_ID
```

### Performance Monitoring

```bash
# Monitor Lambda performance
aws lambda get-function-configuration \
    --function-name agent-orchestrator-development

# Check CloudWatch metrics for memory issues
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Duration \
    --dimensions Name=FunctionName,Value=agent-orchestrator-development \
    --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average

# View custom metrics
aws cloudwatch list-metrics \
    --namespace PrivacyGuardian/Agents
```

## 📈 Scaling and Performance

### Local Development
- Single instance, suitable for testing
- Limited by local resources
- TypeScript RuleEngine runs via Node.js bridge

### AWS Lambda
- Auto-scales based on demand
- Configure memory and timeout limits
- Set max instances for cost control
- Supports concurrent scans

### Performance Optimization
- Use `anthropic.claude-3-5-sonnet-20241022-v1:0` for faster AI responses
- Configure appropriate token limits
- Monitor DynamoDB query performance
- Use S3 for report caching

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
name: Deploy Privacy Guardian
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - run: |
          sam build
          sam deploy --guided
```

### GitLab CI

```yaml
deploy:
  stage: deploy
  script:
    - aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
    - aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
    - aws configure set region us-east-1
    - sam build
    - sam deploy --guided
```

### AWS CodeBuild

```yaml
# buildspec.yml
version: 0.2
phases:
  build:
    commands:
      - sam build
      - sam deploy --guided
```

## 📞 Support

- **Documentation**: See `README.md`, `ARCHITECTURE_DIAGRAM.md`, and `DEPLOYMENT.md`
- **Issues**: Create an issue in the repository
- **Blog Post**: See `BLOG_POST.md` for technical details
- **AWS Bedrock Documentation**: For Bedrock-specific issues

## 🎉 Next Steps

1. **Customize Rules**: Add your own privacy rules in `src/ruleEngine/rules/`
2. **Extend Agents**: Create new agents by inheriting from `BaseAgent`
3. **Integrate CI/CD**: Add privacy scanning to your development pipeline
4. **Monitor Analytics**: Set up CloudWatch dashboards for privacy trends
5. **Scale Up**: Deploy to production with AWS Lambda
6. **Security Hardening**: Implement additional security measures
7. **Contribute**: Submit PRs to improve the system

---

**Happy Privacy Scanning! 🔒✨** 