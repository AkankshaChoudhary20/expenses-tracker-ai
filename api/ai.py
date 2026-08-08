import json
import logging
import os
from datetime import date

import anthropic
from pydantic import BaseModel, Field

from .models import CATEGORY_CHOICES

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-5")
REQUEST_TIMEOUT = 20.0  # seconds - bounds how long a sync Django worker can block

MAX_EXPENSES_IN_CONTEXT = 500       # most recent expenses considered for ask/insights
MAX_TOTAL_CONTEXT_CHARS = 60000     # hard stop while appending expenses to a prompt

_client = None


def get_client():
    """Returns a shared Anthropic client, or None if no API key is configured."""
    global _client
    if _client is not None:
        return _client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    _client = anthropic.Anthropic(api_key=api_key).with_options(timeout=REQUEST_TIMEOUT)
    return _client


class ParsedExpense(BaseModel):
    amount: float
    description: str = Field(description="A short, clean description of the expense")
    category: str = Field(description="One of the allowed expense categories")
    date: str = Field(description="ISO 8601 date (YYYY-MM-DD) the expense occurred on")


class AskAnswer(BaseModel):
    answer: str
    cited_expense_ids: list[int]


def parse_expense_text(text):
    """Parses free-form natural language into a structured expense. Never raises."""
    client = get_client()
    if not client or not text:
        return None
    today = date.today().isoformat()
    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=400,
            system=(
                f"Today's date is {today}. Extract a single expense from the user's text. "
                "Resolve relative dates (e.g. 'yesterday', 'last Friday') against today's date. "
                "If no date is mentioned, use today. "
                f"category must be exactly one of: {', '.join(CATEGORY_CHOICES)}."
            ),
            messages=[{"role": "user", "content": text[:2000]}],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number"},
                            "description": {"type": "string"},
                            "category": {"type": "string", "enum": CATEGORY_CHOICES},
                            "date": {"type": "string"},
                        },
                        "required": ["amount", "description", "category", "date"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        text_block = next(b.text for b in response.content if b.type == "text")
        data = json.loads(text_block)
        return ParsedExpense(**data)
    except Exception:
        logger.exception("parse_expense_text failed")
        return None


def categorize_expense(description):
    """Suggests a category for an expense based on its description. Never raises."""
    client = get_client()
    if not client or not description:
        return None
    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=100,
            system=(
                "Classify the expense description into exactly one category. "
                f"category must be exactly one of: {', '.join(CATEGORY_CHOICES)}."
            ),
            messages=[{"role": "user", "content": description[:1000]}],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string", "enum": CATEGORY_CHOICES},
                        },
                        "required": ["category"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        text_block = next(b.text for b in response.content if b.type == "text")
        return json.loads(text_block)["category"]
    except Exception:
        logger.exception("categorize_expense failed")
        return None


def _build_expense_context(expenses):
    """expenses: iterable of Expense model instances, most-recent-first."""
    context, total = [], 0
    for exp in list(expenses)[:MAX_EXPENSES_IN_CONTEXT]:
        entry = {
            "id": exp.id,
            "date": exp.date.isoformat(),
            "amount": float(exp.amount),
            "category": exp.category,
            "description": exp.description[:200],
        }
        total += len(json.dumps(entry))
        if total > MAX_TOTAL_CONTEXT_CHARS:
            break
        context.append(entry)
    return context


def ask_expenses(question, expenses):
    client = get_client()
    if not client or not question:
        return None
    context = _build_expense_context(expenses)
    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=800,
            system=(
                "Answer the user's question using ONLY the information in the provided expenses. "
                "Amounts are in USD. Do the necessary arithmetic yourself (sums, averages, comparisons). "
                "If the expenses don't contain the answer, say so plainly. "
                "cited_expense_ids must only contain ids of expenses you actually used."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nExpenses: {json.dumps(context)}",
                }
            ],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "answer": {"type": "string"},
                            "cited_expense_ids": {"type": "array", "items": {"type": "integer"}},
                        },
                        "required": ["answer", "cited_expense_ids"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        text_block = next(b.text for b in response.content if b.type == "text")
        data = json.loads(text_block)
        valid_ids = {e["id"] for e in context}
        data["cited_expense_ids"] = [i for i in data["cited_expense_ids"] if i in valid_ids]
        return AskAnswer(**data)
    except Exception:
        logger.exception("ask_expenses failed")
        return None


def generate_insights(expenses, period_label="recent"):
    """Returns a plain-English spending summary, or None. Never raises."""
    client = get_client()
    if not client:
        return None
    context = _build_expense_context(expenses)
    if not context:
        return None
    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=700,
            system=(
                f"You are a financial assistant summarizing {period_label} spending for the user. "
                "Given a JSON list of expenses (id, date, amount, category, description), write a "
                "concise plain-English summary: total spend, the top 1-3 categories by spend, and any "
                "notable patterns or callouts (e.g. a category trending up, an unusually large expense). "
                "3-6 sentences. No markdown headers, no JSON — plain prose."
            ),
            messages=[{"role": "user", "content": json.dumps(context)}],
        )
        return next((b.text for b in response.content if b.type == "text"), None)
    except Exception:
        logger.exception("generate_insights failed")
        return None
