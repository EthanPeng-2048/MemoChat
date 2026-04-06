#!/usr/bin/env python3
"""
memochat - Local AI Memory Routing System

A modular local AI memory routing system that can interface with llama.cpp server.
Provides structured memory management with query/write markers.
"""

import logging
import argparse
import sys

from memochat import MemoChat, LOG_LEVEL

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="memochat - Local AI Memory Routing System"
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
    parser.add_argument(
        "--api-url",
        type=str,
        help="Llama API URL",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Llama API Key",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model name",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        help="Database path",
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.input:
        memo = MemoChat(
            api_url=args.api_url,
            api_key=args.api_key,
            model=args.model,
            db_path=args.db_path,
        )
        result = memo.chat(args.input)
        if result:
            print(result)
            return 0
        else:
            print("Error: Failed to process input", file=sys.stderr)
            return 1
    else:
        memo = MemoChat(
            api_url=args.api_url,
            api_key=args.api_key,
            model=args.model,
            db_path=args.db_path,
        )
        print("MemoChat initialized. Type 'quit' to exit.")
        
        while True:
            try:
                user_input = input("\nUser: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ("quit", "exit", "q"):
                    print("Exiting...")
                    break
                
                if user_input.lower() == "reset":
                    memo.reset()
                    print("Conversation history reset.")
                    continue
                
                response = memo.chat(user_input)
                
                if response:
                    print(f"\nAssistant: {response}")
                else:
                    print("\nAssistant: Sorry, I encountered an error processing your request.")
                    
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'quit' to exit gracefully.")
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
        
        return 0


if __name__ == "__main__":
    sys.exit(main())
