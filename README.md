# Financial Model Governance Engine (FMG)

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A governance engine for financial models: implement a model once, register a versioned set of parameters, trigger a run — and let the engine handle the rest of the lifecycle automatically.

---

## 📌 Overview

FMG's core mechanic is a **domino effect**: one call sets off a deterministic, auditable chain of steps —

**trigger → execution → checks → (planned) post-check governance actions**

You implement a model by subclassing `FinancialModelExecutor` and defining its `_run` logic. Once it's registered with a parameter set, triggering a run is a single API call — the engine owns dispatching execution, tracking run state, and (already, or soon) chaining into checks and downstream governance actions. The point is that versioning, auditability, and orchestration are platform concerns, not something every new model has to re-implement.

---

## 🏗️ Architecture & Design Principles

Clean Architecture / DDD-inspired layering — domain logic has zero framework dependencies. Five top-level layers:

- **`config/`** — Django settings, root urlconf.
- **`domain/`** — pure business logic (model contracts, entities, enums). No Django, no Celery, no I/O.
- **`application/`** — use-case orchestration. This is where the domino effect is actually implemented: services trigger execution and, on success, dispatch the next step in the chain.
- **`infra/`** — adapters to the outside world (Django ORM models, Celery task definitions).
- **`presentation/`** — the HTTP boundary (views, serializers, urls). Thin by design, no business logic.

> Folder tree intentionally omitted here — it's still being reshuffled as the project moves through remediation. Will be documented once it stabilizes.

### Architectural Decisions (ADRs)

- **Django**: mature ORM, migrations, and admin panel for free — governance tooling needs solid data modeling and audit visibility more than it needs a custom web framework. Frees up effort for the actual differentiator (execution orchestration, checks) instead of re-implementing CRUD/auth plumbing.
- **Celery + Redis**: the domino effect is implemented as a sequence of `.delay()` calls rather than a single declarative `chain`/`chord` — a task runs, and on success a service triggers the next task in the sequence (e.g. execution → checks). Offloading model execution — which can take anywhere from milliseconds to minutes (e.g. a historical VaR simulation) — to a worker decouples it from the HTTP request/response cycle. Redis serves as both the message broker and the Celery result backend.
- **PostgreSQL, append-only via DB triggers**: a `ModelRun` is treated as an immutable audit record once created — governance requires that a run's history can't be silently edited after the fact. Enforced at the storage layer via triggers, not just in application code, so the guarantee holds even against direct DB access.
- **Package manager**: currently `pyproject.toml`-based. No lockfile/resolver in place yet — migration to `uv` is planned for speed, but not started.

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose (v2.20+)
- Python 3.11+ (only needed for running things outside containers, e.g. local test runs)

### Installation & Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/<user>/fmg.git
   cd fmg
   ```

2. **Environment configuration**
   ```bash
   cp .env.example .env
   # fill in DB credentials, Redis URL, Django secret key, etc.
   ```

3. **Start everything**
   ```bash
   docker compose up --build
   ```
   This brings up Postgres, Redis, the Celery worker, and the Django API. `web` runs migrations automatically on startup, then serves at `http://localhost:8000`.

4. **(Temporary) Seed a model, version, and parameter set**

   There's no management command or fixture for this yet — for now it's done by hand via the Django shell:
   ```bash
   docker compose exec web python manage.py shell
   ```
   ```python
   from infra.django.models import FinancialModelORM, ModelVersionORM, ParameterVersionORM

   model = FinancialModelORM.objects.create(
       model_name="Portfolio VaR",
       description="Portfolio Value at Risk model",
       is_active=True,
   )
   ModelVersionORM.objects.create(model=model, version="0.1", code_version="prototype")
   ParameterVersionORM.objects.create(
       model=model,
       parameter_version="v1.0.3",
       parameter_set={"confidence_levels": [0.5, 0.90, 0.95, 0.99], "lookback_days": 500},
   )
   ```
   > TODO: replace this with a `seed_demo_data` management command or fixtures before this goes in front of anyone else.

---

## 🛠️ Usage & Examples

### 1. Define a model

Any model is a class implementing `FinancialModelExecutor._run`. Example — a historical Portfolio VaR/CVaR model:

```python
class PortfolioVaR(FinancialModelExecutor):
    def _run(self, params: dict) -> dict:
        confidence_levels = params["confidence_levels"]
        lookback_days = params["lookback_days"]

        config = self._load_config()
        prices = self._fetch_data(config["tickers"], lookback_days)
        portfolio_returns = self._compute_portfolio_returns(
            prices, np.array(config["weights"])
        )
        var_table = self._compute_var(portfolio_returns, confidence_levels)

        return {
            "tickers": config["tickers"],
            "lookback_days": lookback_days,
            "var_table": var_table,
        }
```
(Full implementation, in `domain/financial_models/portfolio_var.py`.)

### 2. Trigger a run

```bash
curl -X POST http://localhost:8000/api/v1/runs/ \
  -H "Content-Type: application/json" \
  -d '{"model_id": 1, "model_version_id": 1, "parameter_version_id": 1}'
```
```json
{"run_id": 42}
```

This is where the domino effect kicks off: the API only creates the run and returns immediately (`202`). Execution and downstream checks happen asynchronously via Celery.

### 3. Check the outcome

```bash
curl http://localhost:8000/api/v1/runs/42/
```

Returns the run's current status (`PENDING`, `RUNNING`, `OUTPUTS_GENERATED`, `COMPLETED`, `FAILED`) and, once complete, the model output.

---

## 🧪 Testing & Verification

Test suite uses `pytest` + `pytest-django`, split into three tiers:

| Tier | Location | What it exercises |
|---|---|---|
| Unit | `tests/unit/` | Pure application/domain logic against fakes (`FakeTaskDispatcher`, `InMemoryRunRepository`, etc.) — no DB, no broker. |
| Integration | `tests/integration/` | Full API → service → DB path against a real Postgres test DB, model factory monkeypatched, Celery in eager mode. |
| Smoke | `tests/smoke/` | End-to-end against a **real** Celery worker + broker — polls the run until completion, catching broker/serialization issues the eager-mode integration test can't. |

```bash
pytest tests/unit
pytest tests/integration --ds=config.settings.test
pytest tests/smoke -m integration --ds=config.settings.test
```

The integration tier runs Celery in eager mode on purpose — it's testing the API → service → DB path deterministically and fast. The smoke tier exists specifically to catch the class of bugs eager mode can't: broker connectivity, task serialization, actual async timing.

**No CI pipeline yet** — next item in the remediation plan. Current coverage: 4 unit tests, 1 integration test, 1 smoke test.

---

## 📈 Performance & Scalability

_TBD — no benchmarks yet._ Model execution is already offloaded asynchronously via Celery, decoupling it from the request/response cycle. Next steps: horizontal worker scaling, and extending the domino chain with the post-check governance actions stage (e.g. auto-flagging or auto-escalating failed checks).

## 🗺️ Roadmap

- CI pipeline (GitHub Actions)
- Post-check governance actions stage (auto-flagging / auto-escalation)
- `seed_demo_data` management command / fixtures, replacing the manual shell seeding above
- Package management migration to `uv`
- **Frontend UI** — a dashboard for browsing models, triggering runs, and inspecting results/checks. Stack not decided yet, likely React-based.

---

## 🤝 Contributing

Personal portfolio project — not currently accepting external contributions, but issues and suggestions are welcome.

---

## 📄 License

MIT
