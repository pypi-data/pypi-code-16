import sys

# Test the output and error redirection
sys.stdout.write("Hello World!\n")
sys.stderr.write("Hello Error!\n")

# Test creating an output file
with open("test.out", 'w') as f:
    f.write("This is only a test.\n")


