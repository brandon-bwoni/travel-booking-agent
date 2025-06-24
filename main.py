from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory.buffer import ConversationBufferMemory
from tools import booking_tool, search_tool, faq_tool

llm = ChatOpenAI(
    model="gemma3:27b")

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=[search_tool, booking_tool, faq_tool],
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
)


if __name__ == "__main__":
    print("Agent online. Type 'bye' to exit.")
    while True:
        q = input("You: ").strip()
        if q.lower() == "bye":
            break
        print("Agent:", agent.invoke(q))