# Online Multicompras

Sistema da loja com API Django/DRF e frontend React/Vite.

## Superfícies da API

- Público: `GET /api/catalog/products/` e detalhe de produto.
- Painel: JWT em `/api/auth/token/`; produtos administrativos, usuários, vendas e dashboard exigem usuário `is_staff`.
- Automação n8n: header `X-N8N-Token`; pode criar atualizações pendentes e conversas, mas não aprovar, editar ou consultar dados administrativos.

## Desenvolvimento local

1. Copie `.env.example` para `.env` e use credenciais locais.
2. Ative o ambiente Python e execute as migrações com `python manage.py migrate`.
3. Inicie a API com `python manage.py runserver`.
4. Em `frontend`, copie `.env.example` para `.env`, instale as dependências e rode `npm run dev`.

O catálogo fica em `http://localhost:5173/` e o painel em `http://localhost:5173/login`.
