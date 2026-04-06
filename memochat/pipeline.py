import logging
from typing import Optional

from .config import LOG_LEVEL
from .db_handler import init_db
from .memory_router import route_memory

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class MemoryPipeline:
    def __init__(self):
        init_db()
        self.conversation_history: list[dict] = []
        logger.info("MemoryPipeline initialized")

    def process_input(self, user_input: str) -> Optional[str]:
        logger.info(f"Processing user input: {user_input[:100]}...")
        
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
        })
        
        response, results = route_memory(
            user_input,
            self.conversation_history[:-1],
        )
        
        if response is None:
            logger.error("Failed to get response from memory router")
            return None
        
        for result in results:
            if result["type"] == "write":
                self.conversation_history.append({
                    "role": "system",
                    "content": f"Memory saved: {result['result']}",
                })
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
        })
        
        return response

    def get_history(self) -> list[dict]:
        return self.conversation_history.copy()

    def reset(self) -> None:
        self.conversation_history = []
        logger.info("Conversation history reset")


def run_interactive_pipeline() -> None:
    pipeline = MemoryPipeline()
    
    print("Memory Router Pipeline initialized. Type 'quit' to exit.")
    
    while True:
        try:
            user_input = input("\nUser: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ("quit", "exit", "q"):
                print("Exiting pipeline...")
                break
            
            if user_input.lower() == "reset":
                pipeline.reset()
                print("Conversation history reset.")
                continue
            
            response = pipeline.process_input(user_input)
            
            if response:
                print(f"\nAssistant: {response}")
            else:
                print("\nAssistant: Sorry, I encountered an error processing your request.")
                
        except KeyboardInterrupt:
            print("\nInterrupted. Type 'quit' to exit gracefully.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)


def run_single_query(user_input: str) -> Optional[str]:
    pipeline = MemoryPipeline()
    return pipeline.process_input(user_input)


if __name__ == "__main__":
    run_interactive_pipeline()
