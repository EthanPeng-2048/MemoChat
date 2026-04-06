#!/usr/bin/env python3
"""
MemChat - Local AI Memory Routing System

A modular local AI memory routing system that can interface with llama.cpp server.
Provides structured memory management with query/write markers.
"""

import logging
import argparse
import sys

from config import LOG_LEVEL
from pipeline import run_interactive_pipeline, run_single_query

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MemChat - Local AI Memory Routing System"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="Single input query to process",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.input:
        result = run_single_query(args.input)
        if result:
            print(result)
            return 0
        else:
            print("Error: Failed to process input", file=sys.stderr)
            return 1
    else:
        run_interactive_pipeline()
        return 0


if __name__ == "__main__":
    sys.exit(main())
