#!/bin/bash
# Script to remove .DS_Store files from git tracking and history
# Run this script if .DS_Store files were accidentally committed to git

set -e

echo "Removing .DS_Store files from git tracking..."

# Step 1: Remove from current index (if currently tracked)
# This removes .DS_Store files from ALL directories in the current staging area
echo "Checking for tracked .DS_Store files in current index..."
ds_store_files=$(git ls-files | grep -i "\.DS_Store$" || true)

if [ -n "$ds_store_files" ]; then
    echo "$ds_store_files" | while read file; do
        echo "  Removing from index: $file"
        git rm --cached --ignore-unmatch "$file" 2>/dev/null || true
    done
    echo "✓ Removed all .DS_Store files from current index"
else
    echo "  No .DS_Store files currently tracked in index"
fi

# Step 2: Ensure .gitignore is up to date (already done)

# Step 3: Remove from git history (CAUTION: This rewrites history)
echo ""
echo "WARNING: The following will rewrite git history."
echo "This should only be done if you haven't pushed recent commits with .DS_Store,"
echo "or if you're okay with force-pushing to remote."
echo ""
read -p "Remove .DS_Store from entire git history? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    echo "Removing .DS_Store from git history using git filter-branch..."
    echo "This will remove .DS_Store files from ALL directories (root and subdirectories)..."
    
    # Use git filter-branch to remove .DS_Store from all commits and all directories
    # This command:
    # 1. Lists all files in the git index for each commit
    # 2. Filters for .DS_Store files (case-insensitive, matches end of path)
    # 3. Removes each matched file from the index
    # The pattern "\.DS_Store$" ensures we match the file name at the end of the path,
    # which catches .DS_Store in root (/.DS_Store) and in subdirectories (/path/.DS_Store)
    git filter-branch --force --index-filter \
        'git ls-files | grep -i "\.DS_Store$" | while read file; do git rm --cached --ignore-unmatch "$file"; done' \
        --prune-empty --tag-name-filter cat -- --all
    
    echo ""
    echo "Done! .DS_Store has been removed from git history."
    echo ""
    echo "Next steps:"
    echo "1. Verify changes: git log --all -- .DS_Store"
    echo "2. Force push to remote (if shared repo): git push --force --all"
    echo "3. Clean up backup refs: git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin"
    echo "4. Run garbage collection: git gc --prune=now"
else
    echo "Skipped history rewrite. .DS_Store is now ignored going forward."
fi

echo ""
echo "Current .DS_Store files in working directory (these will be ignored):"
find . -name .DS_Store -type f 2>/dev/null || echo "None found"

