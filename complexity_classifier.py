"""
Loads the trained classifier and exposes a `classify()` function to drop
into main.py's routing logic, replacing the `len(prompt) > 80` check.

Usage in main.py:

    from complexity_classifier import classify

    route = classify(prompt)   # returns "light" or "heavy"
    model = "gpt-4o" if route == "heavy" else "llama-3.1-8b"

If you want the confidence score too (nice to show in the Proof Ledger):

    route, confidence = classify(prompt, return_confidence=True)
"""

import joblib
from pathlib import Path

_MODEL_PATH = Path(__file__).parent / "complexity_classifier.joblib"
_pipeline = None  # lazy-loaded so importing this module is cheap


def _load():
    global _pipeline
    if _pipeline is None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(
                f"{_MODEL_PATH} not found. Run `python train_classifier.py` first."
            )
        _pipeline = joblib.load(_MODEL_PATH)
    return _pipeline


def classify(prompt: str, return_confidence: bool = False):
    pipeline = _load()
    proba = pipeline.predict_proba([prompt])[0]  # [P(light), P(heavy)]
    heavy_confidence = proba[1]
    route = "heavy" if heavy_confidence >= 0.5 else "light"

    if return_confidence:
        confidence = heavy_confidence if route == "heavy" else proba[0]
        return route, round(float(confidence), 3)
    return route


if __name__ == "__main__":
    # Sanity-check on cases a pure length threshold gets wrong:
    # short-but-hard, and long-but-easy.
    tricky_cases = [
        ("Why does this recursive function overflow?", "heavy",
         "short but genuinely hard — a length check would send this light"),
        ("Please kindly could you possibly tell me, if you don't mind, "
         "what the capital city of France happens to be?", "light",
         "long but trivial — a length check would send this heavy"),
        ("What is the capital of France?", "light", "baseline light"),
        ("Design a fault-tolerant multi-region payments architecture.",
         "heavy", "baseline heavy"),
    ]

    print(f"{'expected':8} {'got':8} {'conf':6}  prompt")
    print("-" * 70)
    correct = 0
    for prompt, expected, note in tricky_cases:
        route, conf = classify(prompt, return_confidence=True)
        mark = "✓" if route == expected else "✗"
        correct += route == expected
        print(f"{expected:8} {route:8} {conf:<6} {mark}  {prompt[:50]}...  ({note})")

    print(f"\n{correct}/{len(tricky_cases)} tricky cases correct")
