---
name: video-frame-a-frame
description: 'Gera vídeo MP4 tutorial/passo a passo de uma função, tela, sistema ou fluxo de software (layout real, cursor, cliques, legendas de passo), programando a animação frame a frame em canvas HTML com trilha de fundo e efeitos sonoros (clique, digitação, sucesso, erro, whoosh, notificação). Use quando pedirem: tutorial em vídeo de sistema, passo a passo animado de tela, demo de funcionalidade, "com som", "cada clique". Para vídeos que não são de tela/sistema (explicativo, motion, vinheta, redes sociais), use video-programatico.'
argument-hint: 'O que o vídeo deve mostrar (função, tela, fluxo) e para quem'
---

# Vídeo frame a frame com som

Produz um `.html` com a animação (cada frame desenhado por `desenhar(f)`, determinístico) e um `.mp4` (H.264 + AAC) com trilha e efeitos sincronizados aos eventos do roteiro.

- Template da animação: [assets/template.html](./assets/template.html)
- Renderizador MP4 + áudio: [scripts/renderizar_mp4.py](./scripts/renderizar_mp4.py) (idêntico ao da skill `video-programatico`; sons extras: `pop`, `ding`, `impacto`, `subida`, `tique`; opção `--ate-frame N` para prévia)
- Validação visual sem navegador interativo: [scripts/preview_frames.py](./scripts/preview_frames.py)
- Vídeos que não são de tela/sistema: skill `video-programatico`.

## Sobre o Higgsfield

O repositório `github.com/higgsfield-ai/higgsfield` é um orquestrador de GPU para **treino distribuído de LLMs** (ZeRO-3, FSDP, GitHub Actions). Ele **não gera vídeo nem áudio**, então não faz parte do pipeline. A plataforma comercial Higgsfield AI (produto separado, web) pode ser usada **manualmente**, depois, para pós-produção com IA sobre o MP4 gerado aqui. Explique isso ao usuário se ele pedir o Higgsfield; não instale o pacote `higgsfield`.

## Procedimento

1. **Entender o pedido**: o que mostrar, público, duração-alvo (20–60 s costuma bastar), resolução 1280x720.
2. **Coletar fidelidade do material real** antes de desenhar: rótulos, cores/tokens, layout, regras de negócio e ordem dos passos, lendo o código (templates, SCSS de variáveis, handlers) ou prints/documentação fornecidos pelo usuário. Não invente telas ou regras; se algo não existir, diga.
3. **Escrever o roteiro** (antes de codar): cenas com início/fim em segundos, keyframes do cursor `[s, x, y]`, eventos `SONS` (`{t, tipo, dur?}`), legendas `[ini, fim, passo, texto]` e uma tela final de resumo.
4. **Copie o template** para a pasta de saída do projeto (ex.: `tutoriais/<tema>/animacao.html`) e edite **só a seção ROTEIRO**: `TITULO`, `SUBTITULO`, `DURACAO`, `ABERTURA`, `ENCERRAMENTO`, `TEMA`, `CURSOR`, `SONS`, `LEGENDAS`, `TOTAL_PASSOS`, `cena(t)` e `telaFinal(t)`. Use os helpers do motor: `caixa`, `texto`, `quebrar`, `badge`, `botao`, `toast`, `spinner`, `destaque`, `sobre` (hover pelo cursor), `prog`, `ease`, `fade`, `entre`.
5. **Instale as dependências** uma vez (ver seção abaixo) e **valide os frames** gerando uma prancha de contato com vários momentos:
   ```bash
   python <skill>/scripts/preview_frames.py animacao.html preview.png --frames 60 200 400 600 --colunas 2
   ```
   Depois abra `preview.png` com a ferramenta **Read** (ela exibe imagens). Corrija sobreposições, textos cortados e destaques fora do lugar.
6. **Renderize o MP4**. Rode em segundo plano (processo longo), redirecionando o log para arquivo:
   ```bash
   python <skill>/scripts/renderizar_mp4.py animacao.html video.mp4 --musica calma > _log_mp4.txt 2>&1 &
   ```
   Depois acompanhe com `tail -f _log_mp4.txt` ou leia o arquivo periodicamente — execuções síncronas longas num único comando podem ser interrompidas pelo timeout da ferramenta de shell.
   - Opções: `--musica calma|animada|nenhuma|<arquivo licenciado>`, `--volume-musica 0.6`, `--navegador auto|msedge|chrome|chromium`.
   - Leva cerca de 1 min a cada 300 frames.
   - `--navegador auto` (padrão) usa o Chromium já incluído no ambiente do Claude Code; só troque para `msedge`/`chrome` se estiver rodando num computador do usuário (via dispositivo conectado) onde esses navegadores já existem.
7. **Verificar**: `<ffmpeg> -hide_banner -i video.mp4` deve mostrar a duração correta, um stream `h264 1280x720 30 fps` e um `aac stereo`. O exit code 1 desse comando é normal, porque não há saída definida. O executável vem de `python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`. Apague o log.
8. **Entregar**: envie o `.html` e o `.mp4` ao usuário (ferramenta de envio de arquivo), com o roteiro resumido (passos + tempos dos sons) e o comando para regerar.

## Instalação das dependências (ambiente de execução)

```bash
pip install --break-system-packages playwright imageio-ffmpeg numpy
```

O Chromium necessário para o `--navegador auto` já vem pré-instalado no sandbox do Claude Code (variável `PLAYWRIGHT_BROWSERS_PATH`); **não rode `playwright install`** nesse ambiente. Se este kit for usado fora do sandbox, rode `playwright install chromium` uma vez.

## Regras

- `desenhar(f)` precisa ser **puro**: nada de `Date.now()`, `Math.random()` sem semente nem estado mutável entre frames. Tudo deriva de `t = f / FPS`.
- O motor depende dos globais `FPS`, `TOTAL`, `DURACAO`, `SONS`, `desenhar` e `tocando`, e do canvas `#tela`. Não renomeie.
- Efeito sonoro e visual devem cair no **mesmo t**: o ripple do clique já sai de `SONS` com `tipo: 'clique'`, e o `toast` de sucesso deve coincidir com `tipo: 'sucesso'`.
- **Dados fictícios** em nomes, CPFs, e-mails e salários (LGPD). Nunca use dados reais de produção no vídeo.
- **Áudio**: só a trilha sintetizada pelo script ou um arquivo cuja licença o usuário confirme. Não baixe músicas da internet.
- Legendas curtas (uma ou duas linhas), um passo por legenda e numeração `PASSO n/N`.
- Elementos de um modal aberto usam `sobre(..., 'dialogo')` e `camadaAtiva = 'dialogo'`, para evitar hover em elementos atrás dele.
