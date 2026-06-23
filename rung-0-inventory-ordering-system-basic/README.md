# Rung 0 — Inventory / Ordering Backend

## The project

Build a backend for a system that sells a **limited stock of something**: event tickets, concert seats, sneaker drops, limited inventory — your choice of domain, but the constraint must be real: **there is a finite quantity and you must never sell more than you have.**

Minimum surface:
- Create products with a stock count.
- Place an order for N units of a product (decrements stock).
- Cancel an order (restores stock).
- View a user's order history.
- View current stock for a product.

This is a backend (API + database). No frontend required. Don't build auth beyond a fake user id in a header — it's a distraction at this rung.

---

## Acceptance criteria

- [ ] Schema is normalized and modeled with real foreign keys and constraints (not everything in one table, not stock stored as a string).
- [ ] Stock can **never** go negative, even under concurrent purchases. Proven by a concurrency test, not by hoping.
- [ ] Ordering is **transactional**: an order either fully succeeds (stock decremented + order row created) or fully fails. No partial state.
- [ ] Order-history query is backed by an appropriate index; you can show the query plan before and after.
- [ ] You can articulate the isolation level you're running at and why.
- [ ] A concurrency test exists in the repo that would catch a regression of the double-sell.

---

## Reasoning questions (answer in writing, your own words)

> These are the questions an interviewer would use to find out if you actually understand your own code. "It works" is not an answer to any of them.

1. Walk through, step by step, what happens *at the database* when two requests try to buy the last unit at the same moment. What does the DB do, what does your application code do, and where exactly is the danger window?

   **Your answer:** This is called a lost update problem, where 2 concurrent transactions read the exact same data and modify it. If this modification query does not have any safeguards, you may end up with invalid data - e.g. invalid balances. How this happens is for postgres: only 1 transaction can occur at any given time per data field (FYI, all queries in postgres are a transaction as they are all wrapped in it's own tiny transaction even if you do not create one manually). In isolation level read commited, transaction 2 gets blocked and waits for transaction 1, so in situations where you have data that is of a balance type, you may have data issues that do not fulfill business logic if there are no safeguards, e.g. product stock balance going negative. 

2. How did you prevent the double-sell — `SELECT ... FOR UPDATE`, optimistic concurrency with a version column, a `CHECK`/unique constraint, an atomic `UPDATE ... WHERE stock >= n`, something else? Why that mechanism and not the others? What does your choice **cost** (throughput, lock contention, retries)?

   **Your answer:** atomic query was chosen

3. What isolation level is your database running at by default? Name one concurrency anomaly that is *possible* at that level, and say whether your design tolerates it or prevents it — and why that's the right call here.

   **Your answer: read commited. It is the default transaction isolation level, while it blocks dirty reads, it takes a new snapshot at the beginning of each SQL, which leaves transactions vulnerable to 3 major concurrency anomalies - non-repeateable reads, phantom reads and serialisation anomalies.
   
   - Non-repeateable reads -> Re-reading the same row returns updated value because another transaction commited in between
   
   - phantom reads -> Re-executing a query returns new matching rows inserted and commited by another transaction.

   - serialisation (Write skew) -> Overlapping updates violate business rule
   **

4. Show the query plan for your order-history query before and after you added the index. In plain language: what was the database doing before (and why was it slow), and what does the index let it do instead?

   **Your answer:**

5. Indexes aren't free. Describe a concrete situation in *this* system where adding an index would make overall performance **worse**. Be specific about which operation pays the cost.

   **Your answer:**

6. Suppose this system suddenly needed to handle 100× the order throughput. What breaks **first**, and why? (Answer at the level of the specific bottleneck, not "we'd add more servers.")

   **Your answer:**

---

## Learnings

1. Dockerfile is a build recipe, it describes how to build a custom image. We start FROM a base, add files, install packages, set defaults and then it outputs an image. docker-compose is a run config. It describes hwo to run containers - which image, what ports. If i'm running a stock image, there's no reason to use a Dockerfile. But i can still benefit from docker compose as I wouldnt need to always run docker run...