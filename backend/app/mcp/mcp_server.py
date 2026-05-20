from app.mcp.tools.campaign_tool import create_campaign_tool, get_campaigns_tool
from app.mcp.tools.dataset_tool import list_datasets_tool, read_dataset_tool
from app.mcp.tools.email_gen_tool import (
    generate_body_tool,
    generate_preview_text_tool,
    generate_subject_tool,
)
from app.mcp.tools.email_send_tool import send_email_campaign_tool


def get_all_tools():
    return [
        list_datasets_tool,
        read_dataset_tool,
        generate_subject_tool,
        generate_preview_text_tool,
        generate_body_tool,
        create_campaign_tool,
        get_campaigns_tool,
        send_email_campaign_tool,
    ]
