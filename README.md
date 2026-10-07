# claude-video-kit

Skills do **Claude Code** para gerar **vídeos MP4 programados frame a frame**: cada quadro é desenhado por código num canvas HTML, e o vídeo sai com trilha de fundo e efeitos sonoros sincronizados (cliques, pop, whoosh, ding, digitação etc.).

Adaptação de um kit equivalente feito originalmente para o GitHub Copilot, convertido para o formato de skills do Claude Code — mantendo o mesmo motor de animação e o mesmo renderizador. Só a instalação, o navegador padrão e o passo de validação visual foram adaptados.

| Skill | Para quê |
|---|---|
| `video-programatico` | Qualquer vídeo: explicativo, motion graphics, gráfico animado, vinheta, logo animado, comunicado, redes sociais (16:9, 9:16, 1:1, 4:5) |
| `video-frame-a-frame` | Tutorial de sistema/tela: layout real, cursor, cliques, legendas "PASSO n/N" |

Basta pedir no chat (ex.: *"crie um vídeo vertical de 20s anunciando o novo processo seletivo"*). O Claude monta o storyboard, programa as cenas, valida os quadros e gera o MP4.

## Instalação

**Pessoal (todas as suas conversas do Claude Code)**
```bash
cp -r skills/video-programatico skills/video-frame-a-frame ~/.claude/skills/
```

**Em um repositório (compartilhado com o time, versionado no Git)**
```bash
mkdir -p .claude/skills
cp -r skills/video-programatico skills/video-frame-a-frame .claude/skills/
```

Depois disso, basta pedir um vídeo no chat do Claude Code (ou invocar por nome, ex. `/video-programatico`) dentro da pasta/perfil onde as skills foram copiadas.

## Dependências (só para gerar o MP4)

- Python 3.10+ e `pip install --break-system-packages -r requirements.txt` (playwright, imageio-ffmpeg, numpy)
- Um Chromium/Edge/Chrome disponível:
  - No sandbox do Claude Code, o Chromium já vem pré-instalado (nada a fazer, use `--navegador auto`, que é o padrão).
  - Fora do sandbox (ex.: rodando no computador do usuário via dispositivo conectado), rode `playwright install chromium` uma vez, ou use `--navegador msedge`/`chrome` se um deles já estiver instalado.

A animação HTML abre em qualquer navegador sem dependências, mesmo sem Python.

## Uso direto dos scripts

```bash
# validar frames antes de renderizar (gera um PNG com várias prévias; abra com a ferramenta Read)
python skills/video-programatico/scripts/preview_frames.py video.html preview.png --frames 45 180 330 480

# renderizar o MP4 final
python skills/video-programatico/scripts/renderizar_mp4.py video.html video.mp4 --musica calma|animada|nenhuma|arquivo.mp3 [--volume-musica 0.6] [--ate-frame 150]
```

## Regras embutidas

- Frames determinísticos (`desenhar(f)` puro), sons no mesmo instante do evento visual.
- Só ativos com direito de uso: tudo gerado por código, imagens/logos fornecidos pelo usuário, áudio sintetizado ou arquivo licenciado.
- Dados pessoais sempre fictícios (LGPD).

## O que mudou em relação ao kit original (Copilot)

- **Instalação**: pastas `skills/` copiadas para `~/.claude/skills/` (pessoal) ou `.claude/skills/` de um repositório (time), em vez de `~/.copilot/skills` / `.github/skills` e do fluxo `copilot plugin install`.
- **Navegador padrão do renderizador**: `--navegador auto` tenta primeiro o Chromium embutido do Playwright (já presente no sandbox do Claude Code) e só então cai para Edge/Chrome do sistema — o original assumia sempre o Edge do Windows.
- **Validação visual**: em vez do truque de `page.evaluate` num "navegador integrado" específico do Copilot, cada skill ganhou `scripts/preview_frames.py`, que gera uma prancha de contato em PNG a partir da própria animação HTML; o Claude abre esse PNG com a ferramenta **Read** para inspecionar os quadros.
- **Execução longa**: as instruções passaram a recomendar rodar o render em segundo plano com log em arquivo, adequado ao limite de tempo das chamadas de shell do Claude Code.
- O motor de animação (`template.html`) e a síntese de áudio (`renderizar_mp4.py`) são os mesmos do kit original — só o bloco de abertura do navegador foi generalizado.

## Higgsfield

O repositório `higgsfield-ai/higgsfield` é um orquestrador de treino distribuído de LLMs e **não gera vídeo**; não é dependência deste kit. A plataforma comercial Higgsfield AI pode ser usada manualmente para pós-produção do MP4.
