@echo off
setlocal

REM ============================================================
REM CONFIGURACAO
REM Altere SOMENTE esta URL para o repositorio do projeto
REM ============================================================

set "REPO_URL=https://github.com/dantweet/claude-video-kit.git"

REM ============================================================
REM INICIO
REM ============================================================

echo.
echo ==========================================
echo        CONFIGURANDO REPOSITORIO GIT
echo ==========================================
echo.

REM Verifica se o Git esta instalado
where git >nul 2>&1
if %errorlevel% neq 0 (
echo [ERRO] Git nao encontrado.
echo Instale o Git e tente novamente.
pause
exit /b 1
)

REM Inicializa o repositorio
if not exist ".git" (
echo [1/6] Inicializando Git...
git init
) else (
echo [1/6] Repositorio Git ja existe.
)

REM Cria .gitignore se nao existir
if not exist ".gitignore" (
echo [2/6] Criando .gitignore...

```
(
    echo .gradle/
    echo .idea/
    echo build/
    echo **/build/
    echo local.properties
    echo *.iml
    echo .externalNativeBuild/
    echo .cxx/
    echo *.apk
    echo *.aab
    echo captures/
    echo .DS_Store
) > .gitignore
```

) else (
echo [2/6] .gitignore ja existe.
)

REM Configura branch main
echo [3/6] Configurando branch main...
git branch -M main

REM Configura origin
echo [4/6] Configurando repositorio remoto...

git remote remove origin >nul 2>&1
git remote add origin "%REPO_URL%"

REM Adiciona arquivos
echo [5/6] Adicionando arquivos...
git add .

REM Commit
echo [6/6] Criando commit...

git diff --cached --quiet
if %errorlevel% equ 0 (
echo.
echo Nenhuma alteracao para realizar commit.
) else (
git commit -m "Initial commit"
)

echo.
echo ==========================================
echo             ENVIANDO PARA GITHUB
echo ==========================================
echo.

git push -u origin main

if %errorlevel% neq 0 (
echo.
echo ==========================================
echo [ERRO] O push nao foi concluido.
echo ==========================================
echo.
echo Verifique:
echo - URL do repositorio
echo - autenticacao do GitHub
echo - se o repositorio remoto esta vazio
echo.
pause
exit /b 1
)

echo.
echo ==========================================
echo       REPOSITORIO ENVIADO COM SUCESSO!
echo ==========================================
echo.
echo Repositorio:
echo %REPO_URL%
echo.

pause
endlocal
