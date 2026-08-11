"""
Complexity classifier: decides whether a prompt should go to the light
(fast/cheap) model or the heavy (capable) model.

Stage 1 (here): heuristic scoring — fast to build, gives you a working
end-to-end pipeline on day 1.

Stage 2 (TODO once you have traffic/labels): replace `score()` with a small
trained classifier (e.g. logistic regression or a distilled sentence
embedding classifier) trained on prompts you've manually labeled light/heavy
from your own usage logs. That's the "ML" half of "Hybrid ML+LLM Router" —
don't skip it, it's the differentiator over a pure keyword heuristic.
"""

from dataclasses import dataclass
import re

# Signals that suggest a prompt needs deeper reasoning / the heavy model
HEAVY_SIGNAL_PATTERNS = [
    r"\bwhy\b", r"\banalyz", r"\bcompare\b", r"\bdesign\b", r"\barchitect",
    r"\bdebug\b", r"\bexplain\b.*\bstep by step\b", r"\bproof\b",
    r"\btrade-?off", r"\brefactor\b", r"\boptimi[sz]e\b", r"\bplan\b",
]

# Signals that suggest the prompt is simple lookup/formatting work
LIGHT_SIGNAL_PATTERNS = [
    r"^\s*what is\b", r"^\s*define\b", r"^\s*translate\b",
    r"^\s*summar(y|ize) in one", r"^\s*format\b", r"^\s*list\b",
]


@dataclass
class ComplexityResult:
    score: float          # 0.0 (trivial) -> 1.0 (very complex)
    route: str            # "light" or "heavy"
    reasons: list[str]


def score(prompt: str) -> ComplexityResult:
    reasons = []
    s = 0.0

    # Length signal — long prompts tend to need more reasoning/context
    length = len(prompt.split())
    if length > 150:
        s += 0.35
        reasons.append(f"long prompt ({length} words)")
    elif length < 15:
        s -= 0.15
        reasons.append(f"short prompt ({length} words)")

    lowered = prompt.lower()

    for pat in HEAVY_SIGNAL_PATTERNS:
        if re.search(pat, lowered):
            s += 0.2
            reasons.append(f"heavy signal: /{pat}/")

    for pat in LIGHT_SIGNAL_PATTERNS:
        if re.search(pat, lowered):
            s -= 0.2
            reasons.append(f"light signal: /{pat}/")

    # Code blocks / multi-step instructions usually warrant the heavy model
    if "```" in prompt or re.search(r"\bstep \d\b", lowered):
        s += 0.25
        reasons.append("contains code block or multi-step instructions")

    s = max(0.0, min(1.0, s + 0.5))  # recenter around 0.5 baseline, clamp

    return ComplexityResult(score=s, route="pending", reasons=reasons)


def classify(prompt: str, threshold: float = 0.5) -> ComplexityResult:
    result = score(prompt)
    result.route = "heavy" if result.score >= threshold else "light"
    return result


if __name__ == "__main__":
    tests = [
        "What is the capital of France?",
        "Explain step by step why my Docker container keeps OOM-killing "
        "and propose a refactor of the memory allocation strategy.",
        "Translate 'good morning' to Spanish.",
        "Design a fault-tolerant architecture for a multi-region payments "
        "system, comparing eventual vs strong consistency trade-offs.",
    ]
    for t in tests:
        r = classify(t)
        print(f"[{r.route:5}] score={r.score:.2f}  {t[:60]!r}")
        for reason in r.reasons:
            print(f"          - {reason}")
