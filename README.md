# Bookshelf Tracker

![CI](https://github.com/ventosincaos/Bookshelf-tracker/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Flask](https://img.shields.io/badge/flask-3.x-lightgrey)
![Version](https://img.shields.io/badge/version-1.0.0-green)

## O Problema

As soluções disponíveis para manter registro de leituras são plataformas sociais completas, que exigem cadastro, conexão com internet e armazenam dados em servidores de terceiros.
Para quem quer apenas um diário de leituras simples, local e privado, essas plataformas oferecem muito mais do que o necessário.

## A Solução

O **Bookshelf Tracker** é uma aplicação web que roda localmente, sem cadastro, sem rastreamento e sem dependência de serviços externos.
É um diário de leituras minimalista: você registra, organiza e revisita seus livros com total controle sobre seus dados.

## Público-alvo

Qualquer pessoa que leia livros e queira manter um registro pessoal simples, organizado e visualmente agradável de suas leituras.

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
![Bookshelf Tracker](preview/Tests.png)

## Tecnologias

- Python 3.12
- Flask
- HTML + CSS + JavaScript
- pytest
- ruff

## Dependências

- flask
- pytest
- werkzeug
- ruff
- requests
- gunicorn
- python-dotenv

## API

Integração com [Open Library API](https://openlibrary.org/developers/api) para busca automática de capa, autor e ano de publicação a partir do título do livro.

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

4. Rode o servidor:
```bash
python run.py
```

5. Acesse no navegador na porta indicada

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

ventosincaos — https://github.com/ventosincaos

## Disciplina

Bootcamp II

## Repositório

https://github.com/ventosincaos/Bookshelf-tracker
