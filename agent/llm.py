from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import ( HumanMessage )

class LLM:
    def __init__(self, llm_token) -> None:
        self.llm_token = llm_token
        self.memory = ConversationBufferMemory()

    def converse(self, message):
        model = OpenAI(
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            temperature=0,
            openai_api_key=self.llm_token,
        )
        conversation = ConversationChain(
            llm=model,
            verbose=True,
            memory=self.memory
        )
        return conversation.predict(input=message)