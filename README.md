# API de Gestão de Estoque

## 📖 Sobre o Projeto

Este projeto é uma API RESTful completa e robusta para um **Sistema de Gerenciamento de Estoque (IMS - Inventory Management System)**, desenvolvida com o objetivo de simular um ambiente de produção real. A API foi construída utilizando **Python** com o framework **Django** e **Django REST Framework (DRF)**, seguindo as melhores práticas de desenvolvimento, segurança e performance.

O propósito principal é fornecer um backend poderoso e flexível que possa ser consumido por diversas aplicações frontend (como um painel web, um aplicativo móvel ou um sistema de ponto de venda - PDV), automatizando e centralizando todas as operações de um estoque.

---

## ✨ Funcionalidades Principais

A API oferece um conjunto completo de funcionalidades para a gestão de ponta a ponta:

#### 1. **Gestão de Entidades Básicas**
- ✅ CRUD completo para **Produtos**, **Categorias**, **Fornecedores** e **Clientes**.

#### 2. **Controle de Estoque e Auditoria**
- ✅ **Múltiplos Armazéns**: Gerencie o estoque em diferentes locais físicos.
- ✅ **Movimentação Transacional**: Endpoints seguros para **Entrada** e **Saída** de estoque, garantindo a consistência dos dados com transações atômicas.
- ✅ **Histórico Completo**: Um endpoint de auditoria (`/api/produtos/{id}/historico/`) para rastrear cada movimentação de um produto específico.

#### 3. **Fluxos de Trabalho Automatizados**
- ✅ **Pedidos de Compra**: Crie pedidos para fornecedores. Ao marcar um pedido como "Recebido", a API **automaticamente** dá entrada dos produtos no estoque.
- ✅ **Pedidos de Venda**: Crie pedidos para clientes. A API **valida a disponibilidade** de estoque antes de permitir que um pedido seja "Despachado", e então **automaticamente** dá baixa dos produtos.

#### 4. **Segurança e Controle de Acesso (RBAC)**
- ✅ **Autenticação JWT**: Sistema de login seguro baseado em JSON Web Tokens (Access e Refresh tokens).
- ✅ **Permissões por Papel**: Controle de acesso baseado em grupos (`Gerentes`, `Operadores`), onde apenas usuários autorizados podem executar ações críticas (como criar produtos ou ver relatórios).

#### 5. **Inteligência de Negócio e Relatórios**
- ✅ **Filtros e Buscas Avançadas**: Endpoints com capacidade de filtragem por múltiplos critérios (ex: por categoria, por preço) e busca por texto livre.
- ✅ **Relatórios Customizados**: Endpoint dedicado para relatórios, como o de **"Produtos com Baixo Estoque"**.
- ✅ **Endpoint de Dashboard**: Um único endpoint (`/api/dashboard/`) que fornece dados agregados e prontos para consumo, como:
  - Valor Total de Vendas e Compras.
  - Valor Total do Inventário.
  - Contagem de produtos com baixo estoque.
  - Top 5 produtos mais vendidos.

#### 6. **Integração e Automação**
- ✅ **Webhooks Proativos**: A API notifica automaticamente um sistema externo (via webhook) quando um evento importante ocorre, como um produto atingindo seu nível mínimo de estoque.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:**
  - ![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
  - ![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django)
  - ![Django REST Framework](https://img.shields.io/badge/DRF-3.15-A30000?style=for-the-badge)
- **Banco de Dados:**
  - ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql) (Recomendado para produção)
  - ![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite) (Utilizado em desenvolvimento)
- **Autenticação:**
  - ![JWT](https://img.shields.io/badge/JWT-JSON_Web_Tokens-000000?style=for-the-badge&logo=jsonwebtokens) (via `djangorestframework-simplejwt`)
- **Outras Bibliotecas:**
  - `django-filter`: Para filtros avançados.
  - `python-decouple`: Para gerenciar variáveis de ambiente.
  - `requests`: Para o envio de Webhooks.

---

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e rodar o projeto na sua máquina.

**1. Clone o Repositório:**
```bash
git clone [https://github.com/seu-usuario/api-gestao-estoque.git](https://github.com/seu-usuario/api-gestao-estoque.git)
cd api-gestao-estoque
```

**2. Crie e Ative o Ambiente Virtual:**
```bash
# Criar o venv
python -m venv venv

# Ativar no Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Ativar no macOS/Linux
source venv/bin/activate
```

**3. Instale as Dependências:**
```bash
pip install -r requirements.txt
```
*(Nota: Você precisará criar um arquivo `requirements.txt` com o comando `pip freeze > requirements.txt`)*

**4. Configure as Variáveis de Ambiente:**
- Crie um arquivo chamado `.env` na raiz do projeto.
- Adicione as seguintes variáveis ao arquivo:
  ```
  DJANGO_SECRET_KEY=sua-chave-secreta-aqui
  WEBHOOK_BAIXO_ESTOQUE_URL=[https://webhook.site/sua-url-unica](https://webhook.site/sua-url-unica)
  ```

**5. Aplique as Migrações do Banco de Dados:**
```bash
python manage.py migrate
```

**6. Crie um Superusuário (para acesso ao Admin):**
```bash
python manage.py createsuperuser
```

**7. Inicie o Servidor de Desenvolvimento:**
```bash
python manage.py runserver
```

A API estará disponível em `http://127.0.0.1:8000/`.

---

## 🗺️ Endpoints da API

A documentação completa dos endpoints e seus parâmetros pode ser explorada através da API Navegável do DRF ao iniciar o servidor.

- **Raiz da API:** `/api/`
- **Autenticação:** `/api/token/`
- **Produtos:** `/api/produtos/`
- **Pedidos de Venda:** `/api/pedidos/venda/`
- **Dashboard:** `/api/dashboard/`
- ... e muitos outros.

---

## 👨‍💻 Autor

Desenvolvido por **[Seu Nome]**.

- **LinkedIn:** `https://linkedin.com/in/seu-linkedin`
- **GitHub:** `https://github.com/seu-usuario`