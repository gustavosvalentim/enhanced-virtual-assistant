import logging
from typing import Generator, List, TypedDict
from langchain.chat_models import init_chat_model
from langchain_core.runnables import Runnable
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import END
from eva.prompts import load_prompt
from eva.tools.wikipedia import (
    find_wikipedia_pages_by_subject,
    get_wikipedia_page_by_title
)
from eva.tools.filesystem import (
    write_file,
    read_file
)
from eva.tools.weather import get_weather

tools = [
    find_wikipedia_pages_by_subject,
    get_wikipedia_page_by_title,
    write_file,
    read_file,
    get_weather,
]


class AgentState(TypedDict):
    messages: List[BaseMessage]
    reviewer_approved: bool
    reviewer_feedback: str
    __next__: str


class ReviewerResult(TypedDict):
    approved: bool
    reason: str


class EvaAssistant:
    assistant_name = 'Eva'

    def __init__(self, model: str):
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.checkpointer = InMemorySaver()
        self.agent = self._create_agent()

    def agent_node(self, state: AgentState) -> AgentState:
        chat_template = ChatPromptTemplate([
            {'role': 'system', 'content': load_prompt('system_prompt')},
        ])
        prompt = chat_template.invoke({
            'assistant_name': self.assistant_name,
        })
        messages = prompt.to_messages() + state['messages']
        llm = init_chat_model(self.model)
        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke(messages)
        return {'messages': [response]}

    def reviewer_node(self, state: AgentState) -> AgentState:
        last_message = state['messages'][-1]
        llm = init_chat_model(self.model, temperature=0.2)
        reviewer_prompt = load_prompt('reviewer_prompt').format(
            agent_instructions=load_prompt('system_prompt').format(
                assistant_name=self.assistant_name,
            ),
            chat_history=state['messages'][:-1],
            ai_message=last_message.content,
        )
        response = llm.with_structured_output(ReviewerResult).invoke(reviewer_prompt)
        return {
            '__next__': 'agent' if not response['approved'] else END,
            'reviewer_approved': response['approved'],
            'reviewer_feedback': response['reason'],
            'messages': state['messages'] + [AIMessage(content=response['reason'])],
        }

    def _create_agent(self) -> Runnable:
        self.logger.debug('initializing graph...')

        tools_node = ToolNode(tools=tools)

        state_graph = StateGraph(AgentState)
        state_graph.add_node('agent', self.agent_node)
        state_graph.add_node('tools', tools_node)
        state_graph.add_node('reviewer', self.reviewer_node)

        state_graph.set_entry_point('agent')

        state_graph.add_conditional_edges(
            'agent',
            tools_condition,
            {
                "tools": "tools",
                END: "reviewer",
            }
        )
        state_graph.add_edge('tools', 'agent')
        state_graph.add_conditional_edges(
            'reviewer',
            lambda state: state['__next__'],
            {
                END: END,
                'agent': 'agent',
            }
        )

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


def display_graph(assistant: EvaAssistant):
    try:
        print(assistant.agent.get_graph().draw_mermaid())
    except:
        pass
