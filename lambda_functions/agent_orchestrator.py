import json
import os
import boto3
from datetime import datetime, timezone
from privacy_scan_agent import PrivacyScanAgent
from bedrock_analysis_agent import BedrockAnalysisAgent
from compliance_agent import ComplianceAgent
from fix_suggestion_agent import FixSuggestionAgent
from report_agent import ReportAgent

def lambda_handler(event, context):
    """
    Orchestrator Lambda: Calls each agent in sequence.
    1. Calls Node.js RuleEngine bridge via boto3 (Lambda invoke)
    2. Passes results through all Python agents
    3. Returns the final report
    """
    # Parse event - handle both direct fields and body JSON string
    if isinstance(event.get('body'), str):
        try:
            body_data = json.loads(event['body'])
            # Merge body data with event data
            event.update(body_data)
            print(f"DEBUG: Parsed body data: {body_data}")
        except json.JSONDecodeError:
            print("Warning: Could not parse body as JSON")
    
    # Extract parameters
    project_path = event.get('project_path', '/tmp/project')
    source_code = event.get('source_code') or event.get('sourceCode')  # Handle both naming conventions
    file_type = event.get('fileType', 'java')
    
    print(f"DEBUG: Extracted project_path: {project_path}")
    print(f"DEBUG: Extracted source_code: {source_code[:100] if source_code else None}...")
    print(f"DEBUG: Extracted file_type: {file_type}")
    
    # --- NEW: Write source_code to /tmp/project/{project_path} if provided ---
    if source_code and project_path:
        tmp_dir = '/tmp/project'
        os.makedirs(tmp_dir, exist_ok=True)
        # If project_path is a filename, write to /tmp/project/{project_path}
        # If project_path is a path, ensure parent dirs exist
        dest_path = os.path.join(tmp_dir, os.path.basename(project_path))
        with open(dest_path, 'w') as f:
            f.write(source_code)
        # Update project_path to /tmp/project for bridge
        project_path = tmp_dir
        
        # Debug logging
        print(f"DEBUG: Wrote source code to {dest_path}")
        print(f"DEBUG: File exists: {os.path.exists(dest_path)}")
        print(f"DEBUG: Directory contents: {os.listdir(tmp_dir)}")
        with open(dest_path, 'r') as f:
            print(f"DEBUG: File contents: {f.read()}")
    # --- END NEW ---

    # 1. Call Node.js RuleEngine bridge Lambda
    lambda_client = boto3.client('lambda')
    bridge_function_name = os.environ.get('BRIDGE_FUNCTION_NAME', 'rule-engine-bridge-development')
    
    payload = {
        "projectPath": None,  # Let bridge handle temporary file creation
        "sourceCode": source_code,  # Pass source code to bridge
        "fileType": file_type,  # Pass file type to bridge
        "geminiEnabled": True,  # Enable Bedrock AI in RuleEngine
        "geminiApiKey": os.environ.get('GEMINI_API_KEY'),
        "vertexAIConfig": {
            "project": os.environ.get('GOOGLE_CLOUD_PROJECT'),
            "location": os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
        } if os.environ.get('GOOGLE_CLOUD_PROJECT') else None,
        "start_time": datetime.now(timezone.utc).isoformat()
    }
    
    print(f"Orchestrator: Sending payload to bridge: {json.dumps(payload, indent=2)}")
    
    response = lambda_client.invoke(
        FunctionName=bridge_function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    bridge_result = json.loads(response['Payload'].read().decode('utf-8'))
    print(f"Orchestrator: Bridge response: {json.dumps(bridge_result, indent=2)}")
    
    if bridge_result.get('statusCode') == 200:
        body = bridge_result.get('body', {})
        scan_results = body.get('violations', [])
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'RuleEngine bridge failed', 'details': bridge_result})
        }

    # 2. Pass results through all Python agents
    # Convert bridge violation strings to ScanResult objects
    scan_results_objs = []
    for violation_str in scan_results:
        # Parse violation string: [LANG] path:line - description (found: "match")
        import re
        match = re.match(r'\[(\w+)\]\s+([^:]+):(\d+)\s+-\s+(.+?)\s+\(found:\s*"([^"]*)"\)', violation_str)
        if match:
            lang, file_path, line_num, description, found_value = match.groups()
            from base_agent import ScanResult
            scan_results_objs.append(ScanResult(
                violation_type="PrivacyViolation",  # Will be determined by agents
                severity="medium",  # Will be determined by agents
                description=description.strip(),
                file_path=file_path.strip(),
                line_number=int(line_num),
                found_value=found_value,
                fix_suggestion="Review and fix privacy violation",
                regulation_reference="GDPR/CCPA",  # Will be determined by agents
                timestamp=datetime.now(timezone.utc).isoformat(),
                correlation_id="bridge-scan",
                agent_id="bridge"
            ))

    # PrivacyScanAgent (for compatibility, but already scanned)
    scan_agent = PrivacyScanAgent()
    # scan_results_objs already contains ScanResult objects

    # BedrockAnalysisAgent
    gemini_agent = BedrockAnalysisAgent()
    enhanced_results = gemini_agent.process({'scan_results': scan_results_objs})
    if hasattr(enhanced_results, '__await__'):
        import asyncio
        enhanced_results = asyncio.run(enhanced_results)

    # ComplianceAgent
    compliance_agent = ComplianceAgent()
    compliance_report = compliance_agent.process({'enhanced_results': enhanced_results})
    if hasattr(compliance_report, '__await__'):
        import asyncio
        compliance_report = asyncio.run(compliance_report)

    # FixSuggestionAgent
    fix_agent = FixSuggestionAgent()
    fix_suggestions = fix_agent.process({'enhanced_results': enhanced_results, 'compliance_report': compliance_report})
    if hasattr(fix_suggestions, '__await__'):
        import asyncio
        fix_suggestions = asyncio.run(fix_suggestions)

    # ReportAgent
    report_agent = ReportAgent()
    report = report_agent.process({'enhanced_results': enhanced_results, 'compliance_report': compliance_report, 'fix_suggestions': fix_suggestions})
    if hasattr(report, '__await__'):
        import asyncio
        report = asyncio.run(report)

    return {
        'statusCode': 200,
        'body': json.dumps(report, default=str)
    } 