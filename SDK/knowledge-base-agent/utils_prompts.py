FACTUAL_OR_CREATIVE_PROMPT = """Determine if the following user input to a chatbot is asking for a factual or a creative response. For example, any coding, mathematical, or scientific questions should be classified as Factual; while creative writing requests like poetry, comedy, screenwriting, etc. should be classified as Creative. Casual conversation should also be classified as creative. Your response should be either 'Factual', 'Creative', or 'Neither'. You must respond with exactly one of those three options, and nothing else.
    
User input: Write me a poem.
Output: Creative

User input: What is the capital of France?
Output: Factual

User input: Hello
Output: Creative

User input: How are you doing today?
Output: Creative

User input: Write a blog post about why it's important to be nice to people.
Output: Creative

User input: What is the best way to make a cake?
Output: Neither

User input: What is the big bang exactly?
Output: Factual

Now follow that same format to classify the following user input as either Factual, Creative, or Neither.

User input: {input}
Output:"""

INTENT_CLASSIFICATION_PROMPT = """Determine what the likely intent of the following user input to an AI chatbot is:

User input: {input}

Here are your four options: Information Seeking, Casual Conversation, Creative Writing, or None. You must respond with exactly one of those four options, and nothing else.

Intent:"""


REQUIRED_ABILITIES_PROMPT = """You are an AGI assistant. Determine what abilities you need in order to respond to the following user input:

User input: {input}

Here are the abilities you have to choose from:
{possible_abilities}

Select the abilities you need to best respond to the user input. You can choose as many abilities as you need, but don't choose any abilities that you don't need. You MUST respond with a comma-separated list of integers corresponding to the abilities you need, and nothing else.

Abilities needed:"""


MQSC_PROMPT = """Given the following conversation:

CONVERSATION
{chat_history}

Re-write the following user input such that it contains any additional context from the conversation that would be needed to understand it. If the user input already contains sufficient context, then just return the user input as is.

USER INPUT
{input}

USER INPUT WITH CONTEXT"""