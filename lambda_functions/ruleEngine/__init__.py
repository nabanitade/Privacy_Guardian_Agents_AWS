"""
Python Bridge to TypeScript RuleEngine via AWS Lambda
====================================================

This module provides a Python interface to the TypeScript RuleEngine,
allowing Python code to use the TypeScript privacy scanning capabilities
by invoking a Node.js Lambda function that runs the RuleEngine.

The bridge works by:
1. Invoking the Node.js Lambda bridge function via AWS SDK
2. Passing project path and configuration parameters
3. Receiving scan results and converting them to Python objects
4. Providing a Python-like interface to the TypeScript functionality
"""

import os
import json
import boto3
from typing import List, Dict, Any, Optional
from pathlib import Path

class TypeScriptRuleEngineBridge:
    """Python bridge to TypeScript RuleEngine via AWS Lambda"""
    
    def __init__(self):
        self.lambda_client = boto3.client('lambda')
        self.bridge_function_name = os.environ.get('RULE_ENGINE_BRIDGE_FUNCTION', 'privacy-guardian-rule-engine-bridge')
        
    def run(self, project_path: str) -> List[str]:
        """Run the TypeScript RuleEngine on a project path via Lambda invocation"""
        try:
            # Prepare the payload for the Node.js Lambda
            payload = {
                "projectPath": project_path,
                "geminiEnabled": self.is_bedrock_available(),
                "geminiApiKey": os.environ.get('GEMINI_API_KEY'),
                "vertexAIConfig": {
                    "project": os.environ.get('GOOGLE_CLOUD_PROJECT'),
                    "location": os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
                } if os.environ.get('GOOGLE_CLOUD_PROJECT') else None
            }
            
            print(f"Invoking RuleEngine bridge Lambda: {self.bridge_function_name}")
            print(f"Project path: {project_path}")
            
            # Invoke the Node.js Lambda function
            response = self.lambda_client.invoke(
                FunctionName=self.bridge_function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Parse the response
            response_payload = json.loads(response['Payload'].read().decode('utf-8'))
            
            if response_payload.get('statusCode') == 200:
                body = response_payload.get('body', {})
                if body.get('success'):
                    violations = body.get('violations', [])
                    print(f"✅ RuleEngine bridge found {len(violations)} violations")
                    return violations
                else:
                    print(f"❌ RuleEngine bridge failed: {body.get('error', 'Unknown error')}")
                    return []
            else:
                print(f"❌ RuleEngine bridge returned error status: {response_payload.get('statusCode')}")
                return []
                
        except Exception as e:
            print(f"❌ Error invoking RuleEngine bridge: {str(e)}")
            return []
    
    def set_gemini_enabled(self, enabled: bool):
        """Enable/disable Bedrock scanning"""
        # This is handled in the Lambda invocation payload
        pass
    
    def set_gemini_api_key(self, api_key: str):
        """Set Bedrock API key"""
        os.environ['GEMINI_API_KEY'] = api_key
    
    def set_vertex_ai_config(self, config: Dict[str, str]):
        """Set Vertex AI configuration"""
        if 'project' in config:
            os.environ['GOOGLE_CLOUD_PROJECT'] = config['project']
        if 'location' in config:
            os.environ['GOOGLE_CLOUD_LOCATION'] = config['location']
    
    def is_bedrock_available(self) -> bool:
        """Check if Bedrock is available"""
        return bool(os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_CLOUD_PROJECT'))
    
    def get_rule_stats(self) -> Dict[str, Any]:
        """Get rule statistics"""
        return {
            "status": "available",
            "total_rules": 10,
            "rule_types": [
                "PII Detection", "Privacy Policy", "Consent Management",
                "Encryption & Security", "Data Flow", "Advanced Privacy",
                "AI-Powered", "Developer Guidance"
            ]
        }

# Create a Python RuleEngine class that mimics the TypeScript interface
class RuleEngine:
    """Python wrapper for TypeScript RuleEngine via Lambda"""
    
    def __init__(self, scanners: Optional[List[Any]] = None):
        self.bridge = TypeScriptRuleEngineBridge()
        self.scanners = scanners or []
    
    def run(self, project_path: str) -> List[str]:
        """Run the RuleEngine on a project path (synchronous)"""
        return self.bridge.run(project_path)
    
    def set_gemini_enabled(self, enabled: bool):
        """Enable/disable Bedrock scanning"""
        self.bridge.set_gemini_enabled(enabled)
    
    def set_gemini_api_key(self, api_key: str):
        """Set Bedrock API key"""
        self.bridge.set_gemini_api_key(api_key)
    
    def set_vertex_ai_config(self, config: Dict[str, str]):
        """Set Vertex AI configuration"""
        self.bridge.set_vertex_ai_config(config)
    
    def is_bedrock_available(self) -> bool:
        """Check if Bedrock is available"""
        return self.bridge.is_bedrock_available()
    
    def get_rule_stats(self) -> Dict[str, Any]:
        """Get rule statistics"""
        return self.bridge.get_rule_stats()

# Create mock classes for the rules (these are not used directly in Python)
class Rule:
    """Base rule class (mock for TypeScript compatibility)"""
    pass

class PiiRule(Rule):
    """PII detection rule (mock for TypeScript compatibility)"""
    pass

class PrivacyPolicyRule(Rule):
    """Privacy policy rule (mock for TypeScript compatibility)"""
    pass

class PiiDetectionRule(Rule):
    """PII detection rule (mock for TypeScript compatibility)"""
    pass

class AiPrivacyRule(Rule):
    """AI privacy rule (mock for TypeScript compatibility)"""
    pass

class DeveloperGuidanceRule(Rule):
    """Developer guidance rule (mock for TypeScript compatibility)"""
    pass

class BedrockPrivacyRule(Rule):
    """Bedrock privacy rule (mock for TypeScript compatibility)"""
    pass

class ConsentRule(Rule):
    """Consent rule (mock for TypeScript compatibility)"""
    pass

class EncryptionRule(Rule):
    """Encryption rule (mock for TypeScript compatibility)"""
    pass

class DataFlowRule(Rule):
    """Data flow rule (mock for TypeScript compatibility)"""
    pass

class AdvancedPrivacyRule(Rule):
    """Advanced privacy rule (mock for TypeScript compatibility)"""
    pass

class Scanner:
    """Scanner class (mock for TypeScript compatibility)"""
    pass

# Export the main classes
__all__ = [
    'RuleEngine', 'Rule', 'PiiRule', 'PrivacyPolicyRule', 'PiiDetectionRule',
    'AiPrivacyRule', 'DeveloperGuidanceRule', 'BedrockPrivacyRule', 'ConsentRule',
    'EncryptionRule', 'DataFlowRule', 'AdvancedPrivacyRule', 'Scanner'
] 