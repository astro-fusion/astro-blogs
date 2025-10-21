#!/bin/bash

# Git History Cleanup Script
# This script helps remove exposed API keys from git history

echo "🧹 Git History Cleanup Script"
echo "=============================="
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

echo "⚠️  WARNING: This script will rewrite git history!"
echo "⚠️  Make sure you have backups before proceeding!"
echo ""

# Function to remove specific files from git history
remove_file_from_history() {
    local file_path="$1"
    echo "Removing $file_path from git history..."
    
    git filter-branch --force --index-filter \
        "git rm --cached --ignore-unmatch '$file_path'" \
        --prune-empty --tag-name-filter cat -- --all
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully removed $file_path from git history"
    else
        echo "❌ Failed to remove $file_path from git history"
    fi
}

# Function to remove API keys from specific files
remove_api_keys_from_file() {
    local file_path="$1"
    local key_pattern="$2"
    
    echo "Removing API keys matching pattern '$key_pattern' from $file_path..."
    
    git filter-branch --force --tree-filter \
        "if [ -f '$file_path' ]; then sed -i 's/$key_pattern/API_KEY_REMOVED/g' '$file_path'; fi" \
        --prune-empty --tag-name-filter cat -- --all
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully removed API keys from $file_path"
    else
        echo "❌ Failed to remove API keys from $file_path"
    fi
}

echo "Choose cleanup option:"
echo "1. Remove specific files from git history"
echo "2. Remove API keys from specific files"
echo "3. Remove common API key patterns from all files"
echo "4. Custom cleanup"
echo "5. Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        read -p "Enter file path to remove: " file_path
        remove_file_from_history "$file_path"
        ;;
    2)
        read -p "Enter file path: " file_path
        read -p "Enter API key pattern (regex): " key_pattern
        remove_api_keys_from_file "$file_path" "$key_pattern"
        ;;
    3)
        echo "Removing common API key patterns..."
        # Remove Google API keys
        git filter-branch --force --tree-filter \
            "find . -type f -name '*.js' -o -name '*.py' -o -name '*.json' | xargs sed -i 's/AIzaSy[^[:space:]]*/API_KEY_REMOVED/g'" \
            --prune-empty --tag-name-filter cat -- --all
        
        # Remove other common patterns
        git filter-branch --force --tree-filter \
            "find . -type f -name '*.js' -o -name '*.py' -o -name '*.json' | xargs sed -i 's/sk-[^[:space:]]*/API_KEY_REMOVED/g'" \
            --prune-empty --tag-name-filter cat -- --all
        ;;
    4)
        read -p "Enter custom git filter-branch command: " custom_command
        eval "$custom_command"
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🧹 Cleanup completed!"
echo ""
echo "📝 Next steps:"
echo "1. Force push to remote repository (if needed):"
echo "   git push --force-with-lease origin main"
echo "2. Clean up local references:"
echo "   git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin"
echo "3. Expire reflog and garbage collect:"
echo "   git reflog expire --expire=now --all && git gc --prune=now --aggressive"
echo ""
echo "⚠️  Important:"
echo "- Notify all team members to re-clone the repository"
echo "- Update any CI/CD pipelines that might be affected"
echo "- Monitor for any issues after the cleanup"
