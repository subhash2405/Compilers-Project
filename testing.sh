#!/bin/bash

# Ensure output directories exist
mkdir -p output
mkdir -p regex_outputs
mkdir -p /Users/siddharthsingh/Documents/Compilers-Project/minimal_dfa_graphs

# Define arrays of expressions and test strings
infix_expressions=(
  "(a|b)*.a.b.b"
  "(a|b).(c+).d?"
  "(a.b)*.(c|d+)"
  "a.(b|c|d).(e*)"
  "(a+).(b.c)?.d"
  "a.(b+|c.c|d*).f?"
)

test_strings=(
  "abb"
  "bcccd"
  "ababcd"
  "adeee"
  "ad"
  "acbf"
)

# Number of test cases
num_tests=${#infix_expressions[@]}

# Loop through each test
for (( i=0; i<$num_tests; i++ ))
do
  infix="${infix_expressions[$i]}"
  test_str="${test_strings[$i]}"
  echo "Running test $((i+1))..."

  # Create a temporary input file
  echo -e "$infix\n$test_str" > temp_input.txt

  # Run main.py using the temp input file with test index as argument
  python3 main.py $((i+1)) < temp_input.txt > "output/output_$((i+1)).txt"

  # Move the generated asm file
  mv regex.asm "regex_outputs/regex_$((i+1)).asm"

  # Generate corresponding graphs from the .dot files
  dot_file="/Users/siddharthsingh/Documents/Compilers-Project/minimal_dfa_graphs/graph$((i+1)).dot"
  png_file="/Users/siddharthsingh/Documents/Compilers-Project/minimal_dfa_graphs/graph$((i+1)).png"

  # Check if .dot file exists and generate the corresponding .png
  if [[ -f "$dot_file" ]]; then
    echo "Generating graph from $dot_file"
    dot -Tpng "$dot_file" -o "$png_file"
  else
    echo "No .dot file found for graph$((i+1)).dot"
  fi
done

# Cleanup
rm temp_input.txt
echo "All tests completed!"
