"""
Naive Bayes diagnoser written from scratch (standard library only).

Why Naive Bayes fits this project:
  * Evidence arrives in stages (symptoms -> medication -> tests). Bayes updates
    the disease probabilities each time, and features we haven't observed yet are
    simply left out of the calculation.
  * It is explainable: every finding has a clear push up/down on each disease.
"""
import math

from generate_data import generate
from knowledge import FEATURES


def entropy(post):
    return -sum(p * math.log2(p) for p in post.values() if p > 0)


class NaiveBayesDiagnoser:
    def __init__(self, alpha=1.0):
        self.alpha = alpha  # Laplace smoothing so no probability is ever exactly 0 or 1

    # ---------------------------------------------------------- training
    def fit(self, rows, features):
        self.features = list(features)
        self.classes = sorted({r["disease"] for r in rows})
        n = len(rows)
        counts = {c: 0 for c in self.classes}
        pos = {c: {f: 0 for f in self.features} for c in self.classes}
        for r in rows:
            c = r["disease"]
            counts[c] += 1
            for f in self.features:
                pos[c][f] += int(r[f])
        k = len(self.classes)
        self.log_prior = {c: math.log((counts[c] + self.alpha) / (n + self.alpha * k))
                          for c in self.classes}
        # p[c][f] = P(feature present | disease c), learned by counting
        self.p = {c: {f: (pos[c][f] + self.alpha) / (counts[c] + 2 * self.alpha)
                      for f in self.features} for c in self.classes}
        return self

    # ---------------------------------------------------------- inference
    def posterior(self, evidence):
        """evidence: {feature: True/False}. Unobserved features are left out."""
        logp = {}
        for c in self.classes:
            s = self.log_prior[c]
            for f, present in evidence.items():
                p = self.p[c][f]
                s += math.log(p if present else 1 - p)
            logp[c] = s
        m = max(logp.values())
        exp = {c: math.exp(v - m) for c, v in logp.items()}
        z = sum(exp.values())
        return {c: e / z for c, e in exp.items()}

    def ranked(self, evidence, top_k=None):
        post = self.posterior(evidence)
        out = sorted(post.items(), key=lambda kv: kv[1], reverse=True)
        return out[:top_k] if top_k else out

    def suggest_next(self, evidence, candidates, top_k=3):
        """Rank candidate tests/questions by expected information gain (bits):
        how much would knowing the answer shrink our uncertainty?"""
        post = self.posterior(evidence)
        h0 = entropy(post)
        out = []
        for f in candidates:
            if f in evidence:
                continue
            p_pos = sum(post[c] * self.p[c][f] for c in self.classes)
            post_pos = {c: post[c] * self.p[c][f] / p_pos for c in self.classes}
            post_neg = {c: post[c] * (1 - self.p[c][f]) / (1 - p_pos) for c in self.classes}
            expected_h = p_pos * entropy(post_pos) + (1 - p_pos) * entropy(post_neg)
            out.append((f, h0 - expected_h))
        out.sort(key=lambda kv: kv[1], reverse=True)
        return out[:top_k]

    def explain(self, evidence, disease):
        """For each finding: log-likelihood ratio for `disease` vs the other diseases.
        Positive = supports this disease, negative = argues against it."""
        others = [c for c in self.classes if c != disease]
        w = {c: math.exp(self.log_prior[c]) for c in others}
        zw = sum(w.values())
        contrib = []
        for f, present in evidence.items():
            def lik(c):
                return self.p[c][f] if present else 1 - self.p[c][f]
            p_other = sum(w[c] / zw * lik(c) for c in others)
            contrib.append((f, math.log(lik(disease) / p_other)))
        contrib.sort(key=lambda kv: abs(kv[1]), reverse=True)
        return contrib

    def possible_coinfections(self, evidence, pairs, threshold=0.20):
        """Flag disease pairs that are BOTH still plausible together (each above
        `threshold`), instead of forcing a single winner. Only pairs known to occur
        together clinically should be passed in (see knowledge.COINFECTION_PAIRS)."""
        post = self.posterior(evidence)
        found = []
        for a, b in pairs:
            if a in post and b in post and post[a] >= threshold and post[b] >= threshold:
                found.append((a, b, post[a], post[b]))
        return found


def build_model(n=6000, seed=42):
    rows = generate(n, seed)
    return NaiveBayesDiagnoser().fit(rows, FEATURES.keys())


def evaluate(model, n=3000, seed=7):
    """Accuracy on fresh synthetic patients the model never saw."""
    test = generate(n, seed)
    symptom_feats = [f for f, v in FEATURES.items() if v["kind"] == "symptom"]
    results = {}
    for name, feats in [("symptoms only", symptom_feats), ("symptoms + medication + tests", list(FEATURES))]:
        top1 = top3 = 0
        for r in test:
            ev = {f: bool(int(r[f])) for f in feats}
            ranked = [d for d, _ in model.ranked(ev)]
            top1 += ranked[0] == r["disease"]
            top3 += r["disease"] in ranked[:3]
        results[name] = (top1 / n, top3 / n)
    return results
