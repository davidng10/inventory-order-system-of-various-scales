# Rung 2 — Async, Queues, Idempotency

**What this rung is really teaching:** the moment work leaves the request/response cycle, you inherit the hardest day-to-day problems in backend systems: things run more than once, run out of order, or run after a crash. Idempotency and the outbox pattern are not interview trivia — they're what stops your system from double-charging people. This rung is where "distributed thinking" actually starts.

**Prerequisite:** Rungs 0–1 complete.

---

## The project

Add asynchronous, out-of-band work to your system using a **real message broker** (Kafka if you want the vocabulary the target roles use; RabbitMQ or SQS if you want a gentler start).

Pick at least one genuinely async workflow. Good options:
- On order placement, emit an `order.placed` event; a separate consumer "sends" a confirmation (log it / write to a table — don't actually wire up email).
- A consumer that aggregates orders into a per-product sales report.
- An activity feed that fans out order events.

Requirements:
1. The producing action (placing an order) and the async work are **decoupled** through the broker.
2. The consumer must be **safe to run a message more than once** without corrupting state (idempotent).
3. Use the **outbox pattern** so an event is never lost when the DB commits but the publish fails (or vice versa).
4. You must handle a consumer crash mid-processing **correctly**.

---

## The walls (trigger these)

1. **The crash-and-redeliver.** Kill a consumer after it does the work but *before* it acks. The broker redelivers. Without idempotency, you double-process. Reproduce the double-process first, *then* fix it — you need to see the bug to trust the fix.
2. **The lost event.** Make your code commit the order to the DB and then crash *before* publishing the event (or publish then fail to commit). Show that the naive "write DB, then publish" loses or orphans events. This is what the outbox pattern exists to solve.
3. **The backlog.** Slow your consumer down (or speed up the producer) until the queue grows unbounded. Watch lag climb. Decide what to do about it.

---

## Acceptance criteria

- [ ] Producer and consumer are decoupled via a real broker.
- [ ] Consumer is idempotent: redelivering the same message produces no duplicate side effects. Proven by a test that delivers the same message twice.
- [ ] Outbox pattern implemented: events are written transactionally with the state change, then relayed to the broker. Demonstrate that a crash between commit and publish does **not** lose the event.
- [ ] You can state your delivery guarantee (at-least-once / at-most-once) and why "exactly-once" isn't really what you built.
- [ ] You've measured consumer lag and have a stated strategy for a growing backlog.

---

## Reasoning questions (answer in writing, your own words)

1. A consumer pulls a message, completes the work, and crashes **before** acking. Walk through what happens next. Is the outcome correct in your system? Why?

   **Your answer:**

2. People sell "exactly-once delivery." Argue why that's largely a myth at the messaging layer, and explain what you actually built instead to get exactly-once *effects*.

   **Your answer:**

3. Describe your idempotency key in detail: what is the key derived from, where is it stored, and what's the race if two duplicates of the same message arrive at two consumer instances at the same moment? How does your design resolve that race?

   **Your answer:**

4. Why the outbox pattern instead of just `commit order; publish event;` back to back in your handler? Walk through the specific failure the naive version has, and exactly how the outbox closes it.

   **Your answer:**

5. Your consumers are draining slower than producers are filling the queue, and lag is climbing. List your realistic options and what each one trades off. Which did you pick and why?

   **Your answer:**

6. Does **ordering** matter for your workflow? If yes, how do you preserve it (and what throughput does that cost you)? If no, how do you *know* it's safe for messages to be processed out of order?

   **Your answer:**

7. The outbox table needs to be drained to the broker by *something*. What drains it, and what happens to your guarantees if that relay process itself crashes or runs twice?

   **Your answer:**

---

## You've actually learned this rung when…

You can explain why "write to the database, then publish to the queue" is broken, draw the outbox pattern from memory, and describe the idempotency check that makes redelivery safe — and you instinctively assume every message *will* be delivered more than once.
