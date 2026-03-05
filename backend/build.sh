#!/usr/bin/env bash
set -e

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🧠 Downloading spaCy language model..."
python -m spacy download en_core_web_sm

echo "📁 Creating runtime directories..."
mkdir -p /tmp/uploads /tmp/outputs

echo "✅ Build complete"