#!/usr/bin/env python3
"""
Manual script to check Bitcoin signals
"""

from bitcoin_strategy import check_daily_signals

def main():
    print("Checking Bitcoin trading signals...")
    result = check_daily_signals()
    print(result)

if __name__ == "__main__":
    main()