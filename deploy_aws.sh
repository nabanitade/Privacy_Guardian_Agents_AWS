#!/bin/bash

# Privacy Guardian Agents - AWS Lambda Deployment Script
# AWS Lambda Hackathon Edition

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="privacy-guardian-agents"
ENVIRONMENT=${1:-development}
REGION=${AWS_REGION:-us-east-1}
BEDROCK_MODEL="anthropic.claude-3-5-sonnet-20241022-v1:0"
MAX_TOKENS=2000
TEMPERATURE=0.1

echo -e "${BLUE}🚀 Privacy Guardian Agents - AWS Lambda Deployment${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "Environment: ${GREEN}${ENVIRONMENT}${NC}"
echo -e "Region: ${GREEN}${REGION}${NC}"
echo -e "Stack Name: ${GREEN}${STACK_NAME}-${ENVIRONMENT}${NC}"
echo -e "Bedrock Model: ${GREEN}${BEDROCK_MODEL}${NC}"
echo ""

# Function to check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ AWS CLI found${NC}"
}

# Function to check if SAM CLI is installed
check_sam_cli() {
    if ! command -v sam &> /dev/null; then
        echo -e "${RED}❌ AWS SAM CLI is not installed. Please install it first.${NC}"
        echo -e "${YELLOW}Installation: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ AWS SAM CLI found${NC}"
}

# Function to check AWS credentials
check_aws_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS credentials not configured. Please run 'aws configure' first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ AWS credentials configured${NC}"
}

# Function to create S3 bucket for SAM artifacts
create_sam_bucket() {
    BUCKET_NAME="privacy-guardian-sam-${AWS_ACCOUNT_ID}-${ENVIRONMENT}"
    
    if ! aws s3 ls "s3://${BUCKET_NAME}" &> /dev/null; then
        echo -e "${BLUE}📦 Creating S3 bucket for SAM artifacts: ${BUCKET_NAME}${NC}"
        aws s3 mb "s3://${BUCKET_NAME}" --region "${REGION}"
        aws s3api put-bucket-versioning --bucket "${BUCKET_NAME}" --versioning-configuration Status=Enabled
        aws s3api put-bucket-encryption --bucket "${BUCKET_NAME}" --server-side-encryption-configuration '{
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }
            ]
        }'
        echo -e "${GREEN}✅ S3 bucket created${NC}"
    else
        echo -e "${GREEN}✅ S3 bucket already exists${NC}"
    fi
}

# Function to build Lambda functions
build_lambda_functions() {
    echo -e "${BLUE}🔨 Building Lambda functions...${NC}"
    
    # Create lambda_functions directory if it doesn't exist
    mkdir -p lambda_functions
    
    # Copy existing agent files to lambda_functions
    if [ -f "agents/privacy_scan_agent.py" ]; then
        cp agents/privacy_scan_agent.py lambda_functions/
    fi
    if [ -f "agents/gemini_analysis_agent.py" ]; then
        cp agents/gemini_analysis_agent.py lambda_functions/bedrock_analysis_agent.py
    fi
    if [ -f "agents/compliance_agent.py" ]; then
        cp agents/compliance_agent.py lambda_functions/
    fi
    if [ -f "agents/fix_suggestion_agent.py" ]; then
        cp agents/fix_suggestion_agent.py lambda_functions/
    fi
    if [ -f "agents/report_agent.py" ]; then
        cp agents/report_agent.py lambda_functions/
    fi
    
    # Copy TypeScript RuleEngine
    if [ -f "rule_engine_cli.js" ]; then
        cp rule_engine_cli.js lambda_functions/
    fi
    
    # Copy package.json and node_modules for TypeScript support
    if [ -f "package.json" ]; then
        cp package.json lambda_functions/
        if [ -d "node_modules" ]; then
            cp -r node_modules lambda_functions/
        fi
    fi
    
    echo -e "${GREEN}✅ Lambda functions prepared${NC}"
}

# Function to create requirements.txt for Lambda
create_lambda_requirements() {
    echo -e "${BLUE}📋 Creating Lambda requirements.txt...${NC}"
    
    cat > lambda_functions/requirements.txt << EOF
boto3>=1.26.0
botocore>=1.29.0
requests>=2.28.0
python-dateutil>=2.8.0
EOF
    
    echo -e "${GREEN}✅ Lambda requirements.txt created${NC}"
}

# Function to deploy with SAM
deploy_with_sam() {
    echo -e "${BLUE}🚀 Deploying with AWS SAM...${NC}"
    
    # Build SAM application
    echo -e "${BLUE}🔨 Building SAM application...${NC}"
    sam build --use-container
    
    # Deploy SAM application
    echo -e "${BLUE}🚀 Deploying SAM application...${NC}"
    sam deploy \
        --stack-name "${STACK_NAME}-${ENVIRONMENT}" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region "${REGION}" \
        --parameter-overrides \
            Environment="${ENVIRONMENT}" \
            BedrockModel="${BEDROCK_MODEL}" \
            MaxTokens="${MAX_TOKENS}" \
            Temperature="${TEMPERATURE}" \
        --no-fail-on-empty-changeset \
        --confirm-changeset
    
    echo -e "${GREEN}✅ SAM deployment completed${NC}"
}

# Function to get deployment outputs
get_deployment_outputs() {
    echo -e "${BLUE}📊 Getting deployment outputs...${NC}"
    
    # Get stack outputs
    OUTPUTS=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}-${ENVIRONMENT}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs' \
        --output json)
    
    # Extract important values
    API_URL=$(echo "${OUTPUTS}" | jq -r '.[] | select(.OutputKey=="PrivacyGuardianApiUrl") | .OutputValue')
    S3_BUCKET=$(echo "${OUTPUTS}" | jq -r '.[] | select(.OutputKey=="S3BucketName") | .OutputValue')
    DYNAMODB_TABLE=$(echo "${OUTPUTS}" | jq -r '.[] | select(.OutputKey=="DynamoDBTableName") | .OutputValue')
    EVENT_BUS=$(echo "${OUTPUTS}" | jq -r '.[] | select(.OutputKey=="EventBusName") | .OutputValue')
    DASHBOARD_URL=$(echo "${OUTPUTS}" | jq -r '.[] | select(.OutputKey=="CloudWatchDashboard") | .OutputValue')
    STATE_MACHINE=$(echo "${OUTPUTS}" | jq -r '.[] | select(.OutputKey=="StepFunctionsStateMachine") | .OutputValue')
    
    echo -e "${GREEN}✅ Deployment outputs retrieved${NC}"
}

# Function to display deployment summary
display_deployment_summary() {
    echo ""
    echo -e "${GREEN}🎉 Privacy Guardian Agents Deployment Complete!${NC}"
    echo -e "${GREEN}===============================================${NC}"
    echo ""
    echo -e "${BLUE}📊 Deployment Summary:${NC}"
    echo -e "  Stack Name: ${GREEN}${STACK_NAME}-${ENVIRONMENT}${NC}"
    echo -e "  Environment: ${GREEN}${ENVIRONMENT}${NC}"
    echo -e "  Region: ${GREEN}${REGION}${NC}"
    echo ""
    echo -e "${BLUE}🔗 Important URLs:${NC}"
    echo -e "  API Gateway: ${GREEN}${API_URL}${NC}"
    echo -e "  CloudWatch Dashboard: ${GREEN}${DASHBOARD_URL}${NC}"
    echo ""
    echo -e "${BLUE}📦 AWS Resources:${NC}"
    echo -e "  S3 Bucket: ${GREEN}${S3_BUCKET}${NC}"
    echo -e "  DynamoDB Table: ${GREEN}${DYNAMODB_TABLE}${NC}"
    echo -e "  EventBridge Bus: ${GREEN}${EVENT_BUS}${NC}"
    echo -e "  Step Functions: ${GREEN}${STATE_MACHINE}${NC}"
    echo ""
    echo -e "${BLUE}🧪 Testing Commands:${NC}"
    echo -e "  Test API: ${GREEN}curl -X POST ${API_URL}/scan -H 'Content-Type: application/json' -d '{\"project_path\": \"/tmp/test\"}'${NC}"
    echo -e "  Check Status: ${GREEN}curl ${API_URL}/status${NC}"
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo -e "  1. Test the API endpoints"
    echo -e "  2. Monitor CloudWatch logs"
    echo -e "  3. Review the CloudWatch dashboard"
    echo -e "  4. Set up SNS notifications"
    echo ""
}

# Function to test deployment
test_deployment() {
    echo -e "${BLUE}🧪 Testing deployment...${NC}"
    
    if [ -n "${API_URL}" ]; then
        echo -e "${BLUE}Testing API Gateway...${NC}"
        
        # Test status endpoint
        STATUS_RESPONSE=$(curl -s "${API_URL}/status" || echo "API not ready")
        echo -e "Status Response: ${STATUS_RESPONSE}"
        
        # Test scan endpoint
        SCAN_RESPONSE=$(curl -s -X POST "${API_URL}/scan" \
            -H "Content-Type: application/json" \
            -d '{"project_path": "/tmp/test", "scan_id": "test-scan"}' || echo "Scan not ready")
        echo -e "Scan Response: ${SCAN_RESPONSE}"
        
        echo -e "${GREEN}✅ API testing completed${NC}"
    else
        echo -e "${YELLOW}⚠️  API URL not available for testing${NC}"
    fi
}

# Function to create test data
create_test_data() {
    echo -e "${BLUE}📝 Creating test data...${NC}"
    
    # Create test files with privacy violations
    mkdir -p tests/aws-test
    
    cat > tests/aws-test/test_violations.java << 'EOF'
public class TestViolations {
    public static void main(String[] args) {
        // Hardcoded email violation
        String email = "test@example.com";
        
        // Hardcoded API key violation
        String apiKey = "sk-1234567890abcdef";
        
        // HTTP URL violation
        String url = "http://insecure-api.com/data";
        
        System.out.println("Test violations for AWS Lambda deployment");
    }
}
EOF
    
    cat > tests/aws-test/test_violations.py << 'EOF'
# Test file with privacy violations
import os

# Hardcoded email
email = "user@example.com"

# Hardcoded password
password = "secretpassword123"

# HTTP URL
api_url = "http://api.example.com/data"

# Logging PII
print(f"User email: {email}")
print(f"Processing data for: {email}")

# Insecure connection
import requests
response = requests.get("http://insecure-api.com/data")
EOF
    
    echo -e "${GREEN}✅ Test data created in tests/aws-test/${NC}"
}

# Function to clean up
cleanup() {
    echo -e "${BLUE}🧹 Cleaning up temporary files...${NC}"
    
    # Remove temporary lambda_functions directory
    if [ -d "lambda_functions" ]; then
        rm -rf lambda_functions
    fi
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Function to show help
show_help() {
    echo -e "${BLUE}Privacy Guardian Agents - AWS Lambda Deployment Script${NC}"
    echo ""
    echo "Usage: $0 [environment]"
    echo ""
    echo "Arguments:"
    echo "  environment    Deployment environment (default: development)"
    echo "                 Options: development, staging, production"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy to development"
    echo "  $0 staging           # Deploy to staging"
    echo "  $0 production        # Deploy to production"
    echo ""
    echo "Prerequisites:"
    echo "  - AWS CLI installed and configured"
    echo "  - AWS SAM CLI installed"
    echo "  - Appropriate AWS permissions"
    echo ""
}

# Main deployment function
main() {
    # Check if help is requested
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_help
        exit 0
    fi
    
    echo -e "${BLUE}🚀 Starting Privacy Guardian Agents AWS Lambda Deployment${NC}"
    echo ""
    
    # Pre-deployment checks
    check_aws_cli
    check_sam_cli
    check_aws_credentials
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo -e "${GREEN}✅ AWS Account ID: ${AWS_ACCOUNT_ID}${NC}"
    
    # Create S3 bucket for SAM
    create_sam_bucket
    
    # Prepare Lambda functions
    build_lambda_functions
    create_lambda_requirements
    
    # Deploy with SAM
    deploy_with_sam
    
    # Get deployment outputs
    get_deployment_outputs
    
    # Test deployment
    test_deployment
    
    # Create test data
    create_test_data
    
    # Display summary
    display_deployment_summary
    
    # Cleanup
    cleanup
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
}

# Run main function with all arguments
main "$@" 