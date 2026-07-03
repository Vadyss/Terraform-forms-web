# Interní konfigurační portál

Interní portál pro spouštění placeholder Terraform deploymentů přes
jednoduchý formulář. Frontend (Vite + React) mluví s reálným FastAPI
backendem, který nad každým jobem spouští skutečné `terraform init/plan/apply/destroy`
proti vygenerovanému `null_resource` (žádný reálný cloud provider, jen
lokální `/tmp` state).

Flow: formulář → plán → potvrzení → apply → výsledek → (volitelně) destroy.

## Stack

**Frontend**
- Vite + React + TypeScript
- TanStack Query (`@tanstack/react-query`) pro fetch/polling stavu jobu

**Backend**
- FastAPI + Uvicorn
- Pydantic (validace `DeploymentConfig`)
- Terraform CLI spouštěné přes `asyncio.create_subprocess_exec`

## Spuštění

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend běží na `http://127.0.0.1:8000`. Vyžaduje nainstalovaný `terraform`
binary v `PATH` (joby si vytvářejí vlastní pracovní adresář pod `/tmp/jobs`).

Volitelně lze nastavit `ALLOWED_ORIGINS` (comma-separated) pro CORS; bez
nastavení se povoluje jen `http://localhost:5173`.

### Frontend

```bash
npm install
npm run dev
```

Appka se spustí na `http://localhost:5173`. Vite dev server proxuje `/api`
na backend (`http://127.0.0.1:8000`), viz `vite.config.ts`.

## API

- `POST /api/deployments` — vytvoří job, na pozadí spustí `terraform init` +
  `plan`; vrátí `{ id }`. Po dokončení plánu přejde job do
  `awaiting_confirmation` s vygenerovaným `plan` (summary + risks).
- `GET /api/deployments` — seznam všech jobů.
- `GET /api/deployments/{id}` — aktuální stav jobu.
- `POST /api/deployments/{id}/apply` — z `awaiting_confirmation` spustí
  `terraform apply`; po dokončení `done` s `outputs` (ip, resourceId).
- `POST /api/deployments/{id}/destroy` — z `done` spustí `terraform destroy`;
  po dokončení `destroyed`.

Životní cyklus stavu jobu: `planning → awaiting_confirmation → applying →
done → destroying → destroyed`, s možnou odbočkou do `error` v kterémkoli
kroku.

Bezpečnostní opatření v backendu (viz komentáře v `backend/main.py` a
`backend/jobs/store.py`): striktní allowlist na poli `DeploymentConfig`
(brání shell/HCL injection do generovaného `main.tf`), validace `job_id`
jako UUID, limit počtu jobů v paměti (`backend/jobs/repository.py`),
ořezání interních cest z chybových hlášek. Endpointy zatím nemají
autentizaci/autorizaci — portál je určený jen pro lokální/interní použití.

## Použití

Portál je jedna stránka: formulář pro nový deployment nahoře, tabulka
aktuálních deploymentů dole.

**Deploy:**
1. Vyplňte `Název`, `Region`, `Velikost`, `Image` a odešlete formulář.
2. Po dokončení `terraform plan` se zobrazí souhrn plánu a seznam rizik.
3. Potvrďte plán tlačítkem `Potvrdit` — spustí se `terraform apply`.
4. Po dokončení (`Deployment dokončen`) jsou k dispozici výstupy `IP` a
   `ID prostředku`.

**Destroy:**
- V tabulce deploymentů má každý job ve stavu `Hotovo` tlačítko `Zrušit`,
  které spustí `terraform destroy`. Je to nevratná operace.

## Stavy jobu

| Stav                    | Význam                                                        |
|--------------------------|----------------------------------------------------------------|
| `planning`               | Probíhá `terraform init` + `plan`.                              |
| `awaiting_confirmation`  | Plán je hotový a čeká na potvrzení.                             |
| `applying`               | Probíhá `terraform apply`.                                     |
| `done`                   | Deployment dokončen, `outputs` obsahuje `ip` a `resourceId`.    |
| `error`                  | Selhání v kterémkoli kroku, detail v poli `error`.              |
| `destroying`             | Probíhá `terraform destroy`.                                   |
| `destroyed`              | Zrušeno, job zůstává v seznamu pro auditní účely.               |

## Poznámky

- Terraform state (tfstate) je uložen lokálně na serveru pod `/tmp/jobs/<id>`,
  ne v remote backendu.
- Zrušení deploymentu je nevratné.
- Portál v současné podobě vytváří pouze `null_resource` placeholder —
  žádná reálná cloud infrastruktura zatím nevzniká. Napojení reálného
  cloud providera vyžaduje úpravu `backend/terraform/generator.py`
  (nahradit `null_resource` skutečným resourcem a `ip` output napojit na
  jeho reálný atribut) — víc se měnit nemusí, zbytek pipeline je na to
  připravený.

## Struktura

```
backend/
  main.py                 # FastAPI app, endpointy, orchestrace plan/apply/destroy
  jobs/store.py            # DeploymentConfig (+ validace), Job (modely)
  jobs/repository.py       # JobRepository rozhraní + InMemoryJobRepository
  terraform/generator.py  # generuje main.tf (null_resource) z DeploymentConfig
  terraform/runner.py     # spouští terraform init/plan/apply/destroy/output
  requirements.txt

src/
  components/
    DeploymentForm.tsx   # formulář pro založení jobu
    JobStatusView.tsx    # polling + přepínání obrazovek podle stavu jobu
    ProgressBar.tsx
    screens/             # obrazovky pro jednotlivé stavy (Planning, Done, ...)
                          # + DeploymentList
  hooks/useJobPolling.ts  # TanStack Query polling GET /api/deployments/:id
  mocks/                  # MSW handlers/store — nevyužitý pozůstatek z doby
                          # před reálným backendem, aktuálně se nespouští
  types.ts                # sdílené typy (DeploymentConfig, Job, ...)
  App.tsx                 # formulář + tabulka deploymentů na jedné stránce
  main.tsx                # QueryClientProvider
```

## Napojení na reálnou databázi

`backend/jobs/repository.py` definuje abstraktní `JobRepository`
(`create`/`get`/`list_all`/`update`). Výchozí `InMemoryJobRepository`
drží joby v paměti procesu. Pro reálnou DB: implementujte `JobRepository`
proti vašemu DB driveru a v `repository.py` vyměňte řádek
`job_repository: JobRepository = InMemoryJobRepository()` za instanci nové
třídy — zbytek kódu (endpointy v `main.py`) přistupuje k datům výhradně
přes `job_repository`, takže se nikde jinde nic měnit nemusí.

---

Made by Adam Krúpa
