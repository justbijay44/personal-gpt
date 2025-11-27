from llama_index.core.llms import ChatMessage, MessageRole
from llm_factory.get_llm import get_ollama_llm

def get_answer(model_name, chat_history):
    llm = get_ollama_llm(model_name)

    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content= "You are a helpful chat assistant.")
    ]

    messages.extend(
        ChatMessage(role=MessageRole[msg['role'].upper()], content=msg['content'])
        for msg in chat_history
    )

    response = llm.chat(messages=messages)
    return response.message.content 

# testing
# model_name = "gemma3:1b"
# chat_history = [
#     {"role": "user", "content": "What is Artificial Intelligence?"}
# ]
# response = get_answer(model_name, chat_history)
# print(response)