#!/bin/bash

# Prompt the user to input the input file name
read -p "Please define the input file name (e.g., input_file_name.csv): " input_file

# Check if the input file name is provided
if [ -z "$input_file" ]; then
    echo "Input file name is required."
    exit 1
fi

# Prompt the user to input the output file name
read -p "Please define the output file name (e.g., output_file_name.csv): " output_file

# Check if the output file name is provided
if [ -z "$output_file" ]; then
    echo "Output file name is required."
    exit 1
fi

# Define intermediate file names
intermediate_file1="intermediate_file1.csv"
intermediate_file2="intermediate_file2.csv"

# Step 1: Score Calculation
echo "Running score calculation..."
python score_calculation.py --input "$input_file" --output "$intermediate_file1"
if [ $? -ne 0 ]; then
    echo "Error in score calculation. Please check the input file and try again."
    exit 1
fi

# Step 2: Data Filter
echo "Running data filter..."
python data_filter.py --input "$intermediate_file1" --output "$intermediate_file2"
if [ $? -ne 0 ]; then
    echo "Error in data filter. Please check the intermediate file and try again."
    exit 1
fi

# Step 3: Apply Physical Constraint
echo "Applying physical constraint..."
python apply_constraint.py --input "$intermediate_file2" --output "$output_file"
if [ $? -ne 0 ]; then
    echo "Error in applying physical constraint. Please check the intermediate file and try again."
    exit 1
fi

echo "All steps completed successfully. Output file: $output_file"
