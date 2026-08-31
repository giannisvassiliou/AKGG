class GapService:
    def rank_gaps(self, domain_graph: dict, mastery: dict, misconceptions: dict | None = None):
        misconceptions = misconceptions or {}
        concepts = domain_graph.get("concepts", [])
        relations = domain_graph.get("relations", [])
        incoming_prereqs = {}
        outgoing = {}
        for r in relations:
            outgoing.setdefault(r["source"], []).append(r["target"])
            if r.get("type") == "prerequisite":
                incoming_prereqs.setdefault(r["target"], []).append(r["source"])

        rows = []
        for c in concepts:
            cid = c["id"]
            m = float(mastery.get(cid, 0.0))
            prereqs = incoming_prereqs.get(cid, [])
            prereq_gap = 0.0
            weak_prereqs = []
            for p in prereqs:
                pm = float(mastery.get(p, 0.0))
                if pm < 0.6:
                    weak_prereqs.append(p)
                    prereq_gap += 1 - pm
            prereq_gap = prereq_gap / max(1, len(prereqs))
            misconception_penalty = min(0.25, len(misconceptions.get(cid, [])) * 0.08)
            centrality = min(0.2, len(outgoing.get(cid, [])) * 0.05)
            priority = (1 - m) * 0.60 + prereq_gap * 0.25 + float(c.get("difficulty", 0.5)) * 0.10 + misconception_penalty + centrality
            status = "mastered" if m >= 0.8 else "developing" if m >= 0.45 else "gap"
            rows.append({
                "concept_id": cid,
                "name": c.get("name", cid),
                "region": c.get("region", ""),
                "mastery": round(m, 2),
                "difficulty": c.get("difficulty", 0.5),
                "priority": round(priority, 3),
                "weak_prerequisites": weak_prereqs,
                "misconceptions": misconceptions.get(cid, []),
                "status": status,
            })
        return sorted(rows, key=lambda x: x["priority"], reverse=True)

gap_service = GapService()
