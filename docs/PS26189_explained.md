# PS 26189 — Explained Simply

**Official title:** AI-Powered Criminal Network Analysis System
**Who's asking:** Ministry of Home Affairs

---

## The problem, in one sentence

Police have tons of data about criminals, but it's scattered across different systems, and connecting the dots between suspects by hand is slow and error-prone — so build an AI system that connects those dots automatically.

---

## What data are we talking about?

Investigators already collect data from places like:

- **FIRs** (First Information Reports — the initial police complaint filed for a crime) and police reports
- **CDRs** (Call Detail Records — logs of who called who, when, for how long)
- Financial transaction records (bank transfers, payments)
- Surveillance reports
- Social media intelligence
- Criminal history databases
- Intelligence agency reports

The problem isn't that this data doesn't exist — it's that it's **fragmented** (spread across many different systems), **unstructured** (free-text reports, not neat spreadsheets), and nobody can manually read through all of it to spot patterns.

## What's the actual pain point?

Imagine an investigator has 50 documents about a case — FIRs, call logs, witness statements. Somewhere buried in there, Suspect A (in document #3) and Suspect B (in document #41) both called the same phone number, or were both seen at the same location. A human would have to read every single document and remember every name/number/place to catch that. That's exactly the kind of connection that gets missed today.

## What are we asked to build?

An AI system that does this automatically. Specifically, it needs to:

1. **Take in data from multiple sources** — the documents/records listed above
2. **Pull out the important "things" mentioned in the data** (this is called *entity extraction*) — specifically:
   - People (names)
   - Locations
   - Vehicles
   - Phone numbers
   - Organizations
3. **Figure out how those things are connected** and draw a relationship map — e.g. "Person A called Person B," "Person A was seen at Location X," "Vehicle Y is registered to Person C"
4. **Point out the important people** in the network — i.e., not everyone in a criminal network matters equally; some people are central hubs connecting many others (think: a gang leader vs. a low-level courier)
5. **Notice suspicious or unusual patterns** — e.g. an unusually high number of calls right before a crime, or repeated visits to the same location
6. **Show all of this to investigators in a useful way** — visually (like a network graph) and with clear explanations, not just raw data dumps

## In plain terms, what does the final product look like?

Picture this: an investigator uploads a stack of case documents. The system reads through everything, automatically identifies every person/phone/vehicle/location mentioned, and draws a graph showing how they're all connected — with the most "important" people in the network visually standing out. Click on any connection and it shows you exactly which document that connection came from. The system might also say "hey, this pattern looks unusual, you should look into it."

## Why this matters for judging

Two things the PS keeps repeating that are easy to skim past but matter a lot:

- **"Assist investigators"** — not replace them. The AI surfaces leads and connections; a human still makes the call. Any solution that acts like a black-box verdict machine is missing the point.
- **"Actionable intelligence"** — the output shouldn't just be a pretty graph. It should help an investigator decide what to actually do next.
