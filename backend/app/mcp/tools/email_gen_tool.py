import os

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from app.database.connection import SessionLocal
from app.services import dataset_service


def _get_llm():
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        temperature=float(os.getenv("EMAIL_GEN_TEMPERATURE", "0.5")),
        timeout=int(os.getenv("OPENROUTER_TIMEOUT_SEC", "90")),
        max_retries=int(os.getenv("OPENROUTER_MAX_RETRIES", "1")),
    )


@tool
def generate_subject_tool(topic: str, dataset_name: str = "", campaign_type: str = "") -> str:
    """Generate a compelling email subject line (max ~80 chars) for the marketing topic. Optional campaign_type: welcome, promotional, discount, product_launch, re_engagement, newsletter."""
    llm = _get_llm()
    prompt = f"""Write ONE email marketing subject line only (max 80 characters). No quotes, no explanation.

Topic: {topic}
Audience / dataset: {dataset_name or "general leads"}
Campaign style (if any): {campaign_type or "match topic"}

Rules: professional, specific, not spammy caps lock."""
    response = llm.invoke(prompt)
    return response.content.strip()


@tool
def generate_preview_text_tool(topic: str, subject: str) -> str:
    """Generate short inbox preview / preheader text (40–120 chars) that complements the subject and improves opens. Return only the preview line, no quotes."""
    llm = _get_llm()
    prompt = f"""Write ONE email preheader / preview text (40 to 120 characters) that complements the subject and teases the email. Return only that line, no quotes.

Subject: {subject}
Topic: {topic}"""
    response = llm.invoke(prompt)
    return response.content.strip()


@tool
def generate_body_tool(
    topic: str,
    subject: str,
    dataset_id: int,
    preview_text: str = "",
    body_format: str = "html",
    campaign_type: str = "",
) -> str:
    """Generate full email body: greeting, main content, CTA, closing, signature. Use body_format 'html' (default) or 'plain'. Include placeholders {{name}}, {{email}}, {{company}}. Embed preview_text as hidden preheader when body_format is html and preview_text is non-empty."""
    db = SessionLocal()
    try:
        contacts = dataset_service.get_contacts_by_dataset(db, dataset_id)
        if not contacts:
            return "Error: This dataset has no contacts. Add a CSV with contacts before generating a campaign body."

        sample_names = [c.name for c in contacts[:5] if c.name]
        fmt = (body_format or "html").strip().lower()
        use_html = fmt != "plain" and fmt != "text"

        llm = _get_llm()
        preview_block = ""
        if use_html and preview_text.strip():
            preview_block = f"""Include at the START of the HTML (before visible content) a hidden preheader block for email clients, e.g. a div with styles like display:none; max-height:0; overflow:hidden; containing this exact preview text: {preview_text.strip()}\n\n"""

        structure = """
Required sections in order:
1) Greeting: Hello {{name}}, (or equivalent using placeholders)
2) Introduction (short)
3) Main marketing message (short paragraphs, good spacing)
4) Offer / product / announcement as fits the topic
5) Clear CTA (HTML: one prominent <a href="#">…</a> button or link; plain: a single clear "Click here: …" line)
6) Closing: Best regards, (or similar)
7) Signature line: AI Marketing Team (or similar professional sign-off)

Use placeholders {{name}}, {{email}}, {{company}} where personalization makes sense.
"""

        if use_html:
            format_instructions = f"""Return valid HTML only (no markdown fences). Use a simple email-safe layout: wrapper, optional <h1> or <h2>, <p> tags, adequate spacing, readable fonts via inline styles if needed. {preview_block}{structure}
Topic: {topic}
Subject: {subject}
Campaign type hint: {campaign_type or "infer from topic"}
Sample recipient names for tone: {", ".join(sample_names) or "valued customer"}"""
        else:
            format_instructions = f"""Return plain text only (no HTML tags). Use blank lines between paragraphs. {structure}
Topic: {topic}
Subject: {subject}
Campaign type hint: {campaign_type or "infer from topic"}
Sample recipient names for tone: {", ".join(sample_names) or "valued customer"}"""

        response = llm.invoke(format_instructions)
        return response.content.strip()
    finally:
        db.close()
