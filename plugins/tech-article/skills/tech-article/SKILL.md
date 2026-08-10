---
name: tech-article
description: >-
  Use when the user is writing or publishing a technical blog article that should read like a human
  engineer wrote it, not an AI. A story-first method — open on a real problem, keep opinions sharp,
  cut AI-slop phrasing, control sentence rhythm, and add a diagram only when it earns its place.
  Trigger on "write a blog article", "draft a dev post", "turn this into an article", "make this
  not sound like AI", even when the word "article" never appears. NOT for documentation, READMEs,
  or reference pages.
---

# Tech Article — write a post that doesn't read like AI

## The one rule

A technical article is **a story that contains technique**, not technique that tells a story. Open on the human problem (the bug, the outage, the bad call), tell what actually happened, then slide the technique inside. If the reader wants to know what happens next, you have won. If they bounce at the first code block, you lost on line one.

## Structure

- **Hook (no heading)** — in medias res. A vivid, real moment. "The program had been running for three days. Memory was creeping up." Never "In this article we'll see...".
- **Body — 4 to 6 H2 sections**, each 1-4 short paragraphs and, when it earns it, one code block. H2s are fragments, not questions: "The four leaks that always bite", "Why the stdlib was enough". The pattern that works: bad code (✗) then fixed code (✓), back to back.
- **Conclusion (H2)** — short. NOT a recap. A meta-observation or the surprising lesson. "The value wasn't in writing the code. It was in the third security review."

## Voice

- Direct, lightly ironic, self-deprecating about your own mistakes.
- Talk to the reader as a peer engineer, not a beginner to lecture.
- Sharp opinions, never hedged: "this is better because X", not "one might consider...".
- Concrete: real numbers, real tool names, a lived situation. Never invent a stat or an incident.
- Contrast of rhythm: short sentences to hit, medium ones to carry an argument. Read it aloud. If you stumble, cut. If it stutters, join.

## Kill the AI-slop (the part that matters most)

These phrasings scream "an LLM wrote this". Cut them on sight. The tells are per-language, so here are both English and French.

- **English**: "It's important to note", "It's worth mentioning", "Moreover, / Furthermore, / Additionally,", "In today's fast-paced world", "Let's dive in", "In conclusion, here are the key takeaways", "By leveraging", and "robust / seamless / powerful" used as filler.
- **French**: "Il est important de noter", "Il convient de mentionner", "De plus, / En outre, / Par ailleurs,", "Par conséquent," (use "Du coup,"), "Dans le cadre de", "Comme nous l'avons vu précédemment" (just cut), "Il faut noter que" (just say the thing), "En résumé, voici les points clés" (the conclusion is an observation, not a recap), "permettre de" on a loop (vary: aide à, sert à, évite de…).
- **Bulleting everything.** Keep prose when the text has flow. A list is for three or more genuinely parallel items, not for hiding a sentence.
- The mechanical "it's not X, it's Y" used on repeat.
- Generic openers ("Today, with the rise of...") — start in the middle of the action instead.
- **Typography per locale.** In French, no em-dash (—): replace with ":", ",", or a new sentence. Respect your own language's conventions.
- **Semicolon enumerations.** Three clauses glued by ";" are not a sentence, they are a list pretending to be one. Rewrite as real sentences, often as a small escalation.

## Fluency mechanics (why a paragraph reads smooth, research-grounded)

The first two are the biggest levers — they are what makes a reader never re-read a paragraph.

1. **Old then new.** Every sentence STARTS on information already known and ENDS on the new information. The last word of one sentence seeds the next. A "choppy" paragraph is almost always this rule, broken.
2. **The strong word goes at the END.** The end of a sentence carries the natural emphasis. Do not waste it on a date or a circumstantial clause.
3. Subject and verb stay close. More than 8-10 words between them, split the sentence.
4. Free the buried verb: "perform an installation of" becomes "install".
5. Show before you name: the example or the minimal code before the formal definition.
6. Point, don't announce: delete "In this section we'll look at...", just say the thing.
7. One concept, one word, everywhere. Never rename a technical term for elegance.

## Self-contained — non-negotiable

The article must be readable by someone who has read nothing else you wrote. Define every internal term, tool name, or concept before using it. If the article is a sequel, say so explicitly and summarize the prerequisite in one sentence. Never assume the reader knows the context, the previous article, or the project.

Minimum text, maximum value. After the draft, cut half the words without losing meaning. Any sentence you can remove without the paragraph collapsing was filler. No flourish you cannot back with a concrete detail. Do not restate the intro inside the concept, or the concept inside the conclusion.

## Diagrams — only when they earn it

Add a diagram (SVG or image) when the idea is **spatial, sequential, or abstract** and the visual makes it land faster than prose: a data flow, an architecture, a state machine, a call chain, a before/after, a cycle. Never decorative. The test: if hiding the prose makes the diagram teach nothing a sentence wouldn't, drop it. Give it generous spacing (no text overlapping a shape, nothing past the viewBox) and verify the render at a narrow and a wide width, because generated coordinates are often wrong.

## SEO basics (without writing for robots)

- One or two precise long-tail queries per article, no more.
- The keyword appears naturally in the title, the meta description (150-160 chars, answering a real question), the H1, the first paragraph, and at least one H2.
- Slug: keyword first, lowercase, hyphens, 3-6 words, no date.
- Internal links with descriptive anchors, never "click here".
- At least one image with a descriptive alt.

## Workflow

1. Write the article directly. No intermediate brainstorm or outline dump: the structure above IS the outline.
2. Run the AI-slop pass and the essential-oil cut on the draft.
3. Read it aloud once, for rhythm.
4. Adapt the output to your platform (Markdown, MDX, a CMS, a static-site generator, a hand-rolled template). This skill writes the article; you wire it into your stack.
5. For a bilingual blog, rewrite the other language idiomatically. Never translate word for word.

## Checklist before publishing

- [ ] Opens on a real problem or moment, not "In this article..."
- [ ] 4-6 H2 sections; the conclusion is a meta-observation, not a recap
- [ ] Zero AI-slop phrasings (ran the list above)
- [ ] Sentence rhythm varies; reads aloud without stumbling
- [ ] Cut half the filler (essential oil)
- [ ] Every claim and number is real, nothing invented
- [ ] A diagram only where it earns its place
- [ ] One long-tail query covered in title, H1, first paragraph, and an H2
- [ ] Slug keyword-first; meta description 150-160 chars
