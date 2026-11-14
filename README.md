# einfach.dawah animation engine

2D PyCairo engine for the islamic short videos (1080x1920, 30 fps).

* `lib.py` core drawing (person, sky, ground, camera, text, subtitles)
* `scenes_common.py` layers with parallax, backgrounds, towns
* `kit.py` story timing (Story), overlays (hook, quote, lesson card, CTA, end card), figures and props
* `align.py` sentence and word timing from the voice mp3
* `render.py` render stills or video segments
* `rv.sh` full render + mux, `sheet.sh` contact sheet, `setup.sh` fonts and deps
* `examples/` finished video modules to copy from

Workflow: see the skill `dawah-animation`.
