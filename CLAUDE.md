# Documentação sobre Química Biofísica Computacional

Site estático em Zensical, publicado em patrickallanfaustino.github.io.
Conteúdo em português do Brasil, público-alvo: alunos de iniciação científica e de pós-graduação começando em simulação de biomoléculas.

## Estrutura
- `docs/` — fonte markdown. Config em `zensical.toml`.
- Imagens em `docs/assets/`, sempre em caminho relativo.
- Publicação automática via `.github/workflows/docs.yml` ao dar push em `main` ou `master`.

## Convenções
- Todo tutorial de instalação começa com um bloco `!!! info "Testado em"` contendo distro, versão do GROMACS, CUDA/ROCm e data.
- Comandos de terminal sempre em blocos ```bash.
- Nunca versionar binários (.deb, .zip) — usar link de download no texto.
- Ambiente Python em `.venv`; ativar antes de rodar `zensical`.

## Antes de propor commit
Rodar `zensical build --clean` e confirmar que não há links quebrados.