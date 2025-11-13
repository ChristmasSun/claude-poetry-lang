#!/bin/bash
# Compare emotional analysis across different code samples

echo "=================================================================="
echo "LAMENT EMOTIONAL ANALYSIS COMPARISON"
echo "=================================================================="
echo ""

for file in test_hopeful.lament test_emotional.lament example_analysis_all_features.lament; do
    echo "Analyzing: $file"
    echo "------------------------------------------------------------------"
    python3 -m lament.analysis "$file" 2>&1 | grep -E "(Overall Health:|Dominant Emotion:|Hope:|Sadness:|Anxiety:|Loneliness:|Chaos:)" | head -7
    echo ""
done

echo "=================================================================="
echo "SUMMARY"
echo "=================================================================="
echo "test_hopeful.lament               - Clean, well-structured code"
echo "test_emotional.lament             - Mixed emotional states"
echo "example_analysis_all_features.lament - Demonstrates all issues"
echo ""
