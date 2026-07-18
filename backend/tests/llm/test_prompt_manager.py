import pytest
import json
from llm.prompt_manager import PromptManager
from llm.schemas import CourseBlueprintResponse

def test_prompt_manager_build():
    schema_json = CourseBlueprintResponse.model_json_schema()
    prompt = PromptManager.build(
        "course_blueprint", 
        document_context="Test Document Context",
        schema=json.dumps(schema_json)
    )
    
    assert "Test Document Context" in prompt
    assert "Generate a descriptive course title" in prompt
    assert "YOUR JSON OUTPUT SCHEMA:" in prompt
    assert "CourseBlueprintResponse" in prompt

def test_prompt_manager_invalid():
    with pytest.raises(ValueError):
        PromptManager.build("invalid_prompt")
