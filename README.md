# langchain-ai-app

A demo that answers natural-language questions about onchain Uniswap swap data by letting a LangChain agent query an SQD (Subsquid) GraphQL squid. It has two parts: a Python Flask backend that runs the agent, and a Next.js frontend that sends prompts to it.

This is an example project from [SQD](https://sqd.dev) (Subsquid Labs). It shows one way to put a language-model agent in front of data indexed with the SQD stack.

## What it does

A user types a prompt (for example, a question about Uniswap swaps). The frontend sends the prompt to the backend's HTTP endpoint. The backend runs a LangChain agent backed by OpenAI that has three tools:

- introspect the GraphQL schema of a squid and summarize it as text,
- run a GraphQL query against that squid,
- sort the returned results by timestamp or block number.

The agent uses these tools to build and execute a query, then returns a text answer. The squid it queries is a Uniswap swaps squid served at `https://squid.subsquid.io/swaps-squid/v/v1/graphql`.

## Repository layout

- `llama-backend/`: Flask app (`main.py`) exposing the agent over HTTP. The agent and its tools are defined in `base/base.py`. Uses `langchain`, `llama-index`, and the OpenAI API.
- `llama-frontend/`: Next.js (App Router) app. The prompt form (`src/app/_components/emoji-form/index.tsx`) POSTs to the backend's `/post_json` endpoint. The frontend was adapted from the [pondorasti/emojis](https://github.com/Pondorasti/emojis) template, so some files still carry that template's naming.

## Backend

### Endpoints

- `GET /` and `GET /about`: return a placeholder JSON message.
- `POST /post_json`: accepts JSON `{ "prompt": "..." }` with `Content-Type: application/json` and returns `{ "text": "..." }` with the agent's answer.

### Requirements

- Python 3.11
- An OpenAI API key

The backend reads the OpenAI key from a variable in the source (`main.py`). Set your own key there or wire it to an environment variable before running. Do not commit a real key.

### Install and run

```bash
cd llama-backend
pip install -r requirements.txt
python3 main.py
```

This starts the development server on port `5000` (override with the `PORT` environment variable). For production, the included `Procfile` runs the app with Gunicorn:

```
web: gunicorn main:app --timeout 900
```

Key dependencies (see `requirements.txt`): `Flask`, `flask-cors`, `langchain`, `llama-index`, `llama-hub`, `openai`, `requests`, `python-dotenv`, `gunicorn`.

## Frontend

A Next.js App Router application that renders a prompt box and shows the agent's reply with a typewriter effect. The request target is set in `src/app/_components/emoji-form/index.tsx`; change it to point at your own backend deployment.

### Install and run

The project includes both a `bun.lockb` and a `package-lock.json`, so you can use Bun or npm.

```bash
cd llama-frontend
npm install        # or: bun install
npm run dev        # starts Next.js on port 3002
```

Other scripts (`package.json`): `build`, `start`, `lint`, `prisma:studio`, `prisma:push`.

Note: the frontend retains parts of the upstream emoji-generator template (Prisma schema, Replicate, Vercel Blob/KV references). Those are not required for the prompt-to-backend flow described above and can be removed or ignored for that use case.

## How this fits into SQD

SQD is an open data platform for Web3. Squids are indexers built with the Squid SDK that expose indexed onchain data, including over a GraphQL API. This project queries one such squid (Uniswap swaps) and uses a language-model agent to translate natural-language prompts into GraphQL queries against it.

- SQD docs: https://docs.sqd.dev
- Squid SDK docs: https://docs.sqd.dev/en/sdk
- SQD: https://sqd.dev

## Related projects used here

- [LangChain](https://python.langchain.com): agent and tool framework
- [LlamaIndex](https://www.llamaindex.ai): used for an alternative agent setup in `base/base.py`
- [Flask](https://flask.palletsprojects.com/en/1.1.x/): backend web framework
- [Next.js (App Router)](https://nextjs.org/docs/app): frontend framework
