# Installation Tutorial — claude-video-kit

Claude Code skills to generate MP4 videos programmed frame by frame (HTML canvas), with a synchronized background track and sound effects. This tutorial covers installation on **Windows** (PowerShell); the `pip`/`python` commands also apply to Linux/macOS, except for the zip-extraction and folder-copy steps, which are noted separately.

## 1. Prerequisites

| Requirement | How to check |
|---|---|
| Python 3.10+ | `python --version` |
| pip working on the same Python | `python -m pip --version` |
| Claude Code installed | already in use, if you're reading this through it |

> **Watch out for multiple Python installations.** If Windows has more than one version installed (common when Python gets installed more than once over time), the `python` command and the `pip` command may point to different installations — and then a package installed via `pip` won't show up when you run `python`. To check:
> ```powershell
> where.exe python
> where.exe pip
> ```
> If the paths are from different folders (e.g. `Python314` vs `Python313`), **always use `python -m pip install ...`** instead of a bare `pip install ...`, to make sure the install goes into the Python you'll actually run. Or use the `py -3.13 ...` / `py -3.14 ...` launcher to pin the version across all commands.

## 2. Extract the package

Windows doesn't have the `unzip` command by default. Use:
```powershell
Expand-Archive -Path claude-video-kit.zip -DestinationPath . -Force
cd claude-video-kit
```
Confirm you're in the right folder (it should contain `README.md`, `requirements.txt`, and the `skills\` folder):
```powershell
dir
```

## 3. Install the Python dependencies

```powershell
python -m pip install -r requirements.txt
```
This installs `playwright`, `imageio-ffmpeg`, and `numpy`. If it says "Requirement already satisfied" but a later test says `ModuleNotFoundError`, that's the multiple-installations issue from step 1 — repeat the command with `python -m pip` (not a bare `pip`) or pin the version with `py -3.13 -m pip install -r requirements.txt`.

## 4. Make sure a browser is available for Playwright

The renderer needs a Chromium, Edge, or Chrome browser installed to draw the frames in the background (headless). Test it:
```powershell
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(); print('OK:', b.version); b.close(); p.stop()"
```
- If it works, great — the scripts will use that Chromium automatically (`--navegador auto`, the default).
- If it errors out asking you to install the browser, run once:
  ```powershell
  python -m playwright install chromium
  ```
- Faster alternative (since Windows already ships with Edge): pass `--navegador msedge` on the commands in steps 5 and 6, with nothing extra to install.

## 5. Test the visual preview (before rendering the MP4)

```powershell
python skills\video-programatico\scripts\preview_frames.py skills\video-programatico\assets\template.html preview.png --frames 15 150 300 450 --colunas 2
```
Open `preview.png` in File Explorer. It should show 4 example frames (animated background, bar chart, numbered step list, and a final screen with a play button). If the images render correctly, the drawing engine is working.

## 6. Test the MP4 render

First a short test (just the first 3 seconds, faster):
```powershell
python skills\video-programatico\scripts\renderizar_mp4.py skills\video-programatico\assets\template.html video.mp4 --musica nenhuma --ate-frame 90
```
Open `video.mp4` — it should play normally. Then, if you want, render the full example (without `--ate-frame`, with music):
```powershell
python skills\video-programatico\scripts\renderizar_mp4.py skills\video-programatico\assets\template.html video_completo.mp4 --musica calma
```

Check the result with the ffmpeg bundled in the `imageio-ffmpeg` package:
```powershell
$FFMPEG = python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"
& $FFMPEG -hide_banner -i video.mp4
```
You should see `h264 ... 1280x720 ... 30 fps` and `Audio: aac ... stereo`. Exit code 1 at the end is normal (the command received no output file, just the inspection).

Repeat steps 5 and 6, swapping `video-programatico` for `video-frame-a-frame` to validate the second skill.

## 7. Install as a Claude Code skill

This is what makes Claude automatically recognize and use the skills when you ask for a video in chat.

**Option A — personal (all your conversations on this machine):**
```powershell
mkdir "$env:USERPROFILE\.claude\skills" -Force
Copy-Item -Recurse -Force skills\video-programatico "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse -Force skills\video-frame-a-frame "$env:USERPROFILE\.claude\skills\"
```

**Option B — per repository (shared with the team via Git):**
```powershell
mkdir .claude\skills -Force
Copy-Item -Recurse -Force skills\video-programatico .claude\skills\
Copy-Item -Recurse -Force skills\video-frame-a-frame .claude\skills\
```
Run this inside the root folder of the repository where you want to make the skills available to the team, and commit the `.claude\skills\` folder.

## 8. Usage

Open a Claude Code conversation (on this machine, or, if installed per repository, with that folder as the working directory) and ask for what you want:

> *"create a 20-second, 16:9 video explaining the benefits of the company's new hiring process"*

> *"make a tutorial video showing how to register a customer in ServiceNow, with cursor and clicks"*

Claude follows the matching `SKILL.md` procedure: briefing → storyboard → editing the script in the template → validation with `preview_frames.py` → rendering with `renderizar_mp4.py` → delivery of the `.html` and `.mp4`. If it doesn't trigger the skill on its own, force it by naming it: `/video-programatico` or `/video-frame-a-frame`.

## 9. Troubleshooting (errors already seen)

| Error | Cause | Fix |
|---|---|---|
| `unzip : The term 'unzip' is not recognized...` | PowerShell has no `unzip` | Use `Expand-Archive -Path ... -DestinationPath . -Force` |
| `ModuleNotFoundError: No module named 'playwright'` right after a `pip install` that said "already satisfied" | `python` and `pip` point to different Python installations | Run `where.exe python` and `where.exe pip`; always use `python -m pip install ...`, or pin the version with `py -3.13 ...` |
| Error asking to install the browser executable when running `renderizar_mp4.py`/`preview_frames.py` | No Playwright Chromium installed | `python -m playwright install chromium`, or use `--navegador msedge` (Windows already ships with Edge) |
| `canvas ...: width and height must be even` | A custom `FORMATO`/resolution in the script ended up odd | Adjust the resolution in the HTML to even values (the template's default formats are already even) |
| `ffmpeg falhou (...)` | Usually audio or video corrupted mid-process | Run again with `--ate-frame 90` to isolate whether the issue is in the video or the audio; check `_log_mp4.txt` if you're using it |

## 10. Quick command reference

```powershell
# visual preview
python skills\<skill>\scripts\preview_frames.py <animation.html> <preview.png> --frames 60 200 400 600 --colunas 2

# final render
python skills\<skill>\scripts\renderizar_mp4.py <animation.html> <output.mp4> --musica calma|animada|nenhuma|<arquivo.mp3> [--volume-musica 0.6] [--ate-frame 150] [--navegador auto|chromium|msedge|chrome]
```

Replace `<skill>` with `video-programatico` or `video-frame-a-frame`, depending on the type of video.

> Note: command-line flag names (`--musica`, `--volume-musica`, `--navegador`, `--ate-frame`, `--frames`, `--colunas`) stay in Portuguese, matching the scripts' actual argument names — they are not translated here since that would break the commands.
