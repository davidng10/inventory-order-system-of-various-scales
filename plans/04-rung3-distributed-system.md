# Rung 3 — A Real Distributed System

**What this rung is really teaching:** everything before this was one logical service getting more robust. Now there are *multiple nodes that must agree while some of them fail*. The defining requirement of this rung — and the line between "distributed system" and "a server with extra steps" — is: **a node dies and the system stays correct.** This is the rung the roles you're targeting actually test.

**Prerequisite:** Rungs 0–2 complete. If you skipped here, stop. You will build something that demos and collapses under the first real question.

---

## The project — pick ONE

Each forces the core distributed concepts through a different door. Pick the one that appeals; you only need one done *well*.

### Option A — Distributed rate limiter
A rate-limiting service that enforces a **global** limit (e.g. 100 req/s per API key) across N stateless app nodes. The hard part: the limit is global but you have no single chokepoint. Forces shared state, consistency vs latency tradeoffs, and approximate-vs-exact counting.

### Option B — Mini replicated key-value store (the strong signal)
A small KV store replicated across 3+ nodes with **leader election and log replication** — a toy Raft. Writes go through a leader; followers replicate; a node can die and the cluster keeps serving correctly. Forces consensus, replication, leader election, split-brain prevention. This is the project that most credibly says "I understand distributed systems."

### Option C — Consistent-hashing cache cluster
A cache sharded across N nodes via consistent hashing, where adding/removing a node moves only a fraction of keys. Forces partitioning, rebalancing, and why naive `hash(key) % N` is a disaster when N changes.

---

## The walls (trigger these — non-negotiable)

1. **Kill a node under load.** Not "assume it works" — actually terminate a node mid-traffic and observe whether the system stays correct. Record the exact window, if any, where clients saw wrong/stale/failed results.
2. **Partition the network.** Simulate two halves that can't talk. Observe what each side does. This is where you find out what consistency/availability choice you *actually* made (vs the one you intended).
3. **(B only) Force a leader failure.** Kill the leader. Watch the election. Confirm two nodes never both act as leader.
4. **(C only) Add/remove a node mid-traffic.** Measure how many keys actually moved and whether in-flight reads broke.

---

## Acceptance criteria

- [ ] System runs across **3+ nodes** (containers/processes are fine).
- [ ] Survives the death of at least one node without losing correctness — **demonstrated**, with the failure injected and the behavior recorded.
- [ ] You can state precisely where your system sits on the consistency/availability spectrum **when the network partitions**, and what a client on each side experiences.
- [ ] A documented failure-injection test (you killed something real and wrote down what happened).
- [ ] (B) Leader election works and split-brain is prevented — shown, not asserted.
- [ ] (C) Node join/leave moves only a bounded fraction of keys — measured.

---

## Reasoning questions (answer in writing, your own words)

> General questions apply to all options. Then answer the block for your chosen option.

**General**

1. A node dies mid-operation. Walk through, step by step, what your system does. What is the **worst-case window** in which a client could see incorrect or stale data, and how long is it?

   **Your answer:**

2. The network partitions. Where does your system land on consistency vs availability, and what does a client on the *losing* side of the partition actually experience — an error, a stale read, a hang? Was that a deliberate choice or an accident you discovered during testing?

   **Your answer:**

3. How did you *test* failure? Did you actually kill nodes and partition the network under load, or reason about it? Describe what you injected and what you observed — including anything that surprised you.

   **Your answer:**

4. What is the single biggest lie your system tells — the failure mode you *know* exists but didn't handle? (Every system has one. Not naming it is the red flag.)

   **Your answer:**

---

**If you built A (rate limiter)**

5A. Your limit is 100 req/s, global, across 5 nodes. How do you enforce it without a single counter becoming the bottleneck? What's the tradeoff between accuracy (never exceeding 100) and latency/throughput?

   **Your answer:**

6A. Under partition, would your limiter rather *over-admit* (allow more than 100) or *under-admit* (block legitimate traffic)? Which did you choose and why is that right for a rate limiter specifically?

   **Your answer:**

---

**If you built B (replicated KV / Raft)**

5B. Explain leader election in your implementation. What triggers it, and how long is the cluster unavailable for writes during one?

   **Your answer:**

6B. Two nodes both believe they're leader (split brain). Walk through how your design makes this impossible — or, if it's possible, what damage it does and why you accepted that.

   **Your answer:**

7B. A write is acknowledged to the client, then the leader crashes before replicating it. Is that write durable? Walk through exactly what your replication/commit rules guarantee about acknowledged writes.

   **Your answer:**

---

**If you built C (consistent hashing)**

5C. A node joins the cluster. Roughly how many keys move, and why is that dramatically better than `hash(key) % N`? Walk through what `% N` does when N goes from 4 to 5.

   **Your answer:**

6C. What do virtual nodes solve, and what goes wrong with plain consistent hashing without them?

   **Your answer:**

---

## You've actually learned this rung when…

You can stand at a whiteboard, sketch your system, and when someone says "okay, this node just died" you can trace exactly what happens and name the consistency guarantee that holds (and the one that doesn't) — without reaching for a memorized diagram. That's the thing the interviews are actually testing, and now you'll have built it instead of read about it.
