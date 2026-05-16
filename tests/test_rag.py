from cryptox_agent.rag import KnowledgeBase


def test_ingest_and_search(tmp_path):
    doc = tmp_path / "airdrop.md"
    doc.write_text("Airdrop checklist: official docs, funding, testnet, and sybil rules.", encoding="utf-8")
    kb = KnowledgeBase(str(tmp_path / "rag.sqlite"))

    assert kb.ingest_paths([str(tmp_path)]) == 1
    hits = kb.search("airdrop")

    assert hits
    assert "airdrop.md" in hits[0][0]
