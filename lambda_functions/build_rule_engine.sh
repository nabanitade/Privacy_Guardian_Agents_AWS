#!/bin/bash

# Build script for TypeScript RuleEngine
# This script compiles TypeScript files to JavaScript for the Node.js Lambda bridge

set -e

echo "🔨 Building TypeScript RuleEngine for Node.js Lambda..."

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Compile TypeScript to JavaScript
echo "⚙️  Compiling TypeScript to JavaScript..."
npx tsc --project tsconfig.json

# Copy compiled files to the correct locations
echo "📁 Copying compiled files..."

# Create directories if they don't exist
mkdir -p ruleEngine
mkdir -p scanners

# Copy compiled RuleEngine files
if [ -f "dist/ruleEngine/RuleEngine.js" ]; then
    cp dist/ruleEngine/RuleEngine.js ruleEngine/
    echo "✅ Copied RuleEngine.js"
fi

# Copy compiled rule files
for rule_file in dist/ruleEngine/rules/*.js; do
    if [ -f "$rule_file" ]; then
        mkdir -p ruleEngine/rules
        cp "$rule_file" ruleEngine/rules/
        echo "✅ Copied $(basename "$rule_file")"
    fi
done

# Copy compiled scanner files
for scanner_file in dist/scanners/*.js; do
    if [ -f "$scanner_file" ]; then
        cp "$scanner_file" scanners/
        echo "✅ Copied $(basename "$scanner_file")"
    fi
done

# Copy package.json for Lambda deployment
cp package.json ./

echo "🎉 TypeScript RuleEngine build completed!"
echo "📋 Files ready for Lambda deployment:"
echo "   - rule_engine_bridge.js"
echo "   - ruleEngine/RuleEngine.js"
echo "   - ruleEngine/rules/*.js"
echo "   - scanners/*.js"
echo "   - package.json" 