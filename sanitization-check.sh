#!/bin/bash
# GPWK Sanitization Verification Script
# Checks for personal data and sensitive information in the repository

echo "=== GPWK Sanitization Verification ==="
echo ""

ERRORS=0
WARNINGS=0

# Check for personal usernames
echo "[1/8] Checking for personal usernames..."
if git grep -i "clostaunau" -- "*.py" "*.md" "*.sh" 2>/dev/null | grep -v ".env.example" | grep -v "README" | grep -v "FEATURE-BRANCH-REVIEW-GUIDE.md"; then
  echo "  ❌ ERROR: Found personal username in tracked files"
  ERRORS=$((ERRORS+1))
else
  echo "  ✅ PASS: No personal usernames found"
fi
echo ""

# Check for hardcoded repo names in code
echo "[2/8] Checking for hardcoded repository names in Python code..."
if git grep '"personal-work"' -- "*.py" 2>/dev/null | grep -v "test" | grep -v ".example"; then
  echo "  ❌ ERROR: Found hardcoded repo name in Python code"
  ERRORS=$((ERRORS+1))
else
  echo "  ✅ PASS: No hardcoded repo names in Python code"
fi
echo ""

# Check for absolute user paths
echo "[3/8] Checking for absolute user paths..."
if git grep "/Users/clo\|/home/clostaunau" -- "*.py" "*.md" "*.sh" 2>/dev/null | grep -v "FEATURE-BRANCH-REVIEW-GUIDE.md"; then
  echo "  ❌ ERROR: Found absolute user paths"
  ERRORS=$((ERRORS+1))
else
  echo "  ✅ PASS: No absolute user paths found"
fi
echo ""

# Check for real API keys (not examples)
echo "[4/8] Checking for real API keys..."
# Note: This script itself contains the pattern as a search string, which is expected
# We check if the pattern exists in files OTHER than this script
if git grep "glc_eyJvIjoiMTU1ODYwNyI" 2>/dev/null | grep -v "sanitization-check.sh" | grep -q .; then
  echo "  ❌ CRITICAL: Found real API key in repository!"
  ERRORS=$((ERRORS+1))
else
  echo "  ✅ PASS: No real API keys found in tracked files"
fi
echo ""

# Check for Python artifacts
echo "[5/8] Checking for Python build artifacts..."
if git ls-files 2>/dev/null | grep "\.egg-info/\|__pycache__\|\.pyc$"; then
  echo "  ❌ ERROR: Python build artifacts are tracked in git"
  ERRORS=$((ERRORS+1))
else
  echo "  ✅ PASS: No Python build artifacts tracked"
fi
echo ""

# Check .gitignore includes Python artifacts
echo "[6/8] Checking .gitignore for Python patterns..."
if ! grep -q "\.egg-info/" gpwk/.gitignore 2>/dev/null; then
  echo "  ⚠️  WARNING: .gitignore missing Python artifact patterns"
  WARNINGS=$((WARNINGS+1))
else
  echo "  ✅ PASS: .gitignore includes Python patterns"
fi
echo ""

# Check .env is ignored
echo "[7/8] Checking .env is not tracked..."
if git ls-files 2>/dev/null | grep "\.env$"; then
  echo "  ❌ CRITICAL: .env file is tracked in git!"
  ERRORS=$((ERRORS+1))
else
  echo "  ✅ PASS: No .env files tracked"
fi
echo ""

# Check for personal user IDs in examples
echo "[8/8] Checking for personal user IDs..."
if git grep -E "2731165|1403465|1558607" -- "*.md" "*.py" 2>/dev/null | grep -v "FEATURE-BRANCH-REVIEW-GUIDE.md"; then
  echo "  ⚠️  WARNING: Found personal user IDs in files"
  WARNINGS=$((WARNINGS+1))
else
  echo "  ✅ PASS: No personal user IDs found"
fi
echo ""

# Summary
echo "=== Summary ==="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo "✅ All sanitization checks passed!"
  echo ""
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo "⚠️  All critical checks passed with $WARNINGS warning(s)"
  echo ""
  exit 0
else
  echo "❌ $ERRORS error(s) and $WARNINGS warning(s) found"
  echo ""
  echo "Please review and fix the issues above before proceeding."
  exit 1
fi
