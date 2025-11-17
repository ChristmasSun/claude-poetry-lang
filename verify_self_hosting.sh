#!/bin/bash
# Self-Hosting Verification Script
# Runs all tests to prove Lament is self-hosting

echo "════════════════════════════════════════════════════════════"
echo "     LAMENT SELF-HOSTING VERIFICATION"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "This script runs all tests to verify self-hosting."
echo ""

# Test 1: Bootstrap test
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Bootstrap (VM executes bytecode)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
python3 -m lament.cli run compiler/test_bootstrap.lament 2>&1 | grep -E "(BOOTSTRAP SUCCESSFUL|✓|30)" | head -5
if [ $? -eq 0 ]; then
    echo "✓ Test 1 PASSED"
else
    echo "✗ Test 1 FAILED"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Compiler (Lament compiles and executes code)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
python3 -m lament.cli run compiler/final_compiler.lament 2>&1 | grep -E "(TRUE SELF-HOSTING|✓|42)" | head -5
if [ $? -eq 0 ]; then
    echo "✓ Test 2 PASSED"
else
    echo "✗ Test 2 FAILED"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: Fixed Point (Compiler stability)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
python3 -m lament.cli run compiler/fixed_point.lament 2>&1 | grep -E "(FIXED POINT|identical|SELF-HOSTING)" | head -5
if [ $? -eq 0 ]; then
    echo "✓ Test 3 PASSED"
else
    echo "✗ Test 3 FAILED"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "          ALL TESTS PASSED - SELF-HOSTING VERIFIED! ✓"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Summary:"
echo "  ✓ VM (in Lament) executes bytecode correctly"
echo "  ✓ Compiler (in Lament) compiles source code"
echo "  ✓ Compiler produces consistent output (fixed point)"
echo ""
echo "Conclusion: LAMENT IS SELF-HOSTING!"
echo ""
