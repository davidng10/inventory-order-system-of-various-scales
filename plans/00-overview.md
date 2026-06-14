# Backend Mastery Ladder — Overview

**Goal:** reach a level where you can credibly design and discuss distributed-systems architecture, starting from below-junior.

**Hard rule of this ladder:** you do the rungs in order. Each project deliberately forces a wall you cannot fake past. Skipping a rung doesn't save time — it produces a project that *looks* distributed with a hollow center, which is the exact failure mode you're trying to avoid. An interviewer probing one level down finds the hole fast.

---

## The four rungs

| # | Project | Forces you to learn | Rough time @ 6–12 hrs/wk |
|---|---------|---------------------|--------------------------|
| 0 | Inventory / Ordering backend | SQL, schema modeling, transactions, ACID, isolation levels, indexes, DB-level concurrency | 3–4 wks |
| 1 | Make it survive load | Caching + invalidation, profiling, load testing, read-scaling, latency thinking | 2–3 wks |
| 2 | Async, queues, idempotency | Message brokers, delivery guarantees, idempotency, outbox pattern, backpressure | ~3 wks |
| 3 | A real distributed system | Replication, partitioning, consensus, consistency models, failure handling | 4–6 wks |

Honest total: **~12–16 weeks** to get through Rung 3 with real understanding. The only lever that speeds this up is skipping rungs, which regenerates the hollow-center problem. Don't.

---

## How to use these files

1. Read the rung's file fully **before** writing code, including the reasoning questions — they tell you what you're actually meant to understand, not just build.
2. Build to the **acceptance criteria**, and deliberately trigger the **walls**. The walls are the point. A project that never broke taught you nothing.
3. Answer the **reasoning questions in writing**, in the file, in your own words. No copy-paste from docs. If you can't answer one without looking it up, that's the gap — mark it.
4. Run the **"you've actually learned this when…"** self-test honestly.
5. Bring the file back to me. We evaluate together: I push on the answers the way an interviewer would, find the soft spots, and decide if you're ready for the next rung.

## How evaluation works

I'm not grading for "did you write words." I'm probing whether the understanding survives a follow-up. Expect me to ask "why not the other option," "what breaks at 100x," and "walk me through the failure." Vague or memorized answers get flagged, not waved through — that's the whole point of doing this with a coach instead of alone.

A rung is **passed** when you can defend your design choices under pressure, name the failure modes you *didn't* handle, and explain the tradeoffs you made. Not when the code runs.

---

## A note on stack

Pick one language you'll commit to (Go and Python are both fine; Go is closer to the systems roles you're targeting). Use **PostgreSQL** for the relational work — don't start on a NoSQL store, you need to feel relational modeling first. Everything else (Redis, a broker, etc.) gets introduced at the rung that needs it, not before.
