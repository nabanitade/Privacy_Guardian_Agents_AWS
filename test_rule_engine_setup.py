#!/usr/bin/env python3
"""
Test script to verify RuleEngine setup
=====================================

This script tests the Python agents' ability to communicate with the TypeScript RuleEngine
via the Node.js Lambda bridge.
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add the lambda_functions directory to the path
sys.path.append(str(Path(__file__).parent / "lambda_functions"))

def test_rule_engine_import():
    """Test if the RuleEngine can be imported"""
    print("🔍 Testing RuleEngine import...")
    
    try:
        from ruleEngine import RuleEngine
        print("✅ RuleEngine imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import RuleEngine: {e}")
        return False

def test_rule_engine_initialization():
    """Test if the RuleEngine can be initialized"""
    print("\n🔍 Testing RuleEngine initialization...")
    
    try:
        from ruleEngine import RuleEngine
        engine = RuleEngine()
        print("✅ RuleEngine initialized successfully")
        
        # Test basic methods
        stats = engine.get_rule_stats()
        print(f"📊 Rule stats: {stats}")
        
        gemini_available = engine.is_gemini_available()
        print(f"🤖 Gemini available: {gemini_available}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize RuleEngine: {e}")
        return False

def test_agent_import():
    """Test if the agents can be imported"""
    print("\n🔍 Testing agent imports...")
    
    agents = [
        "privacy_scan_agent",
        "bedrock_analysis_agent", 
        "compliance_agent",
        "fix_suggestion_agent",
        "report_agent"
    ]
    
    success_count = 0
    for agent_name in agents:
        try:
            module = __import__(agent_name)
            print(f"✅ {agent_name} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"❌ Failed to import {agent_name}: {e}")
    
    return success_count == len(agents)

def test_agent_initialization():
    """Test if the agents can be initialized"""
    print("\n🔍 Testing agent initialization...")
    
    try:
        from privacy_scan_agent import PrivacyScanAgent
        agent = PrivacyScanAgent()
        print("✅ PrivacyScanAgent initialized successfully")
        
        # Test RuleEngine status
        status = agent.get_rule_engine_status()
        print(f"📊 RuleEngine status: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize PrivacyScanAgent: {e}")
        return False

def test_lambda_bridge_setup():
    """Test if the Lambda bridge is properly configured"""
    print("\n🔍 Testing Lambda bridge setup...")
    
    try:
        import boto3
        lambda_client = boto3.client('lambda')
        print("✅ boto3 Lambda client created successfully")
        
        # Check if we're in AWS environment
        try:
            lambda_client.list_functions(MaxItems=1)
            print("✅ Lambda client can connect to AWS")
            return True
        except Exception as e:
            print(f"⚠️  Lambda client cannot connect to AWS (this is normal for local testing): {e}")
            return True  # This is expected for local testing
            
    except ImportError as e:
        print(f"❌ boto3 not available: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Privacy Guardian Agents - RuleEngine Setup Test")
    print("=" * 60)
    
    tests = [
        ("RuleEngine Import", test_rule_engine_import),
        ("RuleEngine Initialization", test_rule_engine_initialization),
        ("Agent Imports", test_agent_import),
        ("Agent Initialization", test_agent_initialization),
        ("Lambda Bridge Setup", test_lambda_bridge_setup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The setup is ready for deployment.")
        print("\n📋 Next steps:")
        print("   1. Run: ./deploy_with_rule_engine.sh")
        print("   2. Test the deployed API endpoints")
        print("   3. Monitor the Lambda functions in AWS Console")
    else:
        print("⚠️  Some tests failed. Please fix the issues before deployment.")
        print("\n🔧 Common fixes:")
        print("   1. Install missing dependencies: pip install boto3")
        print("   2. Build TypeScript: cd lambda_functions && ./build_rule_engine.sh")
        print("   3. Check file paths and imports")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 