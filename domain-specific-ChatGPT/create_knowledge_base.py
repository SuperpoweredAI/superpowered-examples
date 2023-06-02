from superpowered import create_knowledge_base, create_document_via_url
import os

"""
# set API keys here (and uncomment this block), or export them in your shell
os.environ["SUPERPOWERED_API_KEY_ID"] = "YOUR_API_KEY_ID"
os.environ["SUPERPOWERED_API_KEY_SECRET"] = "YOUR_API_KEY_SECRET"
"""

# create a knowledge base to store some domain-specific knowledge
knowledge_base_title = "YOUR_KNOWLEDGE_BASE_TITLE"
kb = create_knowledge_base(title=knowledge_base_title)
knowledge_base_id = kb["id"]

# print the knowledge base id, because we'll need it in chat.py
print(f"Created knowledge base with id: {knowledge_base_id}")

# upload some domain-specific knowledge to the knowledge base
urls = [
    "https://superpoweredai.notion.site",
    "https://superpowered.ai/docs",
]

for url in urls:
    create_document_via_url(knowledge_base_id=knowledge_base_id, url=url)