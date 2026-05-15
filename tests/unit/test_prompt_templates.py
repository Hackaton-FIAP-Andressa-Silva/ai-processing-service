from src.infrastructure.ai.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def test_system_prompt_is_defined():
    assert isinstance(SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT) > 0


def test_system_prompt_instructs_json_response():
    assert "JSON" in SYSTEM_PROMPT


def test_user_prompt_template_is_defined():
    assert isinstance(USER_PROMPT_TEMPLATE, str)
    assert len(USER_PROMPT_TEMPLATE) > 0


def test_user_prompt_template_contains_required_fields():
    assert "summary" in USER_PROMPT_TEMPLATE
    assert "components" in USER_PROMPT_TEMPLATE
    assert "risks" in USER_PROMPT_TEMPLATE
    assert "recommendations" in USER_PROMPT_TEMPLATE


def test_user_prompt_template_contains_severity_values():
    assert "HIGH" in USER_PROMPT_TEMPLATE
    assert "MEDIUM" in USER_PROMPT_TEMPLATE
    assert "LOW" in USER_PROMPT_TEMPLATE
