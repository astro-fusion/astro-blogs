# Environment Variables Setup Guide

## Security Best Practices

**⚠️ CRITICAL: Never hardcode API keys in your source code!**

### 1. Create Environment Files

Create a `.env` file in your project root (this file is already in `.gitignore`):

```bash
# Copy the example file
cp .env.example .env
```

### 2. Environment File Structure

Your `.env` file should look like this:

```env
# Google Gemini API Configuration
GOOGLE_API_KEY=your_actual_api_key_here
GEMINI_API_KEY=your_actual_gemini_key_here

# Other API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 3. Using Environment Variables in Code

#### JavaScript/Node.js
```javascript
// Load environment variables
require('dotenv').config();

// Use the variables
const apiKey = process.env.GOOGLE_API_KEY;
const geminiKey = process.env.GEMINI_API_KEY;
```

#### Python
```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use the variables
api_key = os.getenv('GOOGLE_API_KEY')
gemini_key = os.getenv('GEMINI_API_KEY')
```

### 4. Security Checklist

- ✅ `.env` files are in `.gitignore`
- ✅ Never commit `.env` files to version control
- ✅ Use `.env.example` as a template
- ✅ Rotate API keys if they've been exposed
- ✅ Use different keys for development/production
- ✅ Monitor API usage for unauthorized access

### 5. If API Keys Are Exposed

1. **Immediately rotate the exposed keys** in your API provider dashboard
2. **Check your git history** for any commits containing the keys
3. **Remove the keys from git history** if necessary:
   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch path/to/file' \
   --prune-empty --tag-name-filter cat -- --all
   ```
4. **Update all services** using the old keys
5. **Monitor for unauthorized usage**

### 6. Production Deployment

For production deployments:
- Use your hosting platform's environment variable settings
- Never store production keys in code repositories
- Use secret management services (AWS Secrets Manager, Azure Key Vault, etc.)

## Example Usage

```javascript
// ❌ WRONG - Never do this
const apiKey = "AIzaSyC..."; // This exposes your key!

// ✅ CORRECT - Use environment variables
const apiKey = process.env.GOOGLE_API_KEY;
```

Remember: **Security is everyone's responsibility!**
