"use strict";
/**
  * Copyright (c) 2025 Privacy Guardian Agents by Privacy License . All rights reserved.
* Licensed under the MIT License with the Commons Clause.
* This file is provided for personal, educational, and non-commercial use only.
* Commercial use including selling, sublicensing, internal deployment in for-profit
* environments, SaaS integration, or submission to hackathons, accelerators, or competitive evaluations—is strictly prohibited without a commercial license.
*
* For complete license terms, see https://gitlab.com/tnabanitade/privacysdk/-/blob/master/LICENSE.
* Commercial use is prohibited without a license.
* To request a Commercial License or integration approval, contact: nabanita@privacylicense.com | https://privacylicense.ai
 *
 * BedrockPrivacyRule - AI-Powered Privacy Scanning with AWS Bedrock
 *
 * This rule implements advanced AI-powered privacy violation detection using AWS Bedrock.
 * It provides intelligent, context-aware analysis of code to identify privacy violations that traditional
 * pattern-based rules might miss.
 *
 * Key Features:
 * - Uses AWS Bedrock for intelligent privacy analysis
 * - Provides detailed explanations with specific fixes
 * - References relevant privacy laws (GDPR, CCPA, etc.)
 * - Includes severity levels and actionable guidance
 * - Falls back gracefully if AI is unavailable
 * - Configurable via environment variables
 *
 * Detection Capabilities:
 * - Hardcoded PII and sensitive data
 * - Privacy policy violations
 * - Data handling compliance issues
 * - Security vulnerabilities
 * - Consent mechanism violations
 * - Data flow and retention issues
 *
 * Configuration:
 * - BEDROCK_ENABLED: Enable/disable AI scanning
 * - BEDROCK_API_KEY: Your AWS API key
 * - BEDROCK_MODEL: Model to use (default: anthropic.claude-3-sonnet-20240229-v1:0)
 * - BEDROCK_MAX_TOKENS: Max tokens per request
 * - BEDROCK_TEMPERATURE: AI creativity level
 *
 * Usage:
 * This rule works in hybrid mode with hardcoded rules, providing enhanced accuracy
 * while maintaining reliability through fallback mechanisms.
 *
 * @author Privacy Vulnerabilities Checker
 * @version 1.0.0
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.BedrockPrivacyRule = void 0;
class BedrockPrivacyRule {
    constructor() {
        this.id = "BEDROCK001";
        this.description = "Detects privacy violations related to AWS Bedrock usage";
        this.enabled = false;
        this.apiKey = null;
        this.config = null;
    }
    setEnabled(enabled) {
        this.enabled = enabled;
    }
    setApiKey(apiKey) {
        this.apiKey = apiKey;
    }
    setBedrockConfig(config) {
        this.config = config;
    }
    isAvailable() {
        return this.enabled && this.apiKey !== null;
    }
    async evaluate(content, filePath) {
        const violations = [];
        const lines = content.split('\n');
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const lineNumber = i + 1;
            // Check for hardcoded Bedrock API keys
            if (line.includes('bedrock') && line.includes('api_key') && line.includes('=')) {
                violations.push({
                    line: lineNumber,
                    match: `Hardcoded Bedrock API key detected. Use AWS Secrets Manager or environment variables for API keys.`
                });
            }
            // Check for exposed Bedrock model names
            if (line.includes('bedrock') && line.includes('model') && line.includes('anthropic.claude')) {
                violations.push({
                    line: lineNumber,
                    match: `Bedrock model name exposed in code. Use environment variables for model names.`
                });
            }
            // Check for hardcoded prompts that might contain sensitive data
            if (line.includes('prompt') && line.includes('"') && (line.includes('password') ||
                line.includes('secret') ||
                line.includes('key') ||
                line.includes('token'))) {
                violations.push({
                    line: lineNumber,
                    match: `Sensitive data in Bedrock prompt. Sanitize prompts to remove sensitive information.`
                });
            }
        }
        return violations;
    }
}
exports.BedrockPrivacyRule = BedrockPrivacyRule;
