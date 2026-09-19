# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P5 sp4, MEM-6 growth · 2026-09-19
"""MEM-6 (canon 0003): corpus ×10, recall latency flat — measured, not
assumed. Rows are bulk-landed here (no events) because the law is about
READ latency against corpus size; the write path is proven elsewhere."""
import secrets
import statistics
import time

from orreth_spine import envelope as ev, store


def _bulk(pg, namespace, start, n):
    rows = [(namespace, f"k{start + i}",
             f"note {start + i}: " + ("lime binder cures slowly " if (start + i) % 100 == 0 else "ordinary words about the day ")
             + secrets.token_hex(6), "sha256:x", "did:orreth:agent:growth", ev.scope())
            for i in range(n)]
    with pg.transaction():
        pg.cursor().executemany(
            "INSERT INTO spine_memories (namespace, key, body, hash, by_did, scope)"
            " VALUES (%s, %s, %s, %s, %s, %s)", rows)


def _median(fn, k=7):
    ts = []
    for _ in range(k):
        t0 = time.perf_counter(); fn(); ts.append(time.perf_counter() - t0)
    return statistics.median(ts)


def test_recall_latency_stays_flat_as_the_corpus_grows_tenfold(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    st = store.OrrethStore(pg, by_did="did:orreth:agent:growth")
    ns = "growth"
    _bulk(pg, ns, 0, 1000)
    hits = st.search(ns, "lime binder cures")
    assert hits and hits[0]["rank"] > 0
    t1k_search = _median(lambda: st.search(ns, "lime binder cures"))
    t1k_within = _median(lambda: st.within(ns, "2000-01-01T00:00:00+00:00", "2100-01-01T00:00:00+00:00"))
    _bulk(pg, ns, 1000, 9000)
    pg.cursor().execute("ANALYZE spine_memories")
    t10k_search = _median(lambda: st.search(ns, "lime binder cures"))
    t10k_within = _median(lambda: st.within(ns, "2000-01-01T00:00:00+00:00", "2100-01-01T00:00:00+00:00"))
    print(f"\nMEM-6 search: 1k {t1k_search*1000:.1f} ms → 10k {t10k_search*1000:.1f} ms;"
          f" within: 1k {t1k_within*1000:.1f} ms → 10k {t10k_within*1000:.1f} ms")
    assert t10k_search < 0.08 and t10k_within < 0.08                      # sub-100 ms at 10k
    assert t10k_search < max(3 * t1k_search, 0.02)                         # flat within a bound
    assert t10k_within < max(3 * t1k_within, 0.02)
