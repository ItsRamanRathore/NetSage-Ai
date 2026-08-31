import json
import os
import pathlib
from typing import Dict, Any

from pydantic import BaseModel
# Assuming checker.py will have a function check_rules(show_outputs: str) -> dict
try:
    from checker import check_rules
except ImportError:
    # Fallback if run directly or module path issues
    def check_rules(show_outputs: str) -> dict:
        return {"status": "OK", "errors": []}

class DiagnosticResult(BaseModel):
    root_cause: str
    osi_layer: int
    confidence: str
    evidence: str
    next_command: str
    fix_steps: list[str]

class NetSageEngine:
    def __init__(self, config_path: str = None):
        base_dir = pathlib.Path(__file__).parent.parent
        if config_path is None:
            self.config_path = base_dir / "system_config.json"
        else:
            self.config_path = pathlib.Path(config_path)
            
        self.config = self._load_config()
        self.provider = self.config.get("llm_provider", "mock")
        self.model_name = self.config.get("models", {}).get(self.provider, "mock-model")
        
        prompt_path = base_dir / "prompts" / "diagnose_prompt.md"
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.prompt_template = f.read()
        else:
            self.prompt_template = "Analyze the network issue based on:\n{symptom}\n{show_outputs}\nRespond in JSON format."

    def _load_config(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"llm_provider": "mock", "models": {"mock": "mock-model"}}

    def run_diagnosis(self, symptom: str, topology_note: str, show_outputs: str) -> Dict[str, Any]:
        # 1. Run deterministic checks first
        checker_results = check_rules(show_outputs)
        
        # 2. Prepare the prompt for LLM
        prompt = self.prompt_template.replace(
            "{symptom}", symptom
        ).replace(
            "{topology_note}", topology_note
        ).replace(
            "{show_outputs}", show_outputs
        ).replace(
            "{checker_results}", json.dumps(checker_results, indent=2)
        )
        
        # 3. Call the appropriate LLM adapter
        if self.provider == "mock":
            llm_response = self._call_mock(prompt)
        elif self.provider == "google-genai":
            llm_response = self._call_google_genai(prompt)
        elif self.provider == "openai":
            llm_response = self._call_openai(prompt)
        elif self.provider == "anthropic":
            llm_response = self._call_anthropic(prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
            
        # Try parsing JSON if it returned a string
        try:
            if isinstance(llm_response, str):
                # Simple cleanup for markdown code blocks
                if llm_response.startswith("```json"):
                    llm_response = llm_response[7:-3].strip()
                elif llm_response.startswith("```"):
                    llm_response = llm_response[3:-3].strip()
                result = json.loads(llm_response)
            else:
                result = llm_response
                
            return {
                "checker_results": checker_results,
                "ai_diagnosis": result
            }
        except Exception as e:
            return {
                "checker_results": checker_results,
                "ai_diagnosis": {"error": f"Failed to parse LLM output: {str(e)}", "raw_output": llm_response}
            }

    def _call_mock(self, prompt: str) -> dict:
        """Mock LLM adapter for testing without API keys."""
        # Simple mock logic based on keywords
        if "down" in prompt.lower() or "administratively" in prompt.lower():
            return {
                "root_cause": "Interface is administratively down.",
                "osi_layer": 1,
                "confidence": "high",
                "evidence": "Found 'administratively down' in show outputs.",
                "next_command": "show ip interface brief",
                "fix_steps": ["configure terminal", "interface <name>", "no shutdown"]
            }
        elif "vlan" in prompt.lower():
             return {
                "root_cause": "VLAN mismatch or missing VLAN.",
                "osi_layer": 2,
                "confidence": "medium",
                "evidence": "VLAN configuration seems incorrect.",
                "next_command": "show vlan brief",
                "fix_steps": ["configure terminal", "vlan <id>", "name <name>"]
            }
        
        # Default mock response
        return {
            "root_cause": "Unknown configuration issue.",
            "osi_layer": 3,
            "confidence": "low",
            "evidence": "Unable to determine from outputs.",
            "next_command": "show run",
            "fix_steps": ["Review configuration"]
        }

    def _call_google_genai(self, prompt: str) -> str:
        """Adapter for Google Gemini."""
        from google import genai
        from google.genai import types
        
        client = genai.Client()
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=self.config.get("execution_params", {}).get("temperature", 0.0),
            ),
        )
        return response.text

    def _call_openai(self, prompt: str) -> str:
        """Adapter for OpenAI."""
        from openai import OpenAI
        
        client = OpenAI() # Uses OPENAI_API_KEY env var
        response = client.chat.completions.create(
            model=self.model_name,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are an expert network troubleshooting AI. Always respond in JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.get("execution_params", {}).get("temperature", 0.0)
        )
        return response.choices[0].message.content

    def _call_anthropic(self, prompt: str) -> str:
        """Adapter for Anthropic."""
        import anthropic
        
        client = anthropic.Anthropic() # Uses ANTHROPIC_API_KEY env var
        response = client.messages.create(
            model=self.model_name,
            max_tokens=self.config.get("execution_params", {}).get("max_tokens", 1000),
            temperature=self.config.get("execution_params", {}).get("temperature", 0.0),
            system="You are an expert network troubleshooting AI. Always output raw valid JSON.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text

if __name__ == "__main__":
    # Test the mock engine
    engine = NetSageEngine("../system_config.json")
    res = engine.run_diagnosis("PC cannot ping gateway", "PC is on VLAN 10", "GigabitEthernet0/1 is administratively down, line protocol is down")
    print(json.dumps(res, indent=2))
