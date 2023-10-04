from superpowered import query_knowledge_bases
from config import knowledge_base_ids

class Tool:
    """Base class for tools."""
    def __init__(self, name: str, callable_function: callable, description: str):
        """Initialize tool."""
        self.name = name
        self.func = callable_function
        self.description = description

# TODO: add a way to specify which knowledge base to use
def query_knowledge_base(query_str: str) -> str:
    """Query Superpowered knowledge bases."""
    results = query_knowledge_bases(query=query_str, knowledge_base_ids=knowledge_base_ids, summarize_results=True)
    summarized_answer = results["summary"]
    return summarized_answer

def _get_knowledge_base_tool() -> Tool:
    return Tool(
        "Knowledge Bases",
        query_knowledge_base,
        "A knowledge base. Useful for when you need to answer questions about a specific topic. Input should be a search query.",
    )

def get_tools(tool_names):
    tools = []
    for tool_name in tool_names:
        if tool_name == "Knowledge Bases":
            tools.append(_get_knowledge_base_tool())
        else:
            raise ValueError("Tool name not recognized")
    return tools