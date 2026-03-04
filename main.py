import json
import os
from typing import List, Dict, Any


class LLMOutputValidator:
    def __init__(self, forbidden_terms: List[str], min_length: int = 15):
        self.forbidden_terms = [term.lower() for term in forbidden_terms]
        self.min_length = min_length

    def validate_file(self, input_file: str, output_file: str):
        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found.")
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        results = []
        print(f"\n--- Validating {len(data)} Entries ---")

        for entry in data:
            prompt = entry.get("prompt", "N/A")
            response = entry.get("response", "")

            issues = []
            if len(response) < self.min_length:
                issues.append(f"Length too short ({len(response)} chars)")

            for term in self.forbidden_terms:
                if term in response.lower():
                    issues.append(f"Forbidden term: {term}")

            status = "PASSED" if not issues else "FAILED"
            results.append({
                "prompt": prompt,
                "status": status,
                "issues": issues
            })

            icon = "✅" if status == "PASSED" else "❌"
            print(f"{icon} Prompt: {prompt[:30]}... -> {status}")

        # save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        print(f"\nReport generated: {output_file}")


if __name__ == "__main__":
    # configuration
    FORBIDDEN = ["[strict_content_filter]", "error 404", "hatespeech"]

    validator = LLMOutputValidator(forbidden_terms=FORBIDDEN, min_length=20)
    validator.validate_file("data.json", "validation_report.json")