# YouTube Video Downloader

Aplicação web em Streamlit para baixar vídeos do YouTube com seleção de qualidade (resolução/FPS) usando `pytubefix`.

## Funcionalidades
- Carregamento de informações do vídeo via URL
- Visualização de thumbnail, título, autor, duração e visualizações
- Seleção de qualidade/formato disponível
- Download do vídeo para a pasta `Downloads`
- Botão para salvar o arquivo diretamente no navegador

## Tecnologias
- Python
- Streamlit
- pytubefix
- `uv` (gerenciador de pacotes e ambiente)

## Requisitos
- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Instalação
1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd pytube-download
```

2. Sincronize as dependências com `uv`:
```bash
uv sync
```

## Como executar
Inicie a aplicação com:
```bash
uv run streamlit run main.py
```

Depois, abra no navegador o endereço exibido no terminal (normalmente `http://localhost:8501`).

## Estrutura do projeto
```text
.
├── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Observações
- Use a ferramenta apenas para conteúdos que você tenha autorização para baixar.
- Alguns vídeos podem ter restrições de download.
