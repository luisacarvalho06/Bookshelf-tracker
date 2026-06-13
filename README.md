# Bookshelf Tracker

![CI](https://github.com/ventosincaos/Bookshelf-tracker/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Flask](https://img.shields.io/badge/flask-3.x-lightgrey)
![Version](https://img.shields.io/badge/version-1.0.0-green)

## O Problema

As soluções disponíveis para manter registro de leituras são plataformas sociais completas, que exigem cadastro, conexão com internet e armazenam dados em servidores de terceiros.
Para quem quer apenas um diário de leituras simples, local e privado, essas plataformas oferecem muito mais do que o necessário.

## A Solução

O **Bookshelf Tracker** é uma aplicação web conectada à nuvem, sem cadastro, sem rastreamento.
É um diário de leituras minimalista: você registra, organiza e revisita seus livros com total controle sobre seus dados, persistidos em banco de dados na nuvem via Supabase.

## Público-alvo

Qualquer pessoa que leia livros e queira manter um registro pessoal simples, organizado e visualmente agradável de suas leituras.

## Deploy

 Acesse a aplicação em produção: https://bookshelf-tracker-2e22.onrender.com

## Funcionalidades

- Adicionar livros com capa, título, autor, gênero, ano de publicação, avaliação (1-10 estrelas) e review pessoal
- Buscar livros pelo título e automaticamente resgatar capa, autor e ano via API Open Library
- Navegar entre os livros em um slider de cards
- Registrar a data em que o livro foi lido
- Remover livros individualmente
- Exportar a lista em formato `.json`
- Importar uma lista previamente exportada

## Preview

![Bookshelf Tracker](preview/Bookshelf-add.png)
![Bookshelf Tracker](preview/Bookshelf-form.png)
![Bookshelf Tracker](preview/Bookshelf-1.png)
![Bookshelf Tracker](<img width="595" height="174" alt="Bookshelf-test" src="https://github.com/user-attachments/assets/033e8a9c-0023-4952-a022-c178ff43ffaa" />


## Tecnologias

- Python 3.12
- Flask
- HTML + CSS + JavaScript
- pytest
- ruff
- Supabase (PostgreSQL)
- Render (Deploy)

## Dependências

- flask
- pytest
- werkzeug
- ruff
- requests
- gunicorn
- python-dotenv
- supabase

## API

Integração com [Open Library API](https://openlibrary.org/developers/api) para busca automática de capa, autor e ano de publicação a partir do título do livro.

## Banco de Dados

Integração com [Supabase](https://supabase.com) para persistência dos dados em nuvem (PostgreSQL).

## Instalação e Execução

1. Clone o repositório:
```bash
git clone https://github.com/ventosincaos/Bookshelf-tracker.git
cd Bookshelf-tracker
```

2. Crie e ative o ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Crie o arquivo `.env` na raiz do projeto:
SUPABASE_URL=https://seu-project-id.supabase.co
SUPABASE_KEY=sua-publishable-key

5. Rode o servidor:
```bash
python run.py
```

6. Acesse no navegador na porta indicada

## Testes

```bash
pytest tests/ -v
```

## Linting

```bash
ruff check app/
```

## Versão

1.0.0

## Autores

- ventosincaos — https://github.com/ventosincaos
- luisacarvalho06 — https://github.com/luisacarvalho06

## Disciplina

Bootcamp II

## Repositório

https://github.com/ventosincaos/Bookshelf-tracker
