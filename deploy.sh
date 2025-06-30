# Copyright (c) 2025 Privacy Guardian Agents by Privacy License . All rights reserved.
# Licensed under the MIT License modified with the Commons Clause.
# For complete license terms, see https://github.com/nabanitade/Privacy_Guardian_Agents-aws/blob/main/LICENSE
# Commercial use is prohibited without a license.
# Contact for Commercial License: nabanita@privacylicense.com | https://privacylicense.ai

#!/bin/bash

# Privacy Guardian Agents - Deployment Script
# Supports local development and AWS Lambda deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
STACK_NAME="privacy-guardian-agents"
S3_BUCKET_NAME="privacy-guardian-reports"
DYNAMODB_TABLE="privacy-scan-results"
ENVIRONMENT=${ENVIRONMENT:-"development"}

echo -e "${BLUE}🚀 Privacy Guardian Agents Deployment${NC}"
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check AWS setup
check_aws_setup() {
    if ! command_exists aws; then
        echo -e "${RED}❌ AWS CLI not found. Please install it first:${NC}"
        echo "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        exit 1
    fi
    
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        echo -e "${RED}❌ Not authenticated with AWS. Please run:${NC}"
        echo "aws configure"
        exit 1
    fi
    
    echo -e "${GREEN}✅ AWS CLI configured${NC}"
}

# Function to setup AWS resources
setup_aws_resources() {
    echo -e "${BLUE}🔧 Setting up AWS resources...${NC}"
    
    # Create S3 bucket
    echo "Creating S3 bucket..."
    aws s3 mb s3://$S3_BUCKET_NAME --region $AWS_REGION || echo "Bucket already exists"
    
    # Create DynamoDB table
    echo "Creating DynamoDB table..."
    aws dynamodb create-table \
        --table-name $DYNAMODB_TABLE \
        --attribute-definitions AttributeName=scan_id,AttributeType=S \
        --key-schema AttributeName=scan_id,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region $AWS_REGION || echo "Table already exists"
    
    echo -e "${GREEN}✅ AWS resources created${NC}"
}

# Function to deploy Lambda functions
deploy_lambda_functions() {
    echo -e "${BLUE}🚀 Deploying Lambda functions...${NC}"
    
    # Build TypeScript RuleEngine
    echo "Building TypeScript RuleEngine..."
    cd lambda_functions
    ./build_rule_engine.sh
    cd ..
    
    # Deploy with SAM
    echo "Deploying with AWS SAM..."
    sam build
    sam deploy \
        --stack-name $STACK_NAME-$ENVIRONMENT \
        --capabilities CAPABILITY_IAM \
        --parameter-overrides \
            Environment=$ENVIRONMENT \
            S3BucketName=$S3_BUCKET_NAME \
            DynamoDBTableName=$DYNAMODB_TABLE \
        --region $AWS_REGION \
        --no-confirm-changeset \
        --no-fail-on-empty-changeset
    
    # Get the API Gateway URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME-$ENVIRONMENT \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
        --output text)
    
    echo -e "${GREEN}✅ Deployed Lambda functions: $API_URL${NC}"
}

# Function to setup CloudWatch monitoring
setup_monitoring() {
    echo -e "${BLUE}📊 Setting up CloudWatch monitoring...${NC}"
    
    # Create CloudWatch dashboard
    cat > cloudwatch-dashboard.json << EOF
{
    "widgets": [
        {
            "type": "metric",
            "x": 0,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    ["AWS/Lambda", "Invocations", "FunctionName", "agent-orchestrator-$ENVIRONMENT"],
                    [".", "Errors", ".", "."],
                    [".", "Duration", ".", "."]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "$AWS_REGION",
                "title": "Lambda Function Metrics"
            }
        }
    ]
}
EOF
    
    aws cloudwatch put-dashboard \
        --dashboard-name "PrivacyGuardianDashboard-$ENVIRONMENT" \
        --dashboard-body file://cloudwatch-dashboard.json \
        --region $AWS_REGION
    
    # Create CloudWatch alarms
    aws cloudwatch put-metric-alarm \
        --alarm-name "PrivacyViolationsHigh-$ENVIRONMENT" \
        --alarm-description "High number of privacy violations detected" \
        --metric-name "Violations" \
        --namespace "PrivacyGuardian" \
        --statistic "Sum" \
        --period 300 \
        --threshold 10 \
        --comparison-operator "GreaterThanThreshold" \
        --region $AWS_REGION
    
    echo -e "${GREEN}✅ CloudWatch monitoring setup completed${NC}"
}

# Function to setup local development
setup_local() {
    echo -e "${BLUE}🏠 Setting up local development...${NC}"
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Install Node.js dependencies
    npm install
    
    # Create .env file
    cat > .env << EOF
AWS_REGION=$AWS_REGION
S3_BUCKET_NAME=$S3_BUCKET_NAME
DYNAMODB_TABLE=$DYNAMODB_TABLE
BEDROCK_MODEL=anthropic.claude-3-7-sonnet-20250219-v1:0
BEDROCK_MAX_TOKENS=2000
BEDROCK_TEMPERATURE=0.1
ENVIRONMENT=$ENVIRONMENT
EOF
    
    echo -e "${GREEN}✅ Local development environment ready${NC}"
    echo -e "${YELLOW}⚠️  Please update .env with your actual AWS credentials${NC}"
}

# Function to run locally
run_local() {
    echo -e "${BLUE}🏃 Running locally...${NC}"
    
    source venv/bin/activate
    
    # Run the web server
    python web_server.py
}

# Function to test Lambda functions
test_lambda() {
    echo -e "${BLUE}🧪 Testing Lambda functions...${NC}"
    
    # Test agent orchestrator
    echo "Testing agent orchestrator function..."
    aws lambda invoke \
        --function-name agent-orchestrator-$ENVIRONMENT \
        --cli-binary-format raw-in-base64-out \
        --payload '{"source_code":"public class TestClass {\n    private String email = \"test@example.com\";\n    private String apiKey = \"sk-1234567890abcdef\";\n    private String ssn = \"123-45-6789\";\n    \n    public void processData() {\n        System.out.println(\"Processing data\");\n    }\n}","scan_id":"test-scan-001","project_path":"test.java"}' \
        response.json \
        --region $AWS_REGION
    
    # Test rule engine bridge
    echo "Testing rule engine bridge function..."
    aws lambda invoke \
        --function-name rule-engine-bridge-$ENVIRONMENT \
        --cli-binary-format raw-in-base64-out \
        --payload '{"source_code":"public class TestClass {\n    private String email = \"test@example.com\";\n}","file_type":"java"}' \
        bridge-response.json \
        --region $AWS_REGION
    
    echo -e "${GREEN}✅ Lambda function tests completed${NC}"
    echo "Check response.json and bridge-response.json for results"
}

# Function to cleanup resources
cleanup() {
    echo -e "${BLUE}🧹 Cleaning up AWS resources...${NC}"
    
    # Delete CloudFormation stack
    aws cloudformation delete-stack \
        --stack-name $STACK_NAME-$ENVIRONMENT \
        --region $AWS_REGION
    
    echo "Waiting for stack deletion to complete..."
    aws cloudformation wait stack-delete-complete \
        --stack-name $STACK_NAME-$ENVIRONMENT \
        --region $AWS_REGION
    
    # Delete S3 bucket contents and bucket
    aws s3 rm s3://$S3_BUCKET_NAME --recursive --region $AWS_REGION || true
    aws s3 rb s3://$S3_BUCKET_NAME --region $AWS_REGION || true
    
    # Delete DynamoDB table
    aws dynamodb delete-table \
        --table-name $DYNAMODB_TABLE \
        --region $AWS_REGION || true
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Function to show status
show_status() {
    echo -e "${BLUE}📊 Checking deployment status...${NC}"
    
    # Check CloudFormation stack
    if aws cloudformation describe-stacks \
        --stack-name $STACK_NAME-$ENVIRONMENT \
        --region $AWS_REGION >/dev/null 2>&1; then
        echo -e "${GREEN}✅ CloudFormation stack exists${NC}"
        
        # Get stack outputs
        API_URL=$(aws cloudformation describe-stacks \
            --stack-name $STACK_NAME-$ENVIRONMENT \
            --region $AWS_REGION \
            --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
            --output text 2>/dev/null || echo "Not available")
        
        echo "API Gateway URL: $API_URL"
    else
        echo -e "${RED}❌ CloudFormation stack not found${NC}"
    fi
    
    # Check Lambda functions
    if aws lambda get-function \
        --function-name agent-orchestrator-$ENVIRONMENT \
        --region $AWS_REGION >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Lambda functions deployed${NC}"
    else
        echo -e "${RED}❌ Lambda functions not found${NC}"
    fi
    
    # Check S3 bucket
    if aws s3 ls s3://$S3_BUCKET_NAME --region $AWS_REGION >/dev/null 2>&1; then
        echo -e "${GREEN}✅ S3 bucket exists${NC}"
    else
        echo -e "${RED}❌ S3 bucket not found${NC}"
    fi
    
    # Check DynamoDB table
    if aws dynamodb describe-table \
        --table-name $DYNAMODB_TABLE \
        --region $AWS_REGION >/dev/null 2>&1; then
        echo -e "${GREEN}✅ DynamoDB table exists${NC}"
    else
        echo -e "${RED}❌ DynamoDB table not found${NC}"
    fi
}

# Main deployment logic
case "${1:-help}" in
    "local")
        setup_local
        ;;
    "run-local")
        run_local
        ;;
    "deploy")
        check_aws_setup
        setup_aws_resources
        deploy_lambda_functions
        setup_monitoring
        ;;
    "test")
        check_aws_setup
        test_lambda
        ;;
    "status")
        check_aws_setup
        show_status
        ;;
    "cleanup")
        check_aws_setup
        cleanup
        ;;
    "setup")
        check_aws_setup
        setup_aws_resources
        ;;
    "help"|*)
        echo -e "${BLUE}Usage:${NC}"
        echo "  ./deploy.sh local          - Setup local development environment"
        echo "  ./deploy.sh run-local      - Run the application locally"
        echo "  ./deploy.sh deploy         - Deploy to AWS Lambda"
        echo "  ./deploy.sh test           - Test deployed Lambda functions"
        echo "  ./deploy.sh status         - Check deployment status"
        echo "  ./deploy.sh cleanup        - Clean up AWS resources"
        echo "  ./deploy.sh setup          - Setup AWS resources only"
        echo ""
        echo -e "${YELLOW}Environment Variables:${NC}"
        echo "  AWS_REGION                 - AWS region (default: us-east-1)"
        echo "  ENVIRONMENT                - Environment name (default: development)"
        echo "  S3_BUCKET_NAME             - S3 bucket for reports"
        echo "  DYNAMODB_TABLE             - DynamoDB table for results"
        echo ""
        echo -e "${GREEN}Quick Start:${NC}"
        echo "  1. Configure AWS credentials: aws configure"
        echo "  2. Run: ./deploy.sh local"
        echo "  3. Update .env with your AWS credentials"
        echo "  4. Run: ./deploy.sh deploy"
        echo "  5. Test: ./deploy.sh test"
        ;;
esac 