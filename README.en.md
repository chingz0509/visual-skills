# visual-skills

**Give your agent a photo. Get a collage poster.**

The agent chooses the title, colors and layout while preserving the original photographic subject. The first style is **Photo Collage**, with more styles planned.

![Photo Collage: all ten actual outputs](examples/contact-sheet.jpg)

[中文](README.md) · [All examples](benchmark/REPORT.md)

## Install and use

The project, skill and install package all use the name **`visual-skills`**. It currently supports photo collage. Scripts and fonts are included; install this single skill.

Tell Codex:

> Install `skills/visual-skills` from https://github.com/chingz0509/visual-skills and prepare its runtime.

Then attach a photo:

> Use visual-skills to turn this photo into a collage poster.

Include your own title if you have one. Otherwise, the agent writes it in your conversation language.

## What you get

- A 1200 × 1600 PNG poster.
- Original photo subjects, composed without generative redrawing.
- Saved photos, layers, fonts and layout for identical recomposition.

Works with portraits, groups, products, pets and landscapes. Group relationships and complete landscape photos are preserved. The baseline uses your existing agent and local tools; no extra image-generation key or additional skill is needed. On first use, the agent may download Python image-processing dependencies and needs permission to execute local tools.

## Experimental status

Verified environment: **Codex desktop on Apple Silicon macOS**. Other environments have not completed end-to-end validation.

Of ten fixed test photos, eight passed the first author-agent review and two passed after repair. **Final human acceptance is pending.** Layout variety and fine-fur cutouts remain limited. [All results, including rejected attempts →](benchmark/REPORT.md)

[Download visual-skills](https://github.com/chingz0509/visual-skills/releases/download/v0.1.0-experimental/visual-skills-0.1.0-experimental.zip) · [Runtime details (Chinese)](docs/USAGE.md) · [Contribute a style](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

Code uses MIT. Photos and fonts retain their own licenses. [Credits](THIRD_PARTY.md)
