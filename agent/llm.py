
from langchain.llms import OpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import json

with open('settings.json', 'r') as file:
    data = json.load(file)

llm = OpenAI(
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
    temperature=0,
    openai_api_key=data["llm_api_key"],
)

resp = llm("Write me a song about sparkling water.")