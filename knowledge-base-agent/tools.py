from superpowered import query
from config import knowledge_base_names

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
    results = query(query=query_str, kb_titles=knowledge_base_names, extract_and_summarize=True)
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

"""
# test tool
if __name__ == "__main__":
    print("Testing tools.py")
    print("query_knowledge_base('test'):", query_knowledge_base("test"))
    print("get_tools(['Knowledge Bases']):", get_tools(["Knowledge Bases"]))
    print("get_tools(['Knowledge Bases'])[0].func('test'):", get_tools(["Knowledge Bases"])[0].run("test"))
    print("get_tools(['Knowledge Bases'])[0].description:", get_tools(["Knowledge Bases"])[0].description)
    print("get_tools(['Knowledge Bases'])[0].name:", get_tools(["Knowledge Bases"])[0].name)
"""