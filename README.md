# Incipient Institute

Incipient Institute is an interactive work of horror fiction by Metanexus Institute. It takes the form of the public website of a research foundation. You can meet its fellows, read its visitor guidance, and look through the records it keeps about its people and grounds. For a first encounter, start with the site before reading further.

## Why horror?

One way to read Shirley Jackson’s *The Haunting of Hill House* is as a house that gives narcissism an architecture. Incipient Institute builds a different haunted house around a question about process. What would a foundation become if it took every increase in relation, novelty, or possibility as evidence that things were going well?

The fictional Institute takes seriously the idea that people and places change through their encounters. Its trouble begins when it treats openness to change as a duty owed to the mission. An objection becomes feedback. An injury becomes a finding. A request to leave becomes a new phase of participation. The Institute can describe each event with great care and still fail the person it happened to.

Something genuinely new can come into being through a change that destroys what someone else needed to live. The new thing can have value in its own right. That value does not settle what the loss meant for the person who bore it. Horror lets us stay with that fact, even when the institution is ready to publish its next success.

Darkness has its own place in the work. It can shelter rest, refusal, and forms of life and imagination that need to grow unseen. We take seriously traditions in which darkness has creative and sacred force. At the Pavilion, even the right to remain unobserved can become something the mission asks you to surrender.

## How the site tells the story

The horror accumulates through the ordinary forms of institutional life. A visitor notice sounds considerate until you see whom it asks to accommodate a change. A revised floor plan is still drawn with a surveyor’s confidence. The staff can sound sincere when they thank you for remaining open. Read the public faces of the Institute first and follow whatever detail makes you stop.

## Contribute

- **Open an issue** about a passage that made you pause, a moment that felt unearned, an accessibility problem, or a reading we might have missed. A page and what you noticed are enough.
- **Propose an edit in a pull request.** A single line, a notice, a change to the floor plan, or a detail that takes on a second meaning on a return visit are all welcome. Tell us what you want a reader to experience.
- **Fork the repository and try an idea on a branch.** Rewrite a record from the perspective of the person it describes. Imagine a director who tries to protect the right to withdraw. Build a different institution around a different idea it holds too dear. Share the experiment, whether or not you want it folded into the main work.

The central question for a contribution is who gets to call a change good, and who has to live with it.

## Preview locally

From the repository root, use Python 3 to build the site and serve it locally.

```sh
python3 build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open [the local preview](http://127.0.0.1:8000/). The editable pages and facilities log are in `content/`.

For a production build, pass the live site's HTTPS origin with `--canonical-origin` and publish `dist/`.

[Metanexus Institute](https://metanexus.net/) · [Shirley Jackson’s *The Haunting of Hill House*](https://www.penguinrandomhouse.com/books/321924/the-haunting-of-hill-house-by-shirley-jackson-introduction-by-laura-miller/)
