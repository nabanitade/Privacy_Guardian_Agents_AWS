# Privacy Guardian Agents - RuleEngine Setup Guide

## Overview

This guide explains how the **Python agents** communicate with the **TypeScript RuleEngine** via a **Node.js Lambda bridge** to create a fully functional privacy scanning system in AWS.

## Architecture

```
┌─────────────────┐    AWS SDK    ┌──────────────────┐    TypeScript    ┌─────────────────┐
│   Python Agent  │ ────────────► │ Node.js Lambda   │ ───────────────► │   RuleEngine    │
│  (Lambda)       │               │     Bridge       │                  │   (TypeScript)  │
└─────────────────┘               └──────────────────┘                  └─────────────────┘
```

### Components

1. **Python Agents** (5 Lambda functions):
   - `privacy_scan_agent.py` - Initiates scans
   - `bedrock_analysis_agent.py` - AI enhancement with AWS Bedrock
   - `compliance_agent.py` - Regulatory mapping
   - `fix_suggestion_agent.py` - Fix generation
   - `report_agent.py` - Report creation

2. **Node.js Lambda Bridge**:
   - `rule_engine_bridge.js` - Executes TypeScript RuleEngine
   - Handles Node.js/TypeScript runtime requirements
   - Returns results to Python agents

3. **TypeScript RuleEngine**:
   - Core privacy violation detection engine
   - 50+ violation types across 12+ programming languages
   - AI integration with AWS Bedrock (Claude 3.7 Sonnet)

## Why This Architecture?

### The Problem
- **Python Lambda runtime** doesn't include Node.js
- **TypeScript RuleEngine** requires Node.js to execute
- **Subprocess calls** fail in Lambda environment
- **Direct imports** don't work across runtime boundaries

### The Solution
- **Node.js Lambda bridge** provides TypeScript execution environment
- **AWS SDK (boto3)** enables cross-runtime communication
- **Lambda invocation** replaces subprocess calls
- **Clean separation** of concerns between Python and TypeScript

## File Structure

```
lambda_functions/
├── rule_engine_bridge.js          # Node.js Lambda bridge
├── ruleEngine/
│   ├── __init__.py               # Python bridge (updated)
│   ├── RuleEngine.ts             # TypeScript RuleEngine
│   └── rules/                    # TypeScript rule files
├── scanners/                     # TypeScript scanner files
├── privacy_scan_agent.py         # Python agent
├── bedrock_analysis_agent.py     # Python agent
├── compliance_agent.py           # Python agent
├── fix_suggestion_agent.py       # Python agent
├── report_agent.py               # Python agent
├── package.json                  # Node.js dependencies
├── tsconfig.json                 # TypeScript config
└── build_rule_engine.sh          # Build script
```

## Setup Instructions

### 1. Prerequisites

```bash
# Install Node.js and npm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Install AWS CLI and SAM CLI
pip install awscli
pip install aws-sam-cli

# Install Python dependencies
pip install boto3
```

### 2. Build TypeScript RuleEngine

```bash
cd lambda_functions
./build_rule_engine.sh
```

This script:
- Installs Node.js dependencies
- Compiles TypeScript to JavaScript
- Copies compiled files to correct locations
- Prepares files for Lambda deployment

### 3. Test the Setup

```bash
python test_rule_engine_setup.py
```

This verifies:
- RuleEngine can be imported
- Agents can be initialized
- Lambda bridge is configured
- All components are ready

### 4. Deploy to AWS

```bash
./deploy_aws.sh development
```

This script:
- Builds TypeScript RuleEngine
- Builds SAM application
- Deploys to AWS with guided prompts

## How It Works

### 1. Python Agent Calls Node.js Bridge

```python
# In privacy_scan_agent.py
from ruleEngine import RuleEngine

engine = RuleEngine()
violations = engine.run(project_path)  # Calls Node.js Lambda via AWS SDK
```

### 2. Node.js Bridge Executes TypeScript

```javascript
// In rule_engine_bridge.js
const { RuleEngine } = require('./ruleEngine/RuleEngine.js');
const ruleEngine = new RuleEngine(scanners);

exports.handler = async (event) => {
    const violations = await ruleEngine.run(event.projectPath);
    return { violations, success: true };
};
```

### 3. Results Return to Python

```python
# Python receives results and continues workflow
for violation in violations:
    # Process each violation
    # Send to next agent in chain
```

## Configuration

### Environment Variables

```bash
# Python Lambda environment
RULE_ENGINE_BRIDGE_FUNCTION=rule-engine-bridge-development
BEDROCK_MODEL=anthropic.claude-3-7-sonnet-20250219-v1:0
AWS_REGION=us-east-1

# Node.js Lambda environment
NODE_ENV=production
ENVIRONMENT=development
```

### AWS Permissions

The Python agents need permission to invoke the Node.js bridge:

```yaml
# In template.yaml
- Effect: Allow
  Action:
    - lambda:InvokeFunction
  Resource: !GetAtt RuleEngineBridgeFunction.Arn
```

## Testing

### Local Testing

```bash
# Test RuleEngine setup
python test_rule_engine_setup.py

# Test individual components
cd lambda_functions
node rule_engine_bridge.js
```

### AWS Testing

```bash
# Test deployed API
curl -X POST https://your-api-gateway-url/scan \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/tmp/test-project"}'
```

## Troubleshooting

### Common Issues

1. **TypeScript compilation fails**
   ```bash
   cd lambda_functions
   npm install
   npx tsc --project tsconfig.json
   ```

2. **Python can't import RuleEngine**
   ```bash
   # Check if __init__.py exists
   ls lambda_functions/ruleEngine/
   ```

3. **Lambda bridge not found**
   ```bash
   # Check environment variable
   echo $RULE_ENGINE_BRIDGE_FUNCTION
   ```

4. **AWS permissions denied**
   ```bash
   # Check IAM roles and policies
   aws iam get-role --role-name your-lambda-role
   ```

### Debugging

1. **Check CloudWatch logs** for each Lambda function
2. **Monitor Step Functions** execution
3. **Test API endpoints** directly
4. **Verify environment variables** are set correctly

## Performance Considerations

### Optimization

- **Cold start**: Node.js Lambda bridge may have longer cold starts
- **Memory**: RuleEngine bridge uses 2GB memory for TypeScript compilation
- **Timeout**: Set to 5 minutes for large codebases
- **Concurrency**: Limit concurrent invocations to prevent throttling

### Monitoring

- **CloudWatch metrics** for Lambda invocations
- **X-Ray tracing** for request flow
- **Custom metrics** for violation detection rates
- **Alarms** for high error rates

## Security

### Best Practices

- **IAM roles** with minimal required permissions
- **VPC configuration** for private resources
- **Encryption** for data in transit and at rest
- **Secrets management** for API keys
- **Input validation** for all parameters

## Conclusion

This architecture successfully bridges the gap between Python and TypeScript runtimes, enabling the Privacy Guardian Agents to leverage the powerful TypeScript RuleEngine while maintaining the flexibility and ease of use of Python for the agent logic.

The Node.js Lambda bridge provides a clean, scalable solution that works reliably in the AWS Lambda environment and can be easily monitored and maintained. 