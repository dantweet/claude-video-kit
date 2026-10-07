"""Gera uma prancha de contato (PNG) com vários frames da animação, para validação visual
sem depender de um navegador interativo. Pensado para o fluxo do Claude Code: rode o script
e depois abra o PNG resultante com a ferramenta Read (que exibe imagens).

Uso:
  python preview_frames.py animacao.html [saida.png] --frames 60 200 400 600 [--colunas 2]
Dependências: pip install playwright
"""
import argparse
import base64
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def abrir_navegador(p, preferencia):
    if preferencia != "auto":
        canal = None if preferencia == "chromium" else preferencia
        return p.chromium.launch(channel=canal, headless=True)
    erros = []
    for canal in (None, "msedge", "chrome"):
        try:
            return p.chromium.launch(channel=canal, headless=True)
        except Exception as e:
            erros.append(f"{canal or 'chromium'}: {e}")
    sys.exit("Não foi possível abrir nenhum navegador Chromium/Edge/Chrome.\n" + "\n".join(erros))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    ap.add_argument("saida", type=Path, nargs="?")
    ap.add_argument("--frames", type=int, nargs="+", required=True, help="números dos frames a exibir, ex: 60 200 400 600")
    ap.add_argument("--colunas", type=int, default=2)
    ap.add_argument("--navegador", default="auto", help="auto | chromium | msedge | chrome")
    args = ap.parse_args()
    html = args.html.resolve()
    saida = (args.saida or html.with_name("preview.png")).resolve()

    with sync_playwright() as p:
        navegador = abrir_navegador(p, args.navegador)
        pagina = navegador.new_page(viewport={"width": 1400, "height": 1000})
        pagina.goto(html.as_uri() + "#f=0")
        pagina.wait_for_function("typeof desenhar === 'function' && window.pronto !== false", timeout=30000)
        pagina.evaluate("typeof tocando !== 'undefined' && (tocando = false)")
        largura, altura = pagina.evaluate(
            "[document.getElementById('tela').width, document.getElementById('tela').height]")
        data_url = pagina.evaluate(
            """([frames, cols, w, h]) => {
                const linhas = Math.ceil(frames.length / cols);
                const c = document.createElement('canvas');
                c.width = w * cols; c.height = h * linhas;
                const g = c.getContext('2d');
                frames.forEach((f, i) => {
                    desenhar(f);
                    g.drawImage(document.getElementById('tela'), (i % cols) * w, Math.floor(i / cols) * h, w, h);
                    g.strokeStyle = 'rgba(255,0,0,.5)'; g.lineWidth = 2;
                    g.strokeRect((i % cols) * w, Math.floor(i / cols) * h, w, h);
                    g.fillStyle = '#fff'; g.font = 'bold 20px Arial';
                    g.fillText('f=' + f, (i % cols) * w + 8, Math.floor(i / cols) * h + 24);
                });
                return c.toDataURL('image/png');
            }""",
            [args.frames, args.colunas, largura, altura])
        navegador.close()

    saida.write_bytes(base64.b64decode(data_url.split(",", 1)[1]))
    print(f"OK: {saida} ({len(args.frames)} frames, {args.colunas} colunas, canvas {largura}x{altura}) — abra com a ferramenta Read")


if __name__ == "__main__":
    main()
