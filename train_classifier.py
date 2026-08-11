"""
Trains a lightweight logistic regression classifier on TF-IDF features to
replace the "prompt length > 80 chars" heuristic in main.py's router.

Why TF-IDF + logistic regression (not a downloaded embedding model):
- Zero external downloads — trains in under a second on CPU, no model
  weights to fetch, no dependency beyond scikit-learn. Anyone cloning the
  repo can retrain instantly, which matters for a demo.
- Fully interpretable — you can inspect clf.coef_ against the vectorizer's
  vocabulary to show exactly which words push a prompt toward "heavy"
  (e.g. "refactor", "trade-off", "architecture"). Great for a README
  screenshot or interview answer about how the model actually decides.
- Good enough for this task: routing is a coarse binary decision, not a
  task that needs semantic nuance the way search/RAG does.

If you later want the classifier to generalize better to phrasings it's
never seen (semantic similarity, not just shared vocabulary), swap the
TfidfVectorizer for sentence-transformers embeddings — same
LogisticRegression downstream, just a different feature extractor. Left
as a clearly-labeled upgrade path rather than the default, since it adds a
model-download dependency for a fairly small accuracy gain at this dataset
size.

Usage:
    python train_classifier.py

Outputs:
    complexity_classifier.joblib   <- load this at inference time
"""

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from training_data import LABELED_EXAMPLES

MODEL_OUT = "complexity_classifier.joblib"


def main():
    prompts = [p for p, _ in LABELED_EXAMPLES]
    labels = [1 if lbl == "heavy" else 0 for _, lbl in LABELED_EXAMPLES]
    y = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        prompts, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training on {len(X_train)} examples, evaluating on {len(X_test)}...")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),   # unigrams + bigrams catch phrases like "step by step"
            min_df=1,
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    pipeline.fit(X_train, y_train)

    print("\n--- Held-out evaluation ---")
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["light", "heavy"]))

    # Retrain on 100% of labeled data for the deployed model once the
    # held-out numbers above look reasonable.
    pipeline_final = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    pipeline_final.fit(prompts, y)

    joblib.dump(pipeline_final, MODEL_OUT)
    print(f"\nSaved trained classifier to {MODEL_OUT}")

    # Show the most heavy/light-indicative terms — useful for your README
    tfidf = pipeline_final.named_steps["tfidf"]
    clf = pipeline_final.named_steps["clf"]
    vocab = np.array(tfidf.get_feature_names_out())
    coefs = clf.coef_[0]
    top_heavy = vocab[np.argsort(coefs)[-10:]]
    top_light = vocab[np.argsort(coefs)[:10]]
    print(f"\nTop terms -> heavy: {list(top_heavy)}")
    print(f"Top terms -> light: {list(top_light)}")


if __name__ == "__main__":
    main()

