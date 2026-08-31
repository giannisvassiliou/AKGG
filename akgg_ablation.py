"""
AKGG selection-policy ablation --- supplementary script for Section 5.7.

Reproduces Table "Agreement with the full priority policy", the simulated-session
figures and the sensitivity table. Deterministic given the seeds below.
Run:  python3 akgg_ablation.py > results.json

Does the five-term priority score of Eq. (3) ever select a different concept
from the trivial rule "among eligible concepts, pick the one with the lowest
mastery"?  All policies share the same eligibility gating and the same
FILTER(?mastery < 0.8) restriction; ties break on concept index everywhere.
"""

import json
import numpy as np

PROG = {
    "name": "Introductory Programming",
    "concepts": {"variables": 0.20, "data_types": 0.30, "conditionals": 0.45,
                 "loops": 0.55, "functions": 0.65, "oop": 0.85},
    "prereq": [("variables", "data_types"), ("data_types", "conditionals"),
               ("conditionals", "loops"), ("variables", "functions"),
               ("loops", "functions"), ("functions", "oop")],
}

DB = {
    "name": "Database Systems (synthetic, 12 concepts)",
    "concepts": {"relational_model": 0.20, "keys": 0.30, "sql_select": 0.35,
                 "filtering": 0.40, "joins": 0.60, "aggregation": 0.55,
                 "subqueries": 0.70, "normalisation": 0.65, "indexing": 0.70,
                 "transactions": 0.75, "concurrency": 0.85, "query_optim": 0.90},
    "prereq": [("relational_model", "keys"), ("relational_model", "sql_select"),
               ("sql_select", "filtering"), ("keys", "joins"),
               ("filtering", "joins"), ("filtering", "aggregation"),
               ("joins", "subqueries"), ("aggregation", "subqueries"),
               ("keys", "normalisation"), ("joins", "indexing"),
               ("indexing", "query_optim"), ("subqueries", "query_optim"),
               ("relational_model", "transactions"),
               ("transactions", "concurrency")],
}

W_M, W_P, W_D = 0.60, 0.25, 0.10
T_WEAK, T_GATE, T_MASTERED = 0.60, 0.65, 0.80


class Domain:
    def __init__(self, spec):
        self.name = spec["name"]
        self.ids = list(spec["concepts"])
        self.idx = {c: i for i, c in enumerate(self.ids)}
        self.n = len(self.ids)
        self.d = [spec["concepts"][c] for c in self.ids]
        self.pre = [[] for _ in self.ids]
        self.outdeg = [0] * self.n
        for p, c in spec["prereq"]:
            self.pre[self.idx[c]].append(self.idx[p])
            self.outdeg[self.idx[p]] += 1
        self.cent = [min(0.20, o * 0.05) for o in self.outdeg]
        self.order = self._topo()

    def _topo(self):
        seen, order = set(), []

        def visit(i):
            if i in seen:
                return
            seen.add(i)
            for p in self.pre[i]:
                visit(p)
            order.append(i)

        for i in range(self.n):
            visit(i)
        return order


def components(dom, m, misc, t_weak=T_WEAK):
    cm = [0.0] * dom.n
    cp = [0.0] * dom.n
    cf = [0.0] * dom.n
    for i in range(dom.n):
        tot = 0.0
        k = 0
        for p in dom.pre[i]:
            mp = m[p]
            if mp < t_weak:
                tot += 1.0 - mp
                k += 1
        cm[i] = 1.0 - m[i]
        cp[i] = tot / k if k else 0.0
        cf[i] = min(0.25, misc[i] * 0.08)
    return cm, cp, cf


def eligible(dom, m, t_gate=T_GATE):
    out = []
    for i in range(dom.n):
        if m[i] >= T_MASTERED:
            continue
        ok = True
        for p in dom.pre[i]:
            if m[p] < t_gate:
                ok = False
                break
        if ok:
            out.append(i)
    return out


OPTS = {"full": {}, "nocent": {"cent": 0.0}, "nomisc": {"misc": 0.0},
        "nodiff": {"wd": 0.0}, "nopre": {"wp": 0.0}}


def pick(dom, m, misc, policy, comp=None, elig=None, t_gate=T_GATE,
         wm=W_M, wp=W_P, wd=W_D, cent=1.0, miscw=1.0, t_weak=T_WEAK):
    if elig is None:
        elig = eligible(dom, m, t_gate)
    if not elig:
        return None, elig
    if policy == "mastery":
        best = min((m[i], i) for i in elig)
        return best[1], elig
    o = OPTS.get(policy, {})
    wm = o.get("wm", wm)
    wp = o.get("wp", wp)
    wd = o.get("wd", wd)
    cent = o.get("cent", cent)
    miscw = o.get("misc", miscw)
    if comp is None:
        comp = components(dom, m, misc, t_weak)
    cm, cp, cf = comp
    bs, bi = None, None
    for i in elig:
        s = wm * cm[i] + wp * cp[i] + wd * dom.d[i] + miscw * cf[i] + cent * dom.cent[i]
        if bs is None or s > bs + 1e-12:
            bs, bi = s, i
    return bi, elig


def sample_state(dom, rng, consistent, misc_rate):
    m = rng.random(dom.n)
    if consistent:
        for i in dom.order:
            if dom.pre[i]:
                m[i] = m[i] * min(m[p] for p in dom.pre[i])
    misc = rng.poisson(misc_rate, dom.n) if misc_rate > 0 else np.zeros(dom.n, int)
    return list(m), list(misc)


def experiment1(dom, n=100_000, seed=7, misc_rate=0.0, consistent=True):
    rng = np.random.default_rng(seed)
    pols = ["mastery", "nocent", "nomisc", "nodiff", "nopre"]
    agree = {p: 0 for p in pols}
    agree_c = {p: 0 for p in pols}
    dec = con = 0
    esz = 0
    for _ in range(n):
        m, misc = sample_state(dom, rng, consistent, misc_rate)
        comp = components(dom, m, misc)
        elig = eligible(dom, m)
        base, _ = pick(dom, m, misc, "full", comp, elig)
        if base is None:
            continue
        dec += 1
        esz += len(elig)
        multi = len(elig) > 1
        con += multi
        for p in pols:
            q, _ = pick(dom, m, misc, p, comp, elig)
            if q == base:
                agree[p] += 1
                if multi:
                    agree_c[p] += 1
    return {"decisions": dec, "mean_eligible": esz / dec,
            "contested_frac": con / dec, "n_contested": con,
            "agreement_all": {p: agree[p] / dec for p in pols},
            "agreement_contested": {p: agree_c[p] / con for p in pols}}


def p_success(d, m):
    return float(np.clip(0.80 - 0.45 * d + 0.35 * m, 0.05, 0.95))


def trajectory(dom, policy, seed, max_q=400):
    rng = np.random.default_rng(seed)
    m = [0.0] * dom.n
    for i in range(dom.n):
        if not dom.pre[i]:
            m[i] = float(rng.uniform(0.3, 0.9))
    misc = [0] * dom.n
    seq = []
    for _ in range(max_q):
        i, _ = pick(dom, m, misc, policy)
        if i is None:
            break
        seq.append(i)
        ok = rng.random() < p_success(dom.d[i], m[i])
        m[i] = min(1.0, m[i] + (0.25 if ok else 0.08))
        if not ok and rng.random() < 0.5:
            misc[i] += 1
    return seq


def experiment2(dom, runs=3000, seed0=101):
    first = same = 0
    div = []
    lf = []
    lm = []
    for r in range(runs):
        a = trajectory(dom, "full", seed0 + r)
        b = trajectory(dom, "mastery", seed0 + r)
        lf.append(len(a))
        lm.append(len(b))
        if a and b and a[0] == b[0]:
            first += 1
        if a == b:
            same += 1
        else:
            k = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
            if k is not None:
                div.append(k)
    return {"runs": runs, "identical_first_choice": first / runs,
            "identical_full_sequence": same / runs,
            "median_first_divergence_step": float(np.median(div)) if div else None,
            "mean_quests_full": float(np.mean(lf)),
            "mean_quests_mastery": float(np.mean(lm))}


def experiment3(dom, n=30_000, seed=11, misc_rate=0.35):
    rng = np.random.default_rng(seed)
    states = [sample_state(dom, rng, True, misc_rate) for _ in range(n)]

    def agr(**kw):
        s = 0
        for m, misc in states:
            elig = eligible(dom, m, kw.get("t_gate", T_GATE))
            a, _ = pick(dom, m, misc, "full", None, elig)
            b, _ = pick(dom, m, misc, "full", None, elig, **kw)
            if a == b:
                s += 1
        return s / n

    out = {}
    for name, kw in [("wm 0.60->0.40", {"wm": 0.40}), ("wm 0.60->0.80", {"wm": 0.80}),
                     ("wp 0.25->0.10", {"wp": 0.10}), ("wp 0.25->0.40", {"wp": 0.40}),
                     ("wd 0.10->0.00", {"wd": 0.00}), ("wd 0.10->0.30", {"wd": 0.30}),
                     ("t_weak 0.60->0.50", {"t_weak": 0.50}),
                     ("t_weak 0.60->0.70", {"t_weak": 0.70})]:
        out[name] = agr(**kw)
    return out


if __name__ == "__main__":
    res = {}
    for spec in (PROG, DB):
        dom = Domain(spec)
        res[dom.name] = {
            "e1_no_misc": experiment1(dom, misc_rate=0.0),
            "e1_with_misc": experiment1(dom, misc_rate=0.35),
            "e1_unconstrained": experiment1(dom, misc_rate=0.35, consistent=False),
            "e2": experiment2(dom),
            "e3": experiment3(dom),
        }
    print(json.dumps(res, indent=2))
