"""
Base Agent Class for Privacy Guardian Agents
===========================================

This module provides the base class for all privacy guardian agents,
defining common functionality, event handling, and integration patterns.

Key Features:
------------
- Event-driven architecture with EventBridge integration
- Structured logging and monitoring
- Error handling and retry mechanisms
- Agent lifecycle management
- Integration with AWS services (S3, DynamoDB, CloudWatch, Bedrock)

Event Flow:
----------
1. Agent receives input data
2. Processes data according to agent-specific logic
3. Emits events for downstream processing
4. Returns structured results
5. Logs metrics and errors

AWS Integration:
---------------
- S3: Store reports and scan results
- DynamoDB: Store structured data and scan results
- CloudWatch: Metrics, logs, and alarms
- EventBridge: Event-driven communication
- Bedrock: AI analysis and enhancement (Claude)
- Secrets Manager: Secure configuration

Author: Privacy Guardian Team
Built for AWS Lambda Hackathon
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import boto3
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    COMPLETED = "completed"

class ViolationSeverity(Enum):
    """Violation severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ScanResult:
    """Represents a privacy violation scan result."""
    violation_type: str
    severity: str
    description: str
    file_path: str
    line_number: int
    found_value: str
    fix_suggestion: str
    regulation_reference: str
    timestamp: str
    correlation_id: str
    agent_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

@dataclass
class AgentEvent:
    """Represents an agent event for EventBridge."""
    event_type: str
    agent_id: str
    correlation_id: str
    timestamp: str
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for EventBridge."""
        return {
            "event_type": self.event_type,
            "agent_id": self.agent_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "data": self.data
        }

class BaseAgent:
    """
    Base class for all privacy guardian agents.
    
    Provides common functionality for:
    - Event handling and emission
    - AWS service integration
    - Logging and monitoring
    - Error handling and retries
    - Agent lifecycle management
    """
    
    def __init__(self, agent_id: str, agent_name: str):
        """Initialize the base agent."""
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.status = AgentStatus.IDLE
        self.start_time = None
        self.end_time = None
        
        # AWS clients
        self.s3_client = boto3.client('s3')
        self.dynamodb_client = boto3.client('dynamodb')
        self.cloudwatch_client = boto3.client('cloudwatch')
        self.events_client = boto3.client('events')
        self.bedrock_client = boto3.client('bedrock-runtime')
        self.secrets_client = boto3.client('secretsmanager')
        
        # Environment variables
        self.environment = os.environ.get('ENVIRONMENT', 'development')
        self.s3_bucket = os.environ.get('S3_BUCKET_NAME')
        self.dynamodb_table = os.environ.get('DYNAMODB_TABLE')
        self.cloudwatch_namespace = os.environ.get('CLOUDWATCH_NAMESPACE', 'PrivacyGuardian')
        self.bedrock_model = os.environ.get('BEDROCK_MODEL', 'anthropic.claude-3-7-sonnet-20250219-v1:0')
        
        logger.info(f"Initialized {self.agent_name} ({self.agent_id})")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "environment": self.environment
        }
    
    def emit_event(self, event_type: str, data: Dict[str, Any], correlation_id: str) -> None:
        """Emit an event to EventBridge."""
        try:
            event = AgentEvent(
                event_type=event_type,
                agent_id=self.agent_id,
                correlation_id=correlation_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                data=data
            )
            
            self.events_client.put_events(
                Entries=[
                    {
                        'Source': f'privacy-guardian.{self.agent_id}',
                        'DetailType': event_type,
                        'Detail': json.dumps(event.to_dict()),
                        'EventBusName': f'privacy-guardian-events-{self.environment}'
                    }
                ]
            )
            
            logger.info(f"Emitted {event_type} event for correlation_id: {correlation_id}")
            
        except Exception as e:
            logger.error(f"Failed to emit event {event_type}: {e}")
    
    def log_metric(self, metric_name: str, value: float, unit: str = 'Count', dimensions: List[Dict[str, str]] = None) -> None:
        """Log a metric to CloudWatch."""
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Dimensions': dimensions or [
                    {'Name': 'AgentId', 'Value': self.agent_id},
                    {'Name': 'Environment', 'Value': self.environment}
                ]
            }
            
            self.cloudwatch_client.put_metric_data(
                Namespace=self.cloudwatch_namespace,
                MetricData=[metric_data]
            )
            
        except Exception as e:
            logger.error(f"Failed to log metric {metric_name}: {e}")
    
    def store_result(self, result: Dict[str, Any], correlation_id: str) -> None:
        """Store result in DynamoDB."""
        try:
            item = {
                'scan_id': {'S': correlation_id},
                'timestamp': {'S': datetime.now(timezone.utc).isoformat()},
                'agent_id': {'S': self.agent_id},
                'result': {'S': json.dumps(result)}
            }
            
            self.dynamodb_client.put_item(
                TableName=self.dynamodb_table,
                Item=item
            )
            
            logger.info(f"Stored result for correlation_id: {correlation_id}")
            
        except Exception as e:
            logger.error(f"Failed to store result: {e}")
    
    def store_report(self, report_data: Dict[str, Any], filename: str) -> str:
        """Store report in S3."""
        try:
            key = f"reports/{filename}"
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=json.dumps(report_data, indent=2),
                ContentType='application/json'
            )
            
            s3_url = f"s3://{self.s3_bucket}/{key}"
            logger.info(f"Stored report: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to store report: {e}")
            return None
    
    def get_secret(self, secret_name: str) -> str:
        """Get a secret from AWS Secrets Manager."""
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            secret = response['SecretString']
            logger.info(f"Retrieved secret: {secret_name}")
            return secret
        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            return ""
    
    async def get_bedrock_analysis(self, prompt: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Get AI analysis from AWS Bedrock (Claude) with fallback.
        
        Args:
            prompt: The prompt to send to Claude
            context: Optional context data to include with the prompt
            
        Returns:
            AI response text if successful, None if AI is unavailable or fails
        """
        try:
            # Enhance prompt with context if provided
            if context:
                context_str = json.dumps(context, indent=2)
                enhanced_prompt = f"{prompt}\n\nContext:\n{context_str}"
            else:
                enhanced_prompt = prompt
            
            # Prepare Bedrock request with correct Claude API format
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": int(os.environ.get('BEDROCK_MAX_TOKENS', 2000)),
                "top_k": 250,
                "stop_sequences": [],
                "temperature": float(os.environ.get('BEDROCK_TEMPERATURE', 0.1)),
                "top_p": 0.999,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": enhanced_prompt
                            }
                        ]
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.bedrock_model,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract content from Claude response
            if 'content' in response_body and len(response_body['content']) > 0:
                content = response_body['content'][0]
                if content.get('type') == 'text':
                    completion = content.get('text', '')
                else:
                    completion = str(content)
            else:
                # Fallback for different response formats
                completion = response_body.get('completion', '') or response_body.get('content', '')
            
            logger.info(f"🤖 Bedrock (Claude) analysis completed for {self.agent_name}")
            return completion
            
        except Exception as e:
            logger.warning(f"Bedrock analysis failed: {str(e)} - using hardcoded rules")
            return None
    
    def is_bedrock_available(self) -> bool:
        """
        Check if Bedrock is available for this agent.
        
        Returns:
            True if Bedrock is configured and available, False otherwise
        """
        return bool(self.bedrock_model)
    
    async def process(self, input_data: Dict[str, Any]) -> Any:
        """
        Process input data - to be implemented by subclasses.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processed results
        """
        raise NotImplementedError("Subclasses must implement process method")
    
    def _handle_error(self, error: Exception, correlation_id: str) -> Dict[str, Any]:
        """Handle errors and log them appropriately."""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "correlation_id": correlation_id,
            "agent_id": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.error(f"Error in {self.agent_name}: {error_info}")
        self.log_metric('Errors', 1.0)
        
        return error_info
    
    def _start_processing(self) -> None:
        """Mark agent as processing."""
        self.status = AgentStatus.PROCESSING
        self.start_time = datetime.now(timezone.utc)
        logger.info(f"Started processing: {self.agent_name}")
    
    def _end_processing(self) -> None:
        """Mark agent as completed."""
        self.status = AgentStatus.COMPLETED
        self.end_time = datetime.now(timezone.utc)
        logger.info(f"Completed processing: {self.agent_name}") 