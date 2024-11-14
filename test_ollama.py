from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3.2")
print(llm.invoke("tell me a joke"))

