from routing.classifier import classify, score


def test_simple_lookup_routes_light():
    r = classify("What is the capital of France?")
    assert r.route == "light"
    assert r.score < 0.5


def test_define_routes_light():
    r = classify("Define recursion in one sentence.")
    assert r.route == "light"


def test_translate_routes_light():
    r = classify("Translate 'good morning' to Spanish.")
    assert r.route == "light"


def test_complex_design_question_routes_heavy():
    r = classify(
        "Design a fault-tolerant architecture for a multi-region payments "
        "system, comparing eventual vs strong consistency trade-offs."
    )
    assert r.route == "heavy"
    assert r.score >= 0.5


def test_code_block_routes_heavy():
    prompt = "Debug this:\n```python\ndef f(x): return x/0\n```"
    r = classify(prompt)
    assert r.route == "heavy"


def test_step_by_step_routes_heavy():
    r = classify(
        "Explain step by step why my Docker container keeps OOM-killing "
        "and propose a refactor of the memory allocation strategy."
    )
    assert r.route == "heavy"


def test_long_prompt_increases_score():
    short = score("What is 2+2?")
    long = score(" ".join(["word"] * 200))
    assert long.score > short.score


def test_reasons_populated():
    r = classify(
        "Design a system and analyze the trade-offs of eventual consistency."
    )
    assert len(r.reasons) >= 1
    assert any("heavy signal" in reason or "long" in reason for reason in r.reasons)
