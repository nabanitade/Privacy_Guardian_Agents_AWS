# Privacy Guardian Agents – Security & License Disclaimer

Privacy Guardian Agents is provided for non-commercial, educational, and evaluation purposes under the MIT License modified by the Commons Clause.

## ⚠️ Commercial Use Prohibited.

Use of Privacy Guardian Agents in any commercial product, paid offering, or service—whether hosted or embedded—is **strictly prohibited** without a commercial license. This includes:
- Selling or sublicensing the software
- Using the software as part of a paid SaaS tool
- Providing commercial consulting or audits powered by Privacy Guardian Agents
- Using the software in any commercial AWS Lambda deployment

To inquire about commercial licensing, contact:
📧 nabanita@privacylicense.com  
🌐 https://privacylicense.ai

## 🔒 Security Considerations

### AWS Lambda Security
- All Lambda functions use IAM roles with least-privilege access
- Secrets are stored in AWS Secrets Manager with encryption
- All data is encrypted at rest and in transit
- CloudWatch logs provide comprehensive audit trails

### Data Privacy
- No code or data is sent to third parties except AWS Bedrock (when enabled)
- All scanning happens in secure AWS Lambda environment
- Scan results are stored in encrypted S3 buckets and DynamoDB tables
- Access is controlled through IAM policies and roles

### Compliance
- GDPR compliant data handling practices
- CCPA compliant privacy controls
- HIPAA compliant security measures
- PCI DSS compliant data protection

## Disclaimer

This software is provided "as is", without warranty or guarantee of privacy compliance. Use at your own risk. The system is designed for educational and evaluation purposes only.

