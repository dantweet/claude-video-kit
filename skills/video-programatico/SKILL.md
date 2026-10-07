---
name: video-programatico
description: 'Gera qualquer vídeo MP4 com animação programada frame a frame em canvas HTML e som (trilha de fundo + efeitos sincronizados): vídeo explicativo, motion graphics, infográfico/gráfico animado, vinheta, abertura, logo animado, convite, comunicado, aula, campanha, post para redes sociais (16:9, 9:16 vertical, 1:1, 4:5). Use quando pedirem: criar vídeo, animação, motion, vinheta, intro, reels/stories, mp4, "com som/trilha", ou mencionarem Higgsfield para vídeo. Para tutorial de tela/sistema com cursor e cliques, prefira video-frame-a-frame.'
argument-hint: 'Tema do vídeo, público, duração, formato (16:9, 9:16, 1:1) e tom'
---

# Vídeo programático (frame a frame + som)

Todo frame é desenhado por código (`desenhar(f)`, determinístico) num canvas e convertido em MP4 (H.264 + AAC) com trilha e efeitos sintetizados e sincronizados aos eventos do roteiro. Não depende de gravação de tela, banco de imagens ou serviço externo.

- Template com motor de cenas, transições e primitivas: [assets/template.html](./assets/template.html)
- Renderizador MP4 + áudio: [scripts/renderizar_mp4.py](./scripts/renderizar_mp4.py)
- Validação visual sem navegador interativo: [scripts/preview_frames.py](./scripts/preview_frames.py)
- Para **tutorial de sistema/tela** (layout real, cursor, cliques, legendas de passo), use a skill `video-frame-a-frame`. O motor e o renderizador são os mesmos.

## Sobre o Higgsfield

`github.com/higgsfield-ai/higgsfield` é um orquestrador de GPU para **treino distribuído de LLMs**. Ele não gera vídeo nem áudio, então não entra no pipeline e não deve ser instalado. A plataforma comercial Higgsfield AI (outro produto, web) pode ser usada manualmente, depois, para pós-produção com IA sobre o MP4.

## Procedimento

1. **Briefing**: objetivo, público, mensagem principal, duração (15–60 s), formato (`16:9`, `1080p`, `9:16`, `1:1`, `4:5`), tom (institucional, animado, sóbrio), paleta/marca. Se faltar algo essencial, pergunte; senão, assuma o padrão e diga qual foi.
2. **Fidelidade**: números, nomes e fatos vêm de fonte real (código, planilha, documento do usuário). Não invente dados. Se for ilustrativo, rotule como exemplo. Dados pessoais devem ser fictícios (LGPD).
3. **Storyboard antes do código**. Monte uma tabela com cena, início–fim, visual, texto na tela, transição de entrada e sons. Ritmo:
   - mantenha cada texto legível por ≥ 2 s (cerca de 3 palavras/s);
   - uma ideia por cena;
   - abertura forte (até 3 s);
   - fechamento com mensagem ou CTA.
4. **Copie o template** para a pasta de saída do projeto (ex.: `videos/<tema>/video.html`) e edite só a seção ROTEIRO: `FORMATO`, `FPS`, `PALETA`, `FONTE`, `IMAGENS`, `CENAS`, `DURACAO`, `SONS`, `LEGENDAS` e as funções de cena `(tl, p)`.
   - **Tempo/easing**: `anim(t, a, b, de, para, E.outBack)`, `prog`, `entre`, `E.linear|inCubic|outCubic|inOut|outBack|outElastic|outBounce`.
   - **Texto**: `texto`, `textoSobe`, `maquinaEscrever`, `quebrar`.
   - **Formas**: `retangulo`, `circulo`, `linhaDesenhada`, `seta`, `check`.
   - **Composição**: `escala`, `camera` (zoom/pan), `fundoGradiente`, `fundoAnimado`, `particulas` (semente fixa).
   - **Dados**: `barras`, `contador` (pt-BR).
   - **Mídia**: `imagem` (arquivos de `IMAGENS`).
   - **Unidades**: use `U` (1% do menor lado) e frações de `W`/`H`, para que a cena se adapte a qualquer formato.
   - **Transições**: `corte`, `fade`, `slide`, `slideCima`, `zoom` e `wipe`, aplicadas na entrada de cada cena (`DURACAO_TRANSICAO`).
5. **Sons**: um evento por acontecimento visual, no mesmo `t`.
   - `whoosh` cerca de 0,15 s antes de cada transição;
   - `pop` quando um elemento aparece;
   - `impacto` quando o título "cai";
   - `subida` antes de uma revelação;
   - `tique` em contadores;
   - `ding`/`sucesso` na conclusão;
   - `digitar` em máquina de escrever;
   - `clique`, `erro` e `notificacao` também existem.

   `dur` controla a duração dos sons contínuos e `vol` o ganho (padrão 1). Música: `--musica calma|animada|nenhuma|<arquivo licenciado>`.
6. **Instale as dependências** uma vez (ver seção abaixo) e **valide os frames** gerando uma prancha de contato com momentos-chave (meio de cada cena e meio de cada transição):
   ```bash
   python <skill>/scripts/preview_frames.py video.html preview.png --frames 45 180 330 480 --colunas 2
   ```
   Depois abra `preview.png` com a ferramenta **Read** (ela exibe imagens). Em formato vertical, use `--colunas 1` ou ajuste a grade. Corrija:
   - texto cortado ou fora da área segura (margem de 5%; em 9:16, conteúdo no terço central);
   - contraste baixo;
   - elementos sobrepostos;
   - transições "vazias".
7. **Renderize** o MP4. Rode em segundo plano (processo longo), redirecionando o log para arquivo:
   ```bash
   python <skill>/scripts/renderizar_mp4.py video.html video.mp4 --musica animada > _log_mp4.txt 2>&1 &
   ```
   Depois acompanhe com `tail -f _log_mp4.txt` ou leia o arquivo periodicamente — execuções síncronas longas num único comando podem ser interrompidas pelo timeout da ferramenta de shell.
   - Para uma prévia rápida, use `--ate-frame 150`.
   - Em 1280x720, conte cerca de 1 min a cada 300 frames; 1080p leva cerca de 2x mais.
   - `--navegador auto` (padrão) usa o Chromium já incluído no ambiente do Claude Code; só troque para `msedge`/`chrome` se estiver rodando num computador do usuário (via dispositivo conectado) onde esses navegadores já existem.
8. **Verifique**: rode `<ffmpeg> -hide_banner -i video.mp4` (o caminho do executável vem de `python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`). O resultado deve mostrar a duração e a resolução esperadas, `h264` e `aac stereo`. O exit code 1 desse comando é normal, pois não há saída definida. Apague logs temporários.
9. **Entregue**: envie o `.html` e o `.mp4` ao usuário (ferramenta de envio de arquivo), com o storyboard resumido (cenas + tempos dos sons) e o comando para regerar.

## Instalação das dependências (ambiente de execução)

```bash
pip install --break-system-packages playwright imageio-ffmpeg numpy
```

O Chromium necessário para o `--navegador auto` já vem pré-instalado no sandbox do Claude Code (variável `PLAYWRIGHT_BROWSERS_PATH`); **não rode `playwright install`** nesse ambiente. Se este kit for usado fora do sandbox (por exemplo, numa máquina sem Chromium/Edge/Chrome), rode `playwright install chromium` uma vez.

## Regras

- `desenhar(f)` é **puro**: tudo deriva de `t = f / FPS`. Use `rng(seed)` em vez de `Math.random()` e nunca `Date.now()`; nada de estado acumulado entre frames.
- Não renomeie os globais do contrato com o renderizador: `FPS`, `TOTAL`, `DURACAO`, `SONS`, `desenhar`, `window.pronto` e o canvas `#tela`. Largura e altura precisam ser **pares**.
- Use fontes locais (Segoe UI/Arial, ou a pilha padrão do sistema) ou fontes embutidas no próprio HTML. Não use fontes web remotas, porque o render pode rodar sem rede.
- Use **somente ativos com direito de uso**: formas e textos gerados por código, imagens e logos fornecidos pelo usuário (via `IMAGENS`) e áudio sintetizado ou arquivo licenciado. Não baixe imagens nem músicas da internet.
- Legibilidade: corpo de texto mínimo `U * 2.4`, títulos a partir de `U * 4`, contraste alto e no máximo cerca de 12 palavras na tela por vez.
- **Dados fictícios** em nomes, CPFs, e-mails e salários (LGPD). Nunca use dados reais de produção no vídeo.
- Se o pedido for de tela ou sistema com interação, mude para a skill `video-frame-a-frame`.
