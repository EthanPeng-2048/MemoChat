from memochat import MemoChat

memo = MemoChat(
    api_url="http://localhost:8080/v1/chat/completions",
    api_key="your_api_key_here",
    model="GLM-5",
    db_path="memochat.db",
)

response = memo.chat("你好！")
print(response)
