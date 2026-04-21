import json
import os
import logging
from typing import List, Dict, Any

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("output-guard")


class LLMOutputValidator:
    """
    Validator for checking LLM responses against safety and quality rules.
    It processes JSON files and generates a detailed validation report.
    """

    def __init__(self, forbidden_terms: List[str], min_length: int = 15):
        self.forbidden_terms = [term.lower() for term in forbidden_terms]
        self.min_length = min_length

    # Core validation pipeline: load → validate → report
    def validate_file(self, input_file: str, output_file: str):
        """
        Reads an input JSON, checks each entry for forbidden terms or length issues,
        and saves the results to a report file.
        """
        if not os.path.exists(input_file):
            logger.error(f"Input file {input_file} not found.")
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        results = []
        logger.info(f"Starting validation for {len(data)} entries.")

        for entry in data:
            prompt = entry.get("prompt", "N/A")
            response = entry.get("response", "")

            issues = []
            # avoid too short / meaningless responses
            if len(response) < self.min_length:
                issues.append(f"Length too short ({len(response)} chars)")

            # simple keyword check (can improve later with smarter logic)
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
            logger.info(f"{icon} Prompt: {prompt[:30]}... -> Status: {status}")

        # save results so I can review them later
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)

        logger.info(f"Validation report successfully generated: {output_file}")


if __name__ == "__main__":
    # basic config for testing
    FORBIDDEN = ["[strict_content_filter]", "error 404", "hatespeech"]

    validator = LLMOutputValidator(forbidden_terms=FORBIDDEN, min_length=20)

    validator.validate_file("data.json", "validation_report.json")