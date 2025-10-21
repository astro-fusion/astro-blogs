#!/bin/bash

# Environment Setup Script for AstroFusion Blog
# This script helps set up environment variables securely

echo "🔐 Setting up environment variables for AstroFusion Blog..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Environment Variables for AstroFusion Blog
# This file contains sensitive API keys - NEVER commit to version control

# Google Gemini API Configuration
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API (if using OpenAI services)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API (if using Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Configuration
NODE_ENV=development
PORT=3000

# Database Configuration (if applicable)
# DATABASE_URL=your_database_url_here

# Other API Keys (add as needed)
# TWITTER_API_KEY=your_twitter_api_key_here
# FACEBOOK_API_KEY=your_facebook_api_key_here
EOF
    echo "✅ .env file created successfully!"
else
    echo "⚠️  .env file already exists. Skipping creation."
fi

echo ""
echo "📝 Next steps:"
echo "1. Edit .env file and replace placeholder values with your actual API keys"
echo "2. Run the git cleanup script if you have exposed API keys in git history"
echo "3. Never commit .env files to version control"
echo ""
echo "🔒 Security reminder:"
echo "- Rotate any exposed API keys immediately"
echo "- Use different keys for development and production"
echo "- Monitor API usage for unauthorized access"
