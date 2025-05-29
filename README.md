# Encurtador de URL — Backend

Backend serverless para encurtamento de URLs. Utiliza AWS Lambda, API Gateway, DynamoDB e autenticação via Google Firebase.

## ✨ Funcionalidades

- Encurtar URLs (sem autenticação)
- Listar URLs criadas (apenas autenticado)
- Deletar URLs (apenas o criador pode excluir)
- Redirecionamento por código curto
- Registro de cliques para analytics (em desenvolvimento)
- Autenticação JWT via Firebase

---

## 🛠️ Tecnologias Utilizadas

- **AWS Lambda** (funções serverless)
- **API Gateway** (endpoints REST)
- **DynamoDB** (banco NoSQL)
- **Firebase Auth** (autenticação e validação de JWT)
- **Python 3.13** (código das lambdas)
- **AWS SAM** (infraestrutura como código)

---

## 🚀 Como executar localmente

1. **Pré-requisitos:**
   - Python 3.13+
   - AWS CLI configurado
   - AWS SAM CLI instalado
   - Conta na AWS

2. **Clone o repositório:**
   ```sh
   git clone https://github.com/mcoldibelli/cortaurl-backend
   cd cortaurl-backend

3. **Configure variáveis e segredos:**

- Adicione as credenciais do Firebase em um parâmetro no AWS SSM (ex: /cortaurl-firebase).
O conteúdo deve ser o JSON de service account do Firebase.

- Altere o valor do caminho do SSM na variável de ambiente FIREBASE_SSM_PATH no template SAM, se necessário.

4. Build e Deploy:
```
   sam build && sam deploy --guided
```

## 📚 Documentação dos Endpoints
Uma coleção para Postman/Insomnia está disponível na pasta /docs.


#### Encurtar uma URL

```http
  POST /shorten
```

| Body Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `original_url` | `string` | **Obrigatório**. URL que será encurtada |
| `expires_in_days` | `int` | Dias até expiração (opcional, padrão: 30) |

Exeplo de Request body:
```json
{
  "original_url": "www.google.com",
  "expires_in_days": 30
}
```
Response (201 Created):
```json
{
  "short_code": "abc123",
  "original_url": "www.google.com"
}
```

---
#### Listar URLs do usuário autenticado

```http
  GET /urls
```

| Header | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `Authorization`      | `string` | **Obrigatório**. Bearer JWT Token (Firebase) |

Response (200 OK):
```json
{
  "items": [
    {
      "short_code": "abc123",
      "original_url": "www.google.com",
      "created_at": "2025-05-29T14:06:57.830Z",
      "expires_at": "2025-06-28T14:06:57.830Z",
      "created_by": "firebase_user_uid"
    }
  ]
}
```
---
#### Deletar uma URL

```http
  DELETE /urls/${short_code}
```

| Header | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `Authorization`      | `string` | **Obrigatório**. Bearer JWT Token (Firebase) |
| `short_code`      | `string` | **Obrigatório**. Código da URL curta |

Response (204 No Content):
- Sem corpo de resposta.
---
#### Redicionar por short code

```http
  GET /${short_code}
```

| Header | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `short_code`      | `string` | **Obrigatório**. Código da URL curta |


Response (302 Found):
- Redirect para a URL original_url
---
#### Analytics de uma URL (Em desenvolvimento)

```http
  GET urls/${short_code}/analytics
```

| Header | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `Authorization`      | `string` | **Obrigatório**. Bearer JWT Token (Firebase) |
| `short_code`      | `string` | **Obrigatório**. Código da URL curta |


Response (200 OK):
- Redirect para a URL original_url
```json
{
  "total_clicks": 3,
  "clicks": [
    {
      "timestamp": "2025-05-29T14:17:25.000Z",
      "country": "BR",
      "ip": "189.1.2.3",
      "user_agent": "...",
      "referrer": "https://www.google.com"
    }
  ]
}
```
---
## 🔒 Autenticação
Autenticação JWT via Firebase (Google Sign-In).

Endpoints protegidos (listar, deletar, analytics) exigem header:
- Authorization: Bearer <id_token>
