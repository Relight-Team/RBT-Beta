import argparse
from Configuration import Arguments

parser = argparse.ArgumentParser(description="Example app with optional arguments")

parser.add_argument('-name', type=str, help='Your name')
parser.add_argument('--age', type=int, help='Your age')
parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

args = parser.parse_args()

ArgsClass = Arguments.Args(args)

# Access arguments
Name = ArgsClass.GetAndParse("name")
print("name: " + str(Name))
