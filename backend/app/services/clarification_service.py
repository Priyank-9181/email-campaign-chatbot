"""
Detect missing campaign parameters and build choice-based clarification payloads.
"""
import json
import re
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.services import dataset_service

# User wants to create/run a campaign (not just list datasets)
_CAMPAIGN_INTENT = re.compile(
    r"\b(campaign|campign|camping|email|promo|promotion|discount|newsletter|"
    r"birthday|welcome|launch|send|blast|draft|marketing)\b",
    re.I,
)

_SEND_INTENT = re.compile(
    r"\b(send|deliver|dispatch|blast|mail\s+(to|the)|email\s+(to|them|all))\b",
    re.I,
)

_DRAFT_ONLY = re.compile(r"\b(draft|only\s+create|don'?t\s+send|do\s+not\s+send|no\s+send)\b", re.I)

_DATASET_ID = re.compile(r"\bdataset\s*(?:id\s*)?[#:]?\s*(\d+)\b", re.I)
_DATASET_NAME = re.compile(r"\bdataset\s+(?:name\s+is\s+)?['\"]?([\w\-]+)['\"]?", re.I)

_CAMPAIGN_TYPES = [
    {"id": "welcome", "label": "Welcome", "value": "campaign_type=welcome"},
    {"id": "promotional", "label": "Promotional", "value": "campaign_type=promotional"},
    {"id": "discount", "label": "Discount / offer", "value": "campaign_type=discount"},
    {"id": "product_launch", "label": "Product launch", "value": "campaign_type=product_launch"},
    {"id": "re_engagement", "label": "Re-engagement", "value": "campaign_type=re_engagement"},
    {"id": "newsletter", "label": "Newsletter", "value": "campaign_type=newsletter"},
]


def _text_from_history(chat_history: list) -> str:
    parts = []
    for msg in chat_history or []:
        content = getattr(msg, "content", None) or (msg if isinstance(msg, str) else "")
        if content:
            parts.append(str(content))
    return "\n".join(parts)


def _resolve_dataset_id(prompt: str, context: str, db: Session) -> Optional[int]:
    """Return dataset id if clearly specified in prompt or recent context."""
    combined = f"{context}\n{prompt}"

    m = _DATASET_ID.search(combined)
    if m:
        return int(m.group(1))

    m = _DATASET_NAME.search(combined)
    if m:
        name = m.group(1).lower()
        for d in dataset_service.list_datasets(db):
            if d.name.lower() == name or d.file_name.lower().replace(".csv", "") == name:
                return d.id

    for d in dataset_service.list_datasets(db):
        if d.name.lower() in prompt.lower():
            return d.id
        if d.name.lower() in context.lower():
            return d.id

    return None


def _has_campaign_type(prompt: str, context: str) -> bool:
    combined = f"{context}\n{prompt}".lower()
    for ct in _CAMPAIGN_TYPES:
        if ct["id"].replace("_", " ") in combined or ct["id"] in combined:
            return True
    if re.search(r"\b(birthday|welcome|discount|promo|newsletter|launch|re-?engage)\b", combined):
        return True
    return False


def _send_intent_clear(prompt: str) -> Optional[bool]:
    """True = send, False = draft only, None = unclear."""
    if _DRAFT_ONLY.search(prompt):
        return False
    if _SEND_INTENT.search(prompt):
        return True
    return None


def build_clarification(
    prompt: str,
    db: Session,
    chat_history: Optional[list] = None,
    skip_clarification: bool = False,
) -> Optional[dict[str, Any]]:
    """
    Return a clarification dict if the user should pick options before running the agent.
    None means proceed with the full agent.
    """
    if skip_clarification:
        return None

    context = _text_from_history(chat_history or [])
    combined = f"{context}\n{prompt}"

    if not _CAMPAIGN_INTENT.search(prompt) and not _CAMPAIGN_INTENT.search(context):
        return None

    datasets = dataset_service.list_datasets(db)
    if not datasets:
        return {
            "question": "You need a contact list before creating a campaign. What would you like to do?",
            "field": "no_dataset",
            "choices": [
                {
                    "id": "upload",
                    "label": "I'll upload a CSV on the Datasets page first",
                    "value": "I will upload a dataset on the Datasets page first.",
                },
            ],
            "allow_multiple": False,
        }

    dataset_id = _resolve_dataset_id(prompt, context, db)

    # 1) Dataset missing or ambiguous (multiple datasets, none resolved)
    if dataset_id is None:
        if len(datasets) == 1:
            # Single dataset — auto-resolve, no question
            pass
        else:
            choices = []
            for d in datasets:
                count = len(dataset_service.get_contacts_by_dataset(db, d.id))
                choices.append(
                    {
                        "id": f"dataset_{d.id}",
                        "label": f"{d.name} ({count} contacts)",
                        "value": f"Use dataset id {d.id} ({d.name}).",
                    }
                )
            return {
                "question": "Which contact list (dataset) should this campaign use?",
                "field": "dataset",
                "choices": choices,
                "allow_multiple": False,
            }

    # 2) Send vs draft unclear when campaign intent exists
    send_clear = _send_intent_clear(prompt)
    if send_clear is None and _CAMPAIGN_INTENT.search(prompt):
        return {
            "question": "Should I only create a draft campaign, or also send emails to all contacts?",
            "field": "send_mode",
            "choices": [
                {
                    "id": "draft",
                    "label": "Create draft only (no emails sent)",
                    "value": "Create a draft campaign only. Do not send emails.",
                },
                {
                    "id": "send",
                    "label": "Create and send emails",
                    "value": "Create the campaign and send emails to all contacts in the dataset.",
                },
            ],
            "allow_multiple": False,
        }

    # 3) Campaign type helpful for generation (optional if topic is very specific like "birthday")
    if not _has_campaign_type(prompt, context) and re.search(
        r"\b(create|make|build|start)\b.*\b(campaign|campign|camping)\b", prompt, re.I
    ):
        return {
            "question": "What type of campaign is this? (helps write subject and body)",
            "field": "campaign_type",
            "choices": _CAMPAIGN_TYPES,
            "allow_multiple": False,
        }

    return None


def format_clarification_response(clarification: dict[str, Any]) -> str:
    """Human-readable message shown above choice buttons."""
    return clarification.get("question", "Please choose an option:")


def serialize_stored_response(text: str, clarification: Optional[dict]) -> str:
    if not clarification:
        return text
    payload = {"text": text, "clarification": clarification}
    return json.dumps(payload)


def parse_stored_response(raw: str) -> tuple[str, Optional[dict]]:
    if not raw or not raw.strip().startswith("{"):
        return raw, None
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and "text" in data:
            return data.get("text", raw), data.get("clarification")
    except json.JSONDecodeError:
        pass
    return raw, None
