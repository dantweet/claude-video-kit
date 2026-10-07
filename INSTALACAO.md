# Tutorial de Instalação — claude-video-kit

Skills do Claude Code para gerar vídeos MP4 programados frame a frame (canvas HTML), com trilha de fundo e efeitos sonoros sincronizados. Este tutorial cobre a instalação no **Windows** (PowerShell); os comandos de `pip`/`python` valem também para Linux/macOS, exceto os passos de extração do zip e de cópia de pastas, indicados à parte.

## 1. Pré-requisitos

| Requisito | Como verificar |
|---|---|
| Python 3.10+ | `python --version` |
| pip funcionando no mesmo Python | `python -m pip --version` |
| Claude Code instalado | já em uso, se você está lendo isto por ele |

> **Atenção a múltiplas instalações de Python.** Se o Windows tiver mais de uma versão instalada (comum quando se instala o Python mais de uma vez ao longo do tempo), o comando `python` e o comando `pip` podem apontar para instalações diferentes — e aí um pacote instalado via `pip` não aparece quando você roda `python`. Para checar:
> ```powershell
> where.exe python
> where.exe pip
> ```
> Se os caminhos forem de pastas diferentes (ex.: `Python314` vs `Python313`), **sempre use `python -m pip install ...`** em vez de `pip install ...` solto, para garantir que a instalação vai para o Python que você realmente vai executar. Ou use o launcher `py -3.13 ...` / `py -3.14 ...` para fixar a versão em todos os comandos.

## 2. Extrair o pacote

O Windows não tem o comando `unzip` por padrão. Use:
```powershell
Expand-Archive -Path claude-video-kit.zip -DestinationPath . -Force
cd claude-video-kit
```
Confirme que você está na pasta certa (deve conter `README.md`, `requirements.txt` e a pasta `skills\`):
```powershell
dir
```

## 3. Instalar as dependências Python

```powershell
python -m pip install -r requirements.txt
```
Isso instala `playwright`, `imageio-ffmpeg` e `numpy`. Se aparecer "Requirement already satisfied" mas depois um teste disser `ModuleNotFoundError`, é o problema de múltiplas instalações descrito no passo 1 — repita o comando com `python -m pip` (não `pip` sozinho) ou fixe a versão com `py -3.13 -m pip install -r requirements.txt`.

## 4. Garantir um navegador para o Playwright

O renderizador precisa de um Chromium, Edge ou Chrome instalado para desenhar os quadros em segundo plano (headless). Teste:
```powershell
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(); print('OK:', b.version); b.close(); p.stop()"
```
- Se funcionar, ótimo — os scripts vão usar esse Chromium automaticamente (`--navegador auto`, o padrão).
- Se der erro pedindo para instalar o navegador, rode uma vez:
  ```powershell
  python -m playwright install chromium
  ```
- Alternativa (mais rápida, pois o Windows já traz o Edge): passe `--navegador msedge` nos comandos dos passos 5 e 6, sem precisar instalar nada extra.

## 5. Testar a prévia visual (antes de renderizar o MP4)

```powershell
python skills\video-programatico\scripts\preview_frames.py skills\video-programatico\assets\template.html preview.png --frames 15 150 300 450 --colunas 2
```
Abra `preview.png` no Explorador de Arquivos. Deve mostrar 4 quadros de exemplo (fundo animado, gráfico de barras, lista de passos numerados e tela final com botão de play). Se as imagens aparecerem corretamente, o motor de desenho está funcionando.

## 6. Testar o render de MP4

Primeiro um teste curto (só os 3 segundos iniciais, mais rápido):
```powershell
python skills\video-programatico\scripts\renderizar_mp4.py skills\video-programatico\assets\template.html video.mp4 --musica nenhuma --ate-frame 90
```
Abra `video.mp4` — deve tocar normalmente. Depois, se quiser, renderize o exemplo completo (sem `--ate-frame`, com música):
```powershell
python skills\video-programatico\scripts\renderizar_mp4.py skills\video-programatico\assets\template.html video_completo.mp4 --musica calma
```

Confira o resultado com o ffmpeg incluso no pacote `imageio-ffmpeg`:
```powershell
$FFMPEG = python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"
& $FFMPEG -hide_banner -i video.mp4
```
Espera-se ver `h264 ... 1280x720 ... 30 fps` e `Audio: aac ... stereo`. O exit code 1 ao final é normal (o comando não recebeu arquivo de saída, só a inspeção).

Repita os passos 5 e 6 trocando `video-programatico` por `video-frame-a-frame` para validar a segunda skill.

## 7. Instalar como skill no Claude Code

Isso é o que faz o Claude passar a reconhecer e usar as skills automaticamente quando você pedir um vídeo no chat.

**Opção A — pessoal (todas as suas conversas nesta máquina):**
```powershell
mkdir "$env:USERPROFILE\.claude\skills" -Force
Copy-Item -Recurse -Force skills\video-programatico "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse -Force skills\video-frame-a-frame "$env:USERPROFILE\.claude\skills\"
```

**Opção B — por repositório (compartilhado com o time via Git):**
```powershell
mkdir .claude\skills -Force
Copy-Item -Recurse -Force skills\video-programatico .claude\skills\
Copy-Item -Recurse -Force skills\video-frame-a-frame .claude\skills\
```
Rode isso dentro da pasta raiz do repositório onde você quer disponibilizar as skills para o time, e faça commit da pasta `.claude\skills\`.

## 8. Usar

Abra uma conversa do Claude Code (nessa máquina ou, se instalou por repositório, com aquela pasta como diretório de trabalho) e peça em português o que você quer:

> *"crie um vídeo de 20 segundos, 16:9, explicando os benefícios do novo processo seletivo da empresa"*

> *"faça um vídeo tutorial mostrando como cadastrar um cliente no ServiceNow, com cursor e cliques"*

O Claude segue o procedimento do `SKILL.md` correspondente: briefing → storyboard → edição do roteiro no template → validação com `preview_frames.py` → render com `renderizar_mp4.py` → entrega do `.html` e do `.mp4`. Se ele não acionar a skill sozinho, force citando o nome: `/video-programatico` ou `/video-frame-a-frame`.

## 9. Solução de problemas (erros já vistos)

| Erro | Causa | Solução |
|---|---|---|
| `unzip : O termo 'unzip' não é reconhecido...` | PowerShell não tem `unzip` | Use `Expand-Archive -Path ... -DestinationPath . -Force` |
| `ModuleNotFoundError: No module named 'playwright'` logo após um `pip install` que disse "already satisfied" | `python` e `pip` apontam para instalações diferentes do Python | Rode `where.exe python` e `where.exe pip`; use sempre `python -m pip install ...` ou fixe a versão com `py -3.13 ...` |
| Erro pedindo para instalar o executável do navegador ao rodar `renderizar_mp4.py`/`preview_frames.py` | Nenhum Chromium do Playwright instalado | `python -m playwright install chromium`, ou use `--navegador msedge` (Windows já traz o Edge) |
| `canvas ...: largura e altura precisam ser pares` | Um `FORMATO`/resolução customizado no roteiro ficou ímpar | Ajuste a resolução no HTML para valores pares (os formatos padrão do template já são pares) |
| `ffmpeg falhou (...)` | Geralmente áudio ou vídeo corrompido no meio do processo | Rode de novo com `--ate-frame 90` para isolar se o problema é no vídeo ou no áudio; cheque o `_log_mp4.txt` se estiver usando |

## 10. Referência rápida de comandos

```powershell
# prévia visual
python skills\<skill>\scripts\preview_frames.py <animacao.html> <preview.png> --frames 60 200 400 600 --colunas 2

# render final
python skills\<skill>\scripts\renderizar_mp4.py <animacao.html> <saida.mp4> --musica calma|animada|nenhuma|<arquivo.mp3> [--volume-musica 0.6] [--ate-frame 150] [--navegador auto|chromium|msedge|chrome]
```

Troque `<skill>` por `video-programatico` ou `video-frame-a-frame`, conforme o tipo de vídeo.
