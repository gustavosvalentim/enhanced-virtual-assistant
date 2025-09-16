import logging
from typing import Generator
from langchain.chat_models import init_chat_model
from langchain_core.runnables import Runnable
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from eva.tools.wikipedia import (
    find_wikipedia_pages_by_subject,
    get_wikipedia_page_by_title
)
from eva.tools.filesystem import (
    write_file,
    read_file
)
from eva.tools.weather import get_weather


with open('prompts/system_prompt.txt', 'r') as pb:
    system_prompt = pb.read()

tools = [
    find_wikipedia_pages_by_subject,
    get_wikipedia_page_by_title,
    write_file,
    read_file,
    get_weather,
]


class AgentState(MessagesState):
    pass


class EvaAssistant:
    assistant_name = 'Eva'

    def __init__(self, model: str):
        self.logger = logging.getLogger(__name__)
        self.llm = init_chat_model(model)
        self.llm_with_tools = self.llm.bind_tools(tools)
        self.checkpointer = InMemorySaver()
        self.agent = self._create_agent()

    def agent_node(self, state: AgentState) -> str:
        chat_template = ChatPromptTemplate([
            {'role': 'system', 'content': system_prompt},
        ])
        prompt = chat_template.invoke({
            'assistant_name': self.assistant_name,
        })
        messages = prompt.to_messages() + state['messages']
        response = self.llm_with_tools.invoke(messages)
        return {'messages': [response]}

    def _create_agent(self) -> Runnable:
        self.logger.debug('initializing graph...')

        tools_node = ToolNode(tools=tools)

        state_graph = StateGraph(AgentState)
        state_graph.add_node('agent', self.agent_node)
        state_graph.add_node('tools', tools_node)
        state_graph.add_conditional_edges(
            'agent',
            tools_condition,
        )
        state_graph.add_edge('tools', 'agent')
        state_graph.set_entry_point('agent')

        self.logger.debug('graph initialized...')
        compiled_graph = state_graph.compile(checkpointer=self.checkpointer)
        self.logger.debug('graph compiled...')

        return compiled_graph

    def inference(self, query: str, thread_id: str = '1') -> Generator[str, any, any]:
        config = {
            'configurable': {
                'thread_id': thread_id,
            },
        }
        invoke_args = {
            'messages': [{'role': 'user', 'content': query}],
        }
        tool_calls = {}
        events = self.agent.stream(invoke_args, config)

        for event in events:
            for value in event.values():
                last_message = value['messages'][-1]

                if isinstance(last_message, AIMessage):
                    if last_message.tool_calls:
                        tool_calls.update({
                            tool['id']: tool['name']
                            for tool in last_message.tool_calls
                        })

                    if last_message.content.strip() != '':
                        yield last_message.content

                if isinstance(last_message, ToolMessage):
                    tool_name = tool_calls.get(last_message.tool_call_id, None)
                    if tool_name:
                        content_limit = min(len(last_message.content), 140)
                        limited_tool_output = (last_message.content[:content_limit]
                                               .replace('\r\n', ' ')
                                               .replace('\n', ' ')
                                               .replace('\r', ''))
                        yield f'Output from {tool_name} - {limited_tool_output}'
