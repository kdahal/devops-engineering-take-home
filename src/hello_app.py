#!/usr/bin/env python3

import argparse

def greet(name: str = "world") -> str:
    return f"Hello, {name}!"

def main():
    parser = argparse.ArgumentParser(description="Simple Hello World app")
    parser.add_argument("-n", "--name", default="world", help="Name to greet")
    args = parser.parse_args()
    print(greet(args.name))

if __name__ == "__main__":
    main()

