# Visual Style Skills

[中文](README.md)

Experimental visual skills for agents. Give your agent a photograph and get a paper collage poster while preserving the original photographic subject. Each style lives in a separately installable directory under `skills/`.

![All ten actual outputs from the fixed benchmark](examples/contact-sheet.jpg)

*All ten outputs from the fixed benchmark, shown unchanged. [All ten cases and rejected attempts](benchmark/REPORT.md) remain available.*

## First style: Photo Paper Collage

The agent chooses the title, palette and layout. Local tools compose original photo pixels, paper, typography and print texture into a 1200 × 1600 PNG. Subjects are never redrawn by an image model. Group photos and landscapes stay whole; unreliable cutouts return to whole-photo composition.

The baseline needs no image-generation API key or author-hosted service. It uses your existing agent for planning and visual review. Optional image generation is a future extension, not an implemented feature.

## Install and use

Give Codex this repository's URL and ask:

> Install `skills/photo-paper-collage` from this repository and prepare its runtime following the skill instructions.

Alternatively, download the standalone skill ZIP from [Releases](https://github.com/chingz0509/visual-style-skills/releases/tag/v0.1.0-experimental), extract it, and ask Codex to install that folder. Developers can run `python3 scripts/install.py --prepare` from a source checkout. Existing installations are not overwritten.

Then attach a photo:

> Use Photo Paper Collage to make a poster. Choose the title, colors and layout for me.

Titles follow the conversation language. Supplied formal copy is preserved. Outputs include the PNG and actual assets, fonts and layout records for pixel-identical recomposition. Regenerating a design is not guaranteed to produce the same image.

## Evidence and limits

- Ten frozen inputs: two each for portraits, groups, products, pets and landscapes.
- Eight passed the first author-agent review. Two pet cutouts were rejected and passed after whole-photo repair. All intermediate results are published.
- Ten final complex compositions; zero final simple compositions or failures in this development set. This is not a held-out evaluation; final human acceptance is pending.
- Six behavioral tests and ten pixel-identical replays passed locally.
- Verified host: Codex desktop on Apple Silicon macOS 26.6.1. Apple Vision segmentation/OCR requires macOS 14+ and Swift tools. Other hosts and clean-machine dependency setup have not completed end-to-end validation.
- Four layouts and four palettes; short copy only. Current output retains a template-like appearance.

[Full report](benchmark/REPORT.md) · [Contribution guide](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

Code and original procedural textures use MIT. Photos and fonts retain their own licenses; see [third-party credits](THIRD_PARTY.md). User-provided reference posters and raw benchmark photographs are not distributed in the repository.
