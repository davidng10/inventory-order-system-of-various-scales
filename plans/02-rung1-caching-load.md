# Rung 1 — Make It Survive Load

**What this rung is really teaching:** how to find a bottleneck instead of guessing at one, and that the moment you add a cache you've signed up for a consistency problem. Most engineers add caches reflexively and can't tell you what staleness their design permits. Don't be one of them.

**Prerequisite:** Rung 0 complete. You're extending that same system.

---

## The project

Take your Rung 0 inventory/ordering backend and make it hold up under read-heavy load.

1. **Load test it first, before optimizing.** Use `k6`, `wrk`, or similar. Push read traffic (product views, stock checks) until latency degrades. Record p50, p95, p99 and throughput. **You are not allowed to optimize anything you haven't measured.**
2. **Find the actual bottleneck** from the measurements + DB metrics. State it explicitly before touching it.
3. **Add Redis** as a cache-aside layer on the hot read path (e.g. product/stock reads).
4. **Re-test** and quantify the improvement with the same numbers.
5. **Break your own cache.** Deliberately construct a sequence of operations that serves a stale read. Then decide whether that staleness is acceptable for each field (stock count vs product name are *not* the same).

---

## The walls (trigger these)

1. **Cold cache stampede.** Restart Redis empty under load. Watch what hits your database. If a popular key expires and 500 requests all miss and all hit the DB at once, that's a thundering herd — observe it, then mitigate it.
2. **The stale read.** Update a product's stock, then read it from cache and get the old value. Reproduce this on purpose. Understand exactly which write path forgot to invalidate.
3. **The p99 cliff.** Your average looks fine but the tail is ugly. Find where the slow 1% is coming from.

---

## Acceptance criteria

- [ ] Documented baseline load-test numbers (p50/p95/p99, throughput) **before** caching.
- [ ] A named, measured bottleneck — not a guess.
- [ ] Redis cache-aside on the hot read path, with explicit TTLs chosen per data type and a written justification for each.
- [ ] Documented after-caching numbers showing the change.
- [ ] A written, reproducible sequence of operations that produces a stale read in your design, and a decision on whether that staleness is acceptable for that field.
- [ ] Some mitigation for cold-cache / thundering herd (e.g. request coalescing, jittered TTLs, or a documented reason you don't need it).

---

## Reasoning questions (answer in writing, your own words)

1. Where exactly did you place the cache, and why there and not one layer up or down (e.g. in front of the API vs around the DB query vs inside the application)? What did that placement decision buy you and what did it cost?

   **Your answer:**

2. Walk me through your invalidation. Give a concrete, ordered sequence of operations in *your* system that results in a client reading stale data. (If you claim there isn't one, you haven't thought hard enough — find it.)

   **Your answer:**

3. Cache-aside vs write-through vs write-behind: which did you implement, and what is the specific failure mode of each? Why was yours the right tradeoff for stock data specifically?

   **Your answer:**

4. Your Redis instance restarts and comes back empty while traffic is at peak. Walk through, second by second, what your database experiences. How did you stop it from falling over?

   **Your answer:**

5. Your p50 latency is healthy but p99 is 20× worse. Name three plausible sources of that tail latency in *this* system, and describe how you'd confirm which one it is.

   **Your answer:**

6. How did you choose your TTLs? Defend the number. What goes wrong if it's 10× too long? 10× too short?

   **Your answer:**

7. Caching stock counts is dangerous in a system whose entire point is "never oversell." Reconcile that: how do you serve fast reads from cache without the cache enabling an oversell? Where is your **source of truth** at the moment a purchase commits?

   **Your answer:**

---

## You've actually learned this rung when…

You can state, for your own system, the precise staleness window you've accepted and *why it's safe* — and you reach for measurement before optimization automatically, because you've felt how often the bottleneck isn't where you'd have guessed.
