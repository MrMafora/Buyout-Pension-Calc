#!/usr/bin/env python3
"""
test-skill - A test skill
"""

import argparse

def main():
    parser = argparse.ArgumentParser(description="A test skill")
    parser.add_argument("--example", help="Example argument")
    
    args = parser.parse_args()
    
    print("Hello from test-skill!")
    
    if args.example:
        print(f"Example: {args.example}")

if __name__ == "__main__":
    main()
