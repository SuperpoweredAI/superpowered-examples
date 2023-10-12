from superpowered import create_chat_thread, get_chat_response
import json
import openai
import os

EVALUATION_PROMPT = """
Your job is to evaluate the performance of an AI-powered question answering system. You will be given a query, a ground truth answer, and the answer given by the AI. Your task is to grade the AI's answer on a scale of 0-10. A score of 0 means the AI's answer is completely wrong. A score of 10 means the AI's answer is completely correct. A score of 5 means the AI's answer is partially correct.

Your response must ONLY be an integer between 0 and 10 (inclusive). Do not include any other text in your response.

GUIDELINES FOR GRADING
- The ground truth answers are often lacking in detail, so if the AI's answer is more detailed than the ground truth answer, then that's generally a good sign.
- Be wary of overly broad or general AI answers. If the AI's answer lacks specifics, then it probably isn't a good answer.

QUERY
{query}

GROUND TRUTH ANSWER
{ground_truth_answer}

AI-GENERATED ANSWER
{model_answer}

GRADE
""".strip()

# we'll use this to run the evaluation prompt
def openai_api_call(chat_messages: list[dict], model_name: str = "gpt-4", temperature: float = 0.0, max_tokens: int = 1) -> str:
    max_tokens = int(max_tokens)
    temperature = float(temperature)
    assert model_name in ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"]

    # call the OpenAI API
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=chat_messages,
        max_tokens=max_tokens,
        temperature=temperature,
        request_timeout=120,
    )
    llm_output = response['choices'][0]['message']['content'].strip()
    return llm_output

# get the model's predictions for each query in the eval set
def get_response(query: str, config: dict):
    """
    - config is a dictionary containing:
        - "use_rse": whether to use the RSE or not
        - "kb_id": the ID of the knowledge base to use
        - "system_message": the system message to use
    """
    use_rse = config["use_rse"]
    kb_id = config["kb_id"]
    system_message = config["system_message"]
    
    thread_id = create_chat_thread([kb_id], use_rse=use_rse, system_message=system_message)["id"] # create a chat thread with the provided config parameters
    chat_response = get_chat_response(thread_id, query)
    chat_response = chat_response["interaction"]["model_response"]["content"]
    return chat_response

# evaluate the model's predictions against the ground truth answers
def evaluate_response(query, gt_answer, model_answer):
    prompt = EVALUATION_PROMPT.format(query=query, ground_truth_answer=gt_answer, model_answer=model_answer)
    chat_messages = [{"role": "user", "content": prompt}]
    response = openai_api_call(chat_messages, model_name="gpt-4", temperature=0.0, max_tokens=1)
    return response

def run_evaluation(eval_set: list[dict], config: dict):
    """
    - eval_set is a list of dictionaries, where each dictionary contains:
        - "query": the query
        - "gt_answer": the ground truth answer, i.e. what you want the model to output
    - config is a dictionary containing:
        - "use_rse": whether to use the RSE or not
        - "kb_id": the ID of the knowledge base to use
        - "system_message": the system message to use
    """
    # run the evaluation
    eval_results = []
    for eval_item in eval_set:
        query = eval_item["query"]
        gt_answer = eval_item["gt_answer"]
        model_answer = get_response(query, config)

        grade = evaluate_response(query, gt_answer, model_answer)
        print(grade)

        # save the results
        eval_results.append({
            "query": query,
            "gt_answer": gt_answer,
            "model_answer": model_answer,
            "grade": grade,
        })

    # export eval results to a json file
    with open(f"eval_results.json", "w") as f:
        json.dump(eval_results, f, indent=4)


# eval set is a list of dicts, each with keys "query" and "gt_answer" (ground truth answer)
eval_set = [
    {
        "query": "What is Sourcegraph’s mission?", 
        "gt_answer": """Sourcegraph’s mission is to make it so everyone codes. They believe that a world where everyone codes will see faster and more broadly beneficial technological progress. By making the process of building software less complex, Sourcegraph hopes to make progress towards this mission."""
    },
    {
        "query": "What is Cody and what are the team’s strategic plans for it over the next year?", 
        "gt_answer": """Cody is an AI coding assistant that lives in your editor that can find, explain, and write code. Their strategic goals over the next three months are increasing enterprise adoption (which will require multi-repo context fetching, Sourcegraph embeddings, and bring your own model capabilities); prove out IDE extension usage (by experimenting with a set of IDE extensions in parallel); add Cody into Sourcegraph; and letting Cody use App as a backend. Over the remainder of the next twelve months, their strategic goals for Cody are to continue pushing for enterprise adoption and to add more editors (like IntelliJ and others)."""
    },
    {
        "query": "I just got hired for an engineering role. What should I do before my first day?",
        "gt_answer": """You should complete the following tasks before your first day: fill out your BambooHR profile and upload a photo, complete your background check, place an order for your Sourcegraph computer, make your welcome video, and order your swag pack."""
    },
    {
        "query": "What are the legal team’s FY’23 goals?",
        "gt_answer": """The legal team has four objectives in FY’23. 1) processes are set up to enable the company to hit revenue targets, 2) data collection and storage policies for cloud and other products earn customer trust, 3) equity compensation is legally compliant and maximizes value to teammates, and 4) each legal team member has grown."""
    },
    {
        "query": "What are the different marketing launch tiers and how should they be used?",
        "gt_answer": """There are L1, L2, and L3 launches. L1 launches should be reserved for the most important product announcements of the year. L2 launches are reserved for features or small products. L3 launches are for small or incremental features and updates."""
    },
    {
        "query": "How do you move a page in the handbook to a new location?",
        "gt_answer": """In a single pull request, rename the file with its new location. Be sure to update any links to that page."""
    },
    {
        "query": "Am I expected to be responsive on weekends and evenings?",
        "gt_answer": """No, you generally are not expected to be responsive on weekend, evening, and holidays, with the exception of on-call engineers and other roles that specifically require it."""
    },
    {
        "query": "What is Sourcegraph’s policy on remote work?",
        "gt_answer": """Sourcegraph is an all-remote company. All teammates are encouraged to work remotely."""
    },
    {
        "query": "What are Sourcegraph’s core values?",
        "gt_answer": """Sourcegraph has four core values: 1) dev love, 2) high agency, 3) win together, and 4) direct and transparent."""
    },
    {
        "query": "Why does Sourcegraph use an async work style?",
        "gt_answer": """Sourcegraph uses an async work style for a few reasons: 1) they are respectful of people's time and responsibilities, 2) they are inclusive, 3) they value context, 4) they encourage thoughtful decision making, 5) they care about mental health, 6) they value high agency, and 7) they are a remote company, so they have to be async."""
    },
]

# define the config and run the evaluation
SYSTEM_MESSAGE = """
You are an AI company assistant for a startup called Sourcegraph. You have been paired with a search system that will provide you with relevant information from the company handbook to help you answer user questions. You will see the results of these searches below. Since this is the only information about the company you have access to, if the necessary information to answer the user's question is not contained there, you should tell the user you don't know the answer. You should NEVER make things up just try to provide an answer.
""".strip()

config = {
    "use_rse": True,
    "kb_id": "INSERT_KB_ID_HERE",
    "system_message": SYSTEM_MESSAGE,
}

print ("\nRunning evaluation...")
run_evaluation(eval_set, config)