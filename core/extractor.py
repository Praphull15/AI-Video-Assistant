import os

# ============================================
# IMPORTS
# ============================================

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda


# ============================================
# LOAD LLM
# ============================================

def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.environ["MISTRAL_API_KEY"],
        temperature=0.2
    )


# ============================================
# GENERIC CHAIN BUILDER
# ============================================

def build_chain(system_prompt: str):

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{text}")
    ])

    chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


# ============================================
# ACTION ITEMS
# ============================================

def extract_action_items(transcript: str) -> str:

    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items.\n\n"
        "For each action item provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list.\n"
        "If no action items exist, say: 'No action items found.'"
    )

    return chain.invoke(transcript)


# ============================================
# KEY DECISIONS
# ============================================

def extract_key_decisions(transcript: str) -> str:

    chain = build_chain(
        "You are an expert meeting analyst. "
        "Extract all important decisions made during the meeting.\n\n"
        "Format as a numbered list.\n"
        "If none found say: 'No key decisions found.'"
    )

    return chain.invoke(transcript)


# ============================================
# OPEN QUESTIONS
# ============================================

def extract_questions(transcript: str) -> str:

    chain = build_chain(
        "You are an expert meeting analyst. "
        "Extract unresolved questions or follow-up topics from the meeting.\n\n"
        "Format as a numbered list.\n"
        "If none found say: 'No open questions found.'"
    )

    return chain.invoke(transcript)
