import json
from dotenv import load_dotenv

from langchain.agents import tool, AgentExecutor
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_community.tools.convert_to_openai import format_tool_to_openai_tool

from langchain_core.messages import AIMessage, HumanMessage

from langchain_openai import ChatOpenAI

from loral import Loral

load_dotenv()

LORAL_CLIENT = Loral()

@tool
def library_search(task: str) -> str:
    """
    Searches the Loral library for all methods that are relevant to accomplishing the given task.
    Returns a stringified JSON object containing the method names and descriptions.
    """
    additional_message = """
    NOTE FOR THE ASSISTANT: As the assistant, you are the only one who can execute these methods! You should now use the `execute_method` method to execute the methods that you got from `library_search` to accomplish the task.
    """
    return json.dumps(LORAL_CLIENT.library_search(task)) + "\n" + additional_message

@tool
def execute_method(method_name: str, method_arguments: str) -> str:
    """
    Executes the method from the Loral library.
    The method_arguments is a stringified JSON object containing the arguments to pass to the method as keyword arguments.
    """
    
    return LORAL_CLIENT.execute_method(method_name, method_arguments)

TOOLS = [library_search, execute_method]

LLM = ChatOpenAI(model="gpt-4-1106-preview", temperature=0)
LLM_WITH_TOOLS = LLM.bind(tools=[format_tool_to_openai_tool(tool) for tool in TOOLS])

MEMORY_KEY = "chat_history"
SYSTEM_MESSAGE = """You are very powerful assistant that is in charge of helping users with their meal prepping and grocery shopping. 
Meal planning operations are your specialty. You are creative and can come up with meal plans for users.
However, you do not know how to perform the grocery store operations. 
To help you with that, we have provided you with a library of methods called Loral that you can use to search for operations and execute them.
After that you will have access to the Loral methods: `library_search` and `execute_method`.
You can use the `library_search` method to search for methods that are relevant to the task at hand.
You can use the `execute_method` method to execute the methods that you find from `library_search` to accomplish the task.

Note that the library only contains API methods to perform grocery store operations. 
All other operations regarding meal planning are your responsibility.
"""
PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_MESSAGE),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | PROMPT
    | LLM_WITH_TOOLS
    | OpenAIToolsAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=True)

class AutoCart:
    def __init__(self):
        self.chat_history = []

    def chat(self, message: str) -> str:
        response = agent_executor.invoke(
            {
                "input": message,
                "chat_history": self.chat_history,
            }
        )
        self.chat_history.extend(
            [
                HumanMessage(content=message),
                AIMessage(content=response["output"]),
            ]
        )
        return response["output"]
