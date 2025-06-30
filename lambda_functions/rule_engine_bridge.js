/**
 * Node.js Lambda Bridge for TypeScript RuleEngine
 * 
 * This Lambda function serves as a bridge between Python agents and the TypeScript RuleEngine.
 * It allows Python Lambda functions to execute the TypeScript privacy scanning engine
 * without needing Node.js in the Python runtime.
 */

const { RuleEngine } = require('./ruleEngine/RuleEngine.js');
const { JavaScriptScanner } = require('./scanners/JavaScriptScanner.js');
const { TypeScriptScanner } = require('./scanners/TypeScriptScanner.js');
const { PythonScanner } = require('./scanners/PythonScanner.js');
const { JavaScanner } = require('./scanners/JavaScanner.js');
const { CSharpScanner } = require('./scanners/CSharpScanner.js');
const { GoScanner } = require('./scanners/GoScanner.js');
const { PHPScanner } = require('./scanners/PHPScanner.js');
const { RubyScanner } = require('./scanners/RubyScanner.js');
const { SwiftScanner } = require('./scanners/SwiftScanner.js');
const { KotlinScanner } = require('./scanners/KotlinScanner.js');
const { RustScanner } = require('./scanners/RustScanner.js');
const { ScalaScanner } = require('./scanners/ScalaScanner.js');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Initialize scanners for all supported languages
const scanners = [
    new JavaScriptScanner(),
    new TypeScriptScanner(),
    new PythonScanner(),
    new JavaScanner(),
    new CSharpScanner(),
    new GoScanner(),
    new PHPScanner(),
    new RubyScanner(),
    new SwiftScanner(),
    new KotlinScanner(),
    new RustScanner(),
    new ScalaScanner()
];

// Initialize the RuleEngine
const ruleEngine = new RuleEngine(scanners);

exports.handler = async (event, context) => {
    console.log('RuleEngine Bridge Lambda invoked');
    console.log('Event:', JSON.stringify(event, null, 2));
    
    try {
        const { projectPath, sourceCode, fileType, geminiEnabled, geminiApiKey, vertexAIConfig } = event;
        
        let scanPath = projectPath;
        
        // If source code is provided, create a temporary file
        if (sourceCode && fileType) {
            const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'privacy_scan_'));
            const tempFile = path.join(tempDir, `test.${fileType}`);
            
            // Ensure the directory exists
            if (!fs.existsSync(tempDir)) {
                fs.mkdirSync(tempDir, { recursive: true });
            }
            
            fs.writeFileSync(tempFile, sourceCode);
            scanPath = tempDir;
            
            console.log(`Created temporary directory: ${tempDir}`);
            console.log(`Created temporary file: ${tempFile}`);
            console.log(`File content length: ${sourceCode.length} characters`);
            
            // Verify file exists
            if (fs.existsSync(tempFile)) {
                console.log(`File exists: ${tempFile}`);
                const stats = fs.statSync(tempFile);
                console.log(`File size: ${stats.size} bytes`);
            } else {
                console.error(`File does not exist: ${tempFile}`);
            }
            
            // List directory contents
            try {
                const files = fs.readdirSync(tempDir);
                console.log(`Directory contents: ${files.join(', ')}`);
            } catch (dirError) {
                console.error(`Error reading directory: ${dirError.message}`);
            }
        }
        
        if (!scanPath) {
            throw new Error('Either projectPath or sourceCode with fileType is required in the event');
        }
        
        // Configure Bedrock if provided
        if (geminiEnabled !== undefined) {
            ruleEngine.setBedrockEnabled(geminiEnabled);
        }
        
        if (geminiApiKey) {
            ruleEngine.setBedrockApiKey(geminiApiKey);
        }
        
        if (vertexAIConfig) {
            ruleEngine.setBedrockConfig(vertexAIConfig);
        }
        
        // Run the RuleEngine
        console.log(`Scanning path: ${scanPath}`);
        const violations = await ruleEngine.run(scanPath);
        
        console.log(`Found ${violations.length} violations`);
        
        // Clean up temporary files if created (after scanning is complete)
        if (sourceCode && fileType) {
            try {
                // Add a small delay to ensure scanning is complete
                await new Promise(resolve => setTimeout(resolve, 100));
                fs.rmSync(scanPath, { recursive: true, force: true });
                console.log('Cleaned up temporary files');
            } catch (cleanupError) {
                console.warn('Failed to clean up temporary files:', cleanupError.message);
            }
        }
        
        // Return results in a format the Python agents can process
        return {
            statusCode: 200,
            body: {
                success: true,
                violations: violations,
                totalViolations: violations.length,
                projectPath: scanPath,
                timestamp: new Date().toISOString(),
                ruleStats: ruleEngine.getRuleStats(),
                bedrockAvailable: ruleEngine.isBedrockAvailable()
            }
        };
        
    } catch (error) {
        console.error('Error in RuleEngine Bridge:', error);
        
        return {
            statusCode: 500,
            body: {
                success: false,
                error: error.message,
                timestamp: new Date().toISOString()
            }
        };
    }
}; 