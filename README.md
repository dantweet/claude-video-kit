# claude-video-kit

**Claude Code** skills that generate **MP4 videos programmatically, frame by frame**: every frame is drawn by code on an HTML canvas, and the video comes out with a synchronized background track and sound effects (clicks, pops, whooshes, dings, typing, etc.).

Adapted from an equivalent kit originally built for GitHub Copilot, converted to the Claude Code skills format — keeping the same animation engine and renderer. Only the installation, default browser, and visual-validation step were adapted.

| Skill | What it's for |
|---|---|
| `video-programatico` | Any video: explainer, motion graphics, animated chart, stinger, animated logo, announcement, social media (16:9, 9:16, 1:1, 4:5) |
| `video-frame-a-frame` | System/screen tutorial: real layout, cursor, clicks, "STEP n/N" captions |

Just ask in chat (e.g. *"create a 20s vertical video announcing the new hiring process"*). Claude builds the storyboard, codes the scenes, validates the frames, and generates the MP4.

## Installation

**Personal (all your Claude Code conversations)**
```bash
cp -r skills/video-programatico skills/video-frame-a-frame ~/.claude/skills/
```

**In a repository (shared with the team, version-controlled in Git)**
```bash
mkdir -p .claude/skills
cp -r skills/video-programatico skills/video-frame-a-frame .claude/skills/
```

After that, just ask for a video in the Claude Code chat (or invoke it by name, e.g. `/video-programatico`) from the folder/profile where the skills were copied.

## Dependencies (only needed to render the MP4)

- Python 3.10+ and `pip install --break-system-packages -r requirements.txt` (playwright, imageio-ffmpeg, numpy)
- A Chromium/Edge/Chrome browser available:
  - In the Claude Code sandbox, Chromium already comes pre-installed (nothing to do, use `--navegador auto`, the default).
  - Outside the sandbox (e.g. running on the user's computer via a connected device), run `playwright install chromium` once, or use `--navegador msedge`/`chrome` if one of them is already installed.

The HTML animation opens in any browser with no dependencies, even without Python.

## Using the scripts directly

```bash
# validate frames before rendering (generates a PNG with several previews; open it with the Read tool)
python skills/video-programatico/scripts/preview_frames.py video.html preview.png --frames 45 180 330 480

# render the final MP4
python skills/video-programatico/scripts/renderizar_mp4.py video.html video.mp4 --musica calma|animada|nenhuma|arquivo.mp3 [--volume-musica 0.6] [--ate-frame 150]
```

> Note: the script flags themselves (`--musica`, `--volume-musica`, `--navegador`, `--ate-frame`, `--frames`, `--colunas`) are kept in Portuguese to match the engine's source code and `SKILL.md` files — see each skill's `SKILL.md` for the full option reference.

## Built-in rules

- Deterministic frames (pure `desenhar(f)`), sounds triggered at the exact instant of the visual event.
- Only assets with proper usage rights: everything code-generated, images/logos supplied by the user, synthesized audio, or a licensed file.
- Personal data always fictional (privacy-by-design / LGPD-style data minimization).

## What changed from the original (Copilot) kit

- **Installation**: `skills/` folders copied to `~/.claude/skills/` (personal) or a repository's `.claude/skills/` (team), instead of `~/.copilot/skills` / `.github/skills` and the `copilot plugin install` flow.
- **Renderer's default browser**: `--navegador auto` first tries Playwright's bundled Chromium (already present in the Claude Code sandbox) and only then falls back to the system's Edge/Chrome — the original always assumed Windows Edge.
- **Visual validation**: instead of the `page.evaluate` trick in a Copilot-specific "integrated browser", each skill gained `scripts/preview_frames.py`, which generates a PNG contact sheet straight from the HTML animation; Claude opens that PNG with the **Read** tool to inspect the frames.
- **Long-running execution**: the instructions now recommend running the render in the background with a log file, suited to Claude Code's shell call time limits.
- The animation engine (`template.html`) and audio synthesis (`renderizar_mp4.py`) are the same as the original kit — only the browser-launch block was generalized.

## Higgsfield

The `higgsfield-ai/higgsfield` repository is a distributed LLM training orchestrator and **does not generate video**; it is not a dependency of this kit. The commercial Higgsfield AI platform can be used manually for post-production on the generated MP4.
