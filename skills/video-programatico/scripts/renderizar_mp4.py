"""Renderiza uma animação HTML (canvas #tela) frame a frame em MP4 com trilha de fundo e efeitos sonoros.

Contrato com o HTML:
  globais FPS, TOTAL, DURACAO, desenhar(f); opcional tocando, window.pronto (aguardado quando existir)
  SONS = [{t, tipo, dur?, vol?}]  (ou CLIQUES = [t, ...], tratado como 'clique')
  O tamanho do vídeo é o tamanho do canvas (precisa ser par).

Uso:
  python renderizar_mp4.py animacao.html [saida.mp4] [--musica calma|animada|nenhuma|arquivo.mp3]
                           [--volume-musica 1.0] [--navegador auto|chromium|msedge|chrome] [--ate-frame N]
Dependências: pip install playwright imageio-ffmpeg numpy
"""
import argparse
import base64
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from playwright.sync_api import sync_playwright

SR = 48000
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def freq(nome):
    semitons = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    return 440.0 * 2 ** ((semitons[nome[0]] + 12 * (int(nome[1:]) - 4)) / 12)


def envelope(n, ataque, liberacao):
    env = np.ones(n)
    a, r = min(int(ataque * SR), n), min(int(liberacao * SR), n)
    env[:a] = np.linspace(0, 1, a)
    if r:
        env[-r:] *= np.linspace(1, 0, r)
    return env


# ---------------- trilhas sintetizadas (livres de direitos) ----------------
def trilha_sintetizada(duracao, estilo):
    total = int(duracao * SR)
    esq, dir_ = np.zeros(total), np.zeros(total)
    acordes = [(["C4", "E4", "G4", "C5"], "C2"), (["A3", "C4", "E4", "A4"], "A1"),
               (["F3", "A3", "C4", "F4"], "F1"), (["G3", "B3", "D4", "G4"], "G1")]
    compasso = 2.5 if estilo == "calma" else 1.875
    padrao = [0, 1, 2, 3, 2, 1, 2, 1]
    rng = np.random.default_rng(7)
    i = 0
    while i * compasso < duracao:
        notas, baixo = acordes[i % 4]
        ini = int(i * compasso * SR)
        n = min(int((compasso + 1.0) * SR), total - ini)
        t = np.arange(n) / SR
        pad = sum(np.sin(2 * np.pi * freq(x) / 2 * t) + 0.5 * np.sin(2 * np.pi * freq(x) / 2 * 1.003 * t) for x in notas[:3])
        pad *= envelope(n, 0.8, 1.0) * 0.035
        bx = np.sin(2 * np.pi * freq(baixo) * t) * envelope(n, 0.3, 1.0) * 0.10
        esq[ini:ini + n] += pad + bx
        dir_[ini:ini + n] += pad + bx
        passo = compasso / len(padrao)
        for k, idx in enumerate(padrao):
            p_ini = ini + int(k * passo * SR)
            pn = min(int(0.9 * SR), total - p_ini)
            if pn <= 0:
                continue
            pt = np.arange(pn) / SR
            f = freq(notas[idx]) * 2
            pluck = (np.sin(2 * np.pi * f * pt) + 0.25 * np.sin(4 * np.pi * f * pt)) * np.exp(-pt / 0.28)
            pluck *= envelope(pn, 0.004, 0.05) * (0.045 + 0.01 * rng.random())
            pan = 0.35 if k % 2 else -0.35
            esq[p_ini:p_ini + pn] += pluck * (1 - pan)
            dir_[p_ini:p_ini + pn] += pluck * (1 + pan)
        if estilo == "animada":
            for k in range(4):
                b_ini = ini + int(k * compasso / 4 * SR)
                bn = min(int(0.15 * SR), total - b_ini)
                if bn > 0:
                    bt = np.arange(bn) / SR
                    bumbo = np.sin(2 * np.pi * (55 + 90 * np.exp(-bt / 0.03)) * bt) * np.exp(-bt / 0.06) * 0.12
                    esq[b_ini:b_ini + bn] += bumbo
                    dir_[b_ini:b_ini + bn] += bumbo
        i += 1
    geral = envelope(total, 1.5, 3.0)
    return np.stack([esq * geral, dir_ * geral], axis=1)


def trilha_arquivo(caminho, duracao):
    bruto = subprocess.run([FFMPEG, "-loglevel", "error", "-i", str(caminho), "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                           capture_output=True, check=True).stdout
    audio = np.frombuffer(bruto, "<i2").reshape(-1, 2).astype(float) / 32768
    total = int(duracao * SR)
    audio = np.tile(audio, (total // len(audio) + 1, 1))[:total]
    return audio * envelope(total, 1.0, 3.0)[:, None] * 0.5


# ---------------- efeitos ----------------
def _t(seg):
    return np.arange(int(seg * SR)) / SR


def _sino(f, seg, decai):
    t = _t(seg)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.1 * np.sin(6 * np.pi * f * t)) * np.exp(-t / decai)


def _sequencia(partes, gap):
    total = int(gap * SR) * (len(partes) - 1) + max(len(p) for p in partes) + 1
    s = np.zeros(total)
    for i, p in enumerate(partes):
        ini = int(i * gap * SR)
        s[ini:ini + len(p)] += p
    return s


def fx_clique(rng, **_):
    t = _t(0.12)

    def transiente(amp):
        ruido = rng.uniform(-1, 1, len(t)) * np.exp(-t / 0.0022)
        tique = np.sin(2 * np.pi * 3200 * t) * np.exp(-t / 0.004) * 0.6
        corpo = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.012) * 0.5
        return (ruido * 0.5 + tique + corpo) * amp

    s = transiente(0.55)
    solta = int(0.065 * SR)
    s[solta:] += transiente(0.35)[: len(t) - solta]
    return s


def fx_digitar(rng, dur=1.0, **_):
    s = np.zeros(int((dur + 0.1) * SR))
    t = _t(0.03)
    pos = 0.0
    while pos < dur:
        ini = int(pos * SR)
        tecla = (rng.uniform(-1, 1, len(t)) * 0.4 + np.sin(2 * np.pi * rng.uniform(1800, 2600) * t)) * np.exp(-t / 0.004)
        s[ini:ini + len(t)] += tecla * rng.uniform(0.15, 0.25)
        pos += rng.uniform(0.07, 0.13)
    return s


def fx_pop(rng, **_):
    t = _t(0.12)
    return np.sin(2 * np.pi * (300 + 900 * np.exp(-t / 0.015)) * t) * np.exp(-t / 0.035) * 0.5


def fx_ding(rng, **_):
    return _sino(1318.5, 1.2, 0.45) * 0.3


def fx_sucesso(rng, **_):
    return _sequencia([_sino(659.25, 0.5, 0.18) * 0.35, _sino(987.77, 0.8, 0.3) * 0.35], 0.12)


def fx_erro(rng, **_):
    a = _sino(233.08, 0.25, 0.1) * 0.45
    return _sequencia([a, a], 0.18)


def fx_notificacao(rng, **_):
    return _sino(880, 0.9, 0.35) * 0.3


def fx_whoosh(rng, dur=0.6, **_):
    n = int(dur * SR)
    ruido = np.convolve(rng.uniform(-1, 1, n), np.hanning(40) / 20, mode="same")
    return ruido * np.sin(np.pi * np.linspace(0, 1, n)) ** 2 * 0.5


def fx_impacto(rng, **_):
    t = _t(0.9)
    grave = np.sin(2 * np.pi * (45 + 120 * np.exp(-t / 0.05)) * t) * np.exp(-t / 0.25)
    ruido = np.convolve(rng.uniform(-1, 1, len(t)), np.hanning(60) / 30, mode="same") * np.exp(-t / 0.08)
    return (grave * 0.6 + ruido * 0.4) * 0.7


def fx_subida(rng, dur=1.0, **_):
    t = _t(dur)
    fase = 2 * np.pi * np.cumsum(200 + 900 * (t / dur) ** 2) / SR
    ruido = np.convolve(rng.uniform(-1, 1, len(t)), np.hanning(25) / 12, mode="same")
    return (np.sin(fase) * 0.25 + ruido * 0.2) * (t / dur) ** 2 * 0.6


def fx_tique(rng, dur=1.0, **_):
    partes, pos, k = [], 0.0, 0
    while pos < dur:
        partes.append(_sino(1500 + 25 * k, 0.04, 0.008) * 0.25)
        pos += 0.1
        k += 1
    return _sequencia(partes, 0.1)


EFEITOS = {"clique": fx_clique, "digitar": fx_digitar, "pop": fx_pop, "ding": fx_ding, "sucesso": fx_sucesso,
           "erro": fx_erro, "notificacao": fx_notificacao, "whoosh": fx_whoosh, "impacto": fx_impacto,
           "subida": fx_subida, "tique": fx_tique}


def gerar_audio(destino, duracao, sons, musica, volume_musica):
    total = int(duracao * SR)
    if musica == "nenhuma":
        mix = np.zeros((total, 2))
    elif musica in ("calma", "animada"):
        mix = trilha_sintetizada(duracao, musica) * volume_musica
    else:
        mix = trilha_arquivo(musica, duracao) * volume_musica
    rng = np.random.default_rng(3)
    for s in sons:
        fx = EFEITOS.get(s.get("tipo", "clique"))
        if not fx:
            print(f"aviso: tipo de som desconhecido {s}", file=sys.stderr)
            continue
        onda = fx(rng, **{k: v for k, v in s.items() if k not in ("t", "tipo", "vol")}) * s.get("vol", 1.0)
        ini = int(s["t"] * SR)
        fim = min(ini + len(onda), total)
        if fim > ini:
            mix[ini:fim] += onda[: fim - ini, None]
    pico = np.max(np.abs(mix))
    if pico > 0:
        mix *= 0.89 / pico
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())


# ---------------- navegador ----------------
def abrir_navegador(p, preferencia):
    """Abre o Chromium. 'auto' tenta primeiro o Chromium embutido do Playwright
    (é o caso do sandbox do Claude Code, que já vem com ele pré-instalado em
    PLAYWRIGHT_BROWSERS_PATH); se isso falhar, tenta o Edge e depois o Chrome
    do sistema (comum em máquinas Windows do usuário)."""
    if preferencia != "auto":
        canal = None if preferencia == "chromium" else preferencia
        return p.chromium.launch(channel=canal, headless=True)
    erros = []
    for canal in (None, "msedge", "chrome"):
        try:
            return p.chromium.launch(channel=canal, headless=True)
        except Exception as e:  # tenta a próxima opção
            erros.append(f"{canal or 'chromium'}: {e}")
    sys.exit("Não foi possível abrir nenhum navegador Chromium/Edge/Chrome.\n"
              "Rode 'pip install playwright && playwright install chromium' ou informe "
              "--navegador msedge|chrome se um deles estiver instalado.\n" + "\n".join(erros))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    ap.add_argument("saida", type=Path, nargs="?")
    ap.add_argument("--musica", default="calma", help="calma | animada | nenhuma | caminho de arquivo de áudio licenciado")
    ap.add_argument("--volume-musica", type=float, default=1.0)
    ap.add_argument("--navegador", default="auto", help="auto | chromium | msedge | chrome")
    ap.add_argument("--ate-frame", type=int, help="renderiza só até este frame (prévia rápida)")
    args = ap.parse_args()
    html = args.html.resolve()
    saida = (args.saida or html.with_suffix(".mp4")).resolve()

    with sync_playwright() as p:
        navegador = abrir_navegador(p, args.navegador)
        pagina = navegador.new_page(viewport={"width": 1400, "height": 1000})
        pagina.goto(html.as_uri() + "#f=0")
        pagina.wait_for_function("typeof desenhar === 'function' && window.pronto !== false", timeout=30000)
        pagina.evaluate("typeof tocando !== 'undefined' && (tocando = false)")
        fps, total, duracao, largura, altura = pagina.evaluate(
            "[FPS, TOTAL, DURACAO, document.getElementById('tela').width, document.getElementById('tela').height]")
        sons = pagina.evaluate("typeof SONS !== 'undefined' ? SONS : (typeof CLIQUES !== 'undefined' ? CLIQUES.map(t => ({t, tipo: 'clique'})) : [])")
        if largura % 2 or altura % 2:
            sys.exit(f"canvas {largura}x{altura}: largura e altura precisam ser pares (H.264/yuv420p)")
        if args.ate_frame:
            total = min(total, args.ate_frame + 1)
            duracao = total / fps

        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "audio.wav"
            gerar_audio(wav, duracao, sons, args.musica, args.volume_musica)
            ffmpeg = subprocess.Popen(
                [FFMPEG, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-i", "-", "-i", str(wav),
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(saida)],
                stdin=subprocess.PIPE)
            for f in range(total):
                url = pagina.evaluate("f => { desenhar(f); return document.getElementById('tela').toDataURL('image/png'); }", f)
                ffmpeg.stdin.write(base64.b64decode(url.split(",", 1)[1]))
                if f % 150 == 0:
                    print(f"frame {f}/{total}", flush=True)
            ffmpeg.stdin.close()
            codigo = ffmpeg.wait()
        navegador.close()

    if codigo:
        sys.exit(f"ffmpeg falhou ({codigo})")
    print(f"OK: {saida} ({saida.stat().st_size / 1e6:.1f} MB, {largura}x{altura}, {duracao:.1f}s, {len(sons)} eventos sonoros)")


if __name__ == "__main__":
    main()
