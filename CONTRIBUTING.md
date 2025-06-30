# Contributing to Privacy Guardian Agents

Thank you for your interest in contributing to Privacy Guardian Agents! This document provides guidelines and information for contributors to help maintain code quality and foster a collaborative community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Process](#contribution-process)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [License](#license)

## Code of Conduct

### Our Pledge

As contributors and maintainers of Privacy Guardian Agents, we pledge to respect all people who contribute through reporting issues, posting feature requests, updating documentation, submitting pull requests or patches, and other activities.

We are committed to making participation in this project a harassment-free experience for everyone, regardless of level of experience, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, or religion.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing opinions and viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

- The use of sexual language or imagery, derogatory comments or personal attacks
- Trolling, insulting or derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information, such as physical or electronic addresses, without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

### Enforcement

Project maintainers have the right and responsibility to remove, edit, or reject comments, commits, code, wiki edits, issues, and other contributions that are not aligned to this Code of Conduct. Project maintainers who do not follow the Code of Conduct may be removed from the project team.

This code of conduct applies both within project spaces and in public spaces when an individual is representing the project or its community.

Instances of abusive, harassing, or otherwise unacceptable behavior can be reported by emailing nabanita@privacylicense.com.

This Code of Conduct is adapted from the [Contributor Covenant](https://contributor-covenant.org), version 1.1.0.

## Getting Started

### Prerequisites

- **Node.js** (v18 or higher)
- **npm** (v8 or higher)
- **Python** (v3.9 or higher)
- **AWS CLI** (for AWS integration)
- **AWS SAM CLI** (for Lambda deployment)
- **TypeScript** knowledge (for development)
- **Git** for version control

### Fork and Clone

1. Fork the Privacy Guardian Agents repository
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/Privacy_Guardian_Agents-aws.git
   cd Privacy_Guardian_Agents-aws
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/nabanitade/Privacy_Guardian_Agents-aws.git
   ```

## Development Setup

### Installation

1. Install dependencies:
   ```bash
   # Node.js dependencies
   npm install
   
   # Python dependencies
   pip install -r requirements.txt
   ```

2. Build the project:
   ```bash
   npm run build
   ```

3. Run tests:
   ```bash
   npm test
   python -m pytest tests/
   ```

### Environment Configuration

For AI-enhanced scanning, set up environment variables:

```bash
# AWS Configuration
export AWS_REGION="us-east-1"
export AWS_PROFILE="default"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# Bedrock AI Configuration
export BEDROCK_MODEL="anthropic.claude-3-7-sonnet-20250219-v1:0"
export BEDROCK_MAX_TOKENS="2000"
export BEDROCK_TEMPERATURE="0.1"

# S3 Configuration
export S3_BUCKET_NAME="privacy-guardian-reports"

# Optional: Custom configuration
export DYNAMODB_TABLE="privacy-scan-results"
export CLOUDWATCH_NAMESPACE="PrivacyGuardian"

# Hardcoded Rules Configuration
export HARDCODED_RULES_ENABLED=true
```

### AWS Setup

1. **Configure AWS CLI**:
   ```bash
   aws configure
   ```

2. **Create AWS Resources**:
   ```bash
   # Create S3 bucket
   aws s3 mb s3://privacy-guardian-reports
   
   # Create DynamoDB table
   aws dynamodb create-table \
       --table-name privacy-scan-results \
       --attribute-definitions AttributeName=scan_id,AttributeType=S \
       --key-schema AttributeName=scan_id,KeyType=HASH \
       --billing-mode PAY_PER_REQUEST
   ```

3. **Deploy Lambda Functions**:
   ```bash
   # Deploy to AWS
   ./deploy_aws.sh development
   ```

## Contribution Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Follow the [Code Standards](#code-standards) below
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Your Changes

Use conventional commit messages:

```bash
git commit -m "feat: add new privacy rule for data retention"
git commit -m "fix: resolve timeout issue in AI scanning"
git commit -m "docs: update README with new configuration options"
```

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Link to related issues
- Screenshots (if applicable)
- Test results

## Code Standards

### TypeScript Guidelines

- Use TypeScript for all new code
- Follow ESLint configuration
- Use meaningful variable and function names
- Add JSDoc comments for public APIs
- Keep functions small and focused

### Python Guidelines

- Use Python 3.9+ syntax
- Follow PEP 8 style guidelines
- Use type hints for function parameters
- Add docstrings for all functions and classes
- Use virtual environments for dependency management

### File Structure

```
src/
├── ruleEngine/          # Privacy rule implementations
│   ├── rules/          # Individual rule files
│   └── RuleEngine.ts   # Main rule orchestrator
├── scanners/           # Language-specific scanners
├── index.ts           # Main entry point
└── types/             # TypeScript type definitions

lambda_functions/
├── agent_orchestrator.py      # Main Lambda orchestrator
├── rule_engine_bridge.js      # Node.js Lambda bridge
├── agents/                    # Python agent implementations
│   ├── privacy_scan_agent.py
│   ├── bedrock_analysis_agent.py
│   ├── compliance_agent.py
│   ├── fix_suggestion_agent.py
│   └── report_agent.py
└── ruleEngine/               # TypeScript RuleEngine
```

### Naming Conventions

- **Files**: PascalCase for classes, camelCase for utilities
- **Classes**: PascalCase (e.g., `JavaScriptScanner`)
- **Functions**: camelCase (e.g., `scanFiles`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `IGNORED_PATHS`)
- **Interfaces**: PascalCase with 'I' prefix (e.g., `IScanner`)

### Documentation Standards

- Add comprehensive JSDoc comments to all public APIs
- Include examples in documentation
- Update README.md for user-facing changes
- Document new environment variables

## Testing

### Running Tests

```bash
# Run all tests
npm test
python -m pytest tests/

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
python -m pytest --cov=tests tests/
```

### Writing Tests

- Place tests in `__tests__/` directories for TypeScript
- Place tests in `tests/` directories for Python
- Use descriptive test names
- Test both positive and negative cases
- Mock external dependencies
- Aim for >80% code coverage

### Test Structure

```typescript
describe('JavaScriptScanner', () => {
  describe('scanFiles', () => {
    it('should find JavaScript files in directory', async () => {
      // Test implementation
    });

    it('should skip ignored paths', async () => {
      // Test implementation
    });
  });
});
```

```python
class TestPrivacyScanAgent:
    def test_scan_codebase(self):
        # Test implementation
        pass
    
    def test_violation_detection(self):
        # Test implementation
        pass
```

### AWS Testing

```bash
# Test Lambda functions locally
sam local invoke AgentOrchestratorFunction --event events/test-event.json

# Test deployed functions
aws lambda invoke --function-name agent-orchestrator-development \
  --cli-binary-format raw-in-base64-out \
  --payload '{"source_code":"test code","scan_id":"test-001"}' \
  response.json
```

## Documentation

### Code Documentation

- Add JSDoc comments to all public functions and classes
- Include parameter types and return values
- Provide usage examples for complex functions
- Document error conditions and edge cases

### User Documentation

- Update README.md for new features
- Add configuration examples
- Include troubleshooting guides
- Provide integration examples

### API Documentation

- Document all public APIs
- Include parameter descriptions
- Provide return value documentation
- Add usage examples

## Areas for Contribution

### High Priority

- **New Privacy Rules**: Add rules for emerging privacy regulations
- **Language Support**: Add scanners for new programming languages
- **AI Enhancements**: Improve AWS Bedrock integration and prompts
- **Performance**: Optimize scanning speed for large codebases
- **AWS Integration**: Enhance Lambda, S3, DynamoDB integration

### Medium Priority

- **Documentation**: Improve guides and examples
- **Testing**: Add more comprehensive test coverage
- **CI/CD**: Enhance GitHub Actions and GitLab CI integration
- **Error Handling**: Improve error messages and recovery
- **Monitoring**: Enhance CloudWatch metrics and alerts

### Low Priority

- **UI Improvements**: Enhance console output formatting
- **Configuration**: Add more configuration options
- **Logging**: Improve logging and debugging capabilities
- **Examples**: Add more example projects and use cases

## AWS Development Guidelines

### Lambda Development

- Keep functions focused and single-purpose
- Use environment variables for configuration
- Implement proper error handling and logging
- Test functions locally with SAM CLI
- Monitor performance and memory usage

### AWS Service Integration

- Use IAM roles with least privilege
- Implement proper error handling for AWS API calls
- Use AWS SDK best practices
- Monitor costs and usage
- Implement proper retry logic

### Security Best Practices

- Never commit AWS credentials
- Use AWS Secrets Manager for sensitive data
- Implement proper input validation
- Use VPC for private resources when needed
- Enable CloudTrail for audit logging

## License

By contributing to Privacy Guardian Agents, you agree that your contributions will be licensed under the MIT License with Commons Clause. See the [LICENSE](LICENSE) file for details.

### Developer Certificate of Origin

By contributing to Privacy Guardian Agents, you certify that:

1. The contribution was created in whole or in part by you and you have the right to submit it under the open source license indicated in the file; or
2. The contribution is based upon previous work that, to the best of your knowledge, is covered under an appropriate open source license and you have the right under that license to submit that work with modifications, whether created in whole or in part by you, under the same open source license (unless you are permitted to submit under a different license), as indicated in the file; or
3. The contribution was provided directly to you by some other person who certified (a), (b) or (c) and you have not modified it; or
4. You understand and agree that this project and the contribution are public and that a record of the contribution (including all personal information you submit with it, including your sign-off) is maintained indefinitely and may be redistributed consistent with this project or the open source license(s) involved.

## Contact

For questions about contributing to Privacy Guardian Agents:

- **Email**: nabanita@privacylicense.com
- **Website**: https://privacylicense.ai/

Thank you for contributing to Privacy Guardian Agents! 
