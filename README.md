[![GitHub stars][githubStar-img]][githubStar-url]
[![GitHub forks][githubForks-img]][githubForks-url]
[![GitHub issues][githubIssues-img]][githubIssues-url]
[![GitHub license][githubLicense-img]][githubLicense-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- TABLE OF CONTENTS -->

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#overview">Overview</a>
    </li>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#architecture">Architecture</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#environment-configuration">Environment Configuration</a></li>
        <li><a href="#generate-the-secret-key">Generate the Secret Key</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#local-infrastructure">Local Infrastructure</a></li>
        <li><a href="#running-the-application">Running the Application</a></li>
      </ul>
    </li>
    <li><a href="#docker">Docker</a></li>
    <li><a href="#production-docker-environment">Production Docker Environment</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#testing">Testing</a></li>
    <li><a href="#ci">Continuous Integration</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#technical-decisions">Technical Decisions</a></li>
    <li><a href="#api-route-map">API Route Map</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- OVERVIEW -->

<a id="overview"></a>

## 🚀 Overview

Comprovante is a personal finance RESTful API built with FastAPI and async SQLAlchemy.

The application is designed to process payment receipts in PDF and image formats, extract relevant information, allow the user to review and correct the extracted data, and register the confirmed payment.

The processing pipeline prioritizes deterministic and local processing, using OCR and external AI services only when necessary.

Main capabilities include:

* JWT authentication;
* receipt upload and processing;
* batch receipt processing;
* PDF text extraction;
* PDF-to-image conversion for OCR fallback;
* image OCR;
* deterministic receipt interpretation;
* beneficiary normalization;
* institution normalization;
* payment confirmation;
* PostgreSQL persistence;
* asynchronous database operations;
* pagination;
* Redis caching support;
* duplicate receipt detection;
* receipt reprocessing for failed processing;
* automated tests;
* Docker-based development and production environments;
* OpenAPI documentation;
* continuous integration with GitHub Actions.

---

<!-- ABOUT THE PROJECT -->

## About The Project

The project was built with FastAPI, async SQLAlchemy, and a domain-oriented architecture focused on clear responsibilities between routes, services, repositories, and schemas.

The main business context is organized around the `finance` domain, which coordinates the following entities:

* **Receipt** — uploaded payment receipt and its processing lifecycle;
* **Payment** — confirmed financial transaction;
* **Beneficiary** — normalized payment beneficiary;
* **Institution** — normalized financial institution.

The `FinanceService` acts as the orchestrator of operations that involve multiple entities.

For example, confirming a receipt follows this general flow:

```text
Receipt
   ↓
Check existing Payment
   ↓
Resolve Beneficiary
   ↓
Resolve Institution
   ↓
Create Payment
   ↓
Confirm Receipt
```

All operations that belong to the same confirmation process are executed within the same database transaction.

### Document Processing

The application supports PDF and image receipts.

PDF processing prioritizes direct text extraction:

```text
PDF
 ↓
pdfplumber
 ↓
Text found?
 ├── YES → Extracted text
 │
 └── NO
       ↓
    pdf2image
       ↓
   PDF pages → Images
       ↓
    pytesseract
       ↓
   Tesseract OCR
       ↓
   Extracted text
```

Image processing uses OCR:

```text
Image
 ↓
Pillow
 ↓
pytesseract
 ↓
Tesseract OCR
 ↓
Extracted text
```

After text extraction, the same interpretation pipeline is used for both document types.

The system prioritizes deterministic processing before using AI as a fallback.

---

<!-- ARCHITECTURE -->

## Architecture

The project follows a domain-oriented architecture designed to maintain clear separation of responsibilities.

The main structure is organized under `app/domain`:

```text
app/
├── core/
│
└── domain/
    ├── auth/
    │
    └── finance/
        ├── route.py
        ├── service.py
        │
        ├── receipt/
        │   ├── extraction/
        │   ├── interpretation/
        │   ├── service.py
        │   └── repository.py
        │
        ├── payment/
        │   ├── service.py
        │   └── repository.py
        │
        ├── beneficiary/
        │   ├── service.py
        │   └── repository.py
        │
        └── institution/
            ├── service.py
            └── repository.py
```

### Routes

Routes define the HTTP API and delegate operations to the appropriate service.

Finance operations are exposed through the `finance` route.

### Services

Services contain domain-specific operations.

Entity services are responsible for their own rules:

* `ReceiptService`
* `PaymentService`
* `BeneficiaryService`
* `InstitutionService`

`FinanceService` coordinates operations that involve multiple entities without duplicating their internal business rules.

### Repositories

Repositories are responsible for persistence and database access using async SQLAlchemy.

They do not contain cross-domain business orchestration.

### Schemas

Pydantic models are used for:

* API request validation;
* API response serialization;
* extracted receipt data;
* domain data contracts;
* structured validation.

Financial amounts use `Decimal` to avoid floating-point representation issues.

### Core

The `app/core` modules provide shared infrastructure, including:

* database configuration;
* authentication;
* security;
* settings;
* exceptions;
* logging;
* repositories;
* services;
* pagination;
* shared utilities.

### Key Architectural Decisions

* Domain-oriented organization.
* Entity-specific services with clear responsibilities.
* `FinanceService` as the orchestrator for multi-entity financial operations.
* Repository layer dedicated to persistence.
* Async-first database and I/O operations.
* PostgreSQL as the primary application database.
* SQLite used where appropriate for isolated tests/local test scenarios.
* Deterministic document processing before AI fallback.
* Local OCR instead of a paid OCR API.
* `pdfplumber` for direct PDF text extraction.
* `pdf2image` for converting scanned PDF pages into images when OCR is required.
* `pytesseract` as the Python interface to Tesseract OCR.
* Environment-driven configuration using Pydantic Settings.
* JWT authentication.
* Alembic for database migrations.
* Redis for caching.
* Docker Compose for local infrastructure and production-container validation.

---

<!-- API ROUTE MAP -->

## API Route Map

### Auth

* `POST /auth/login` — Authenticate user and return JWT token.
* `POST /auth/register` — Register a new user.

### Finance

#### Receipt

* `POST /finance/receipt/upload` — Upload and process a payment receipt.
* `POST /finance/receipt/upload/batch` — Upload and process multiple payment receipts.
* `POST /finance/receipt/{receipt_id}/confirm` — Confirm the extracted receipt data and create the corresponding payment.

The confirmation operation coordinates Receipt, Payment, Beneficiary, and Institution.

The complete and authoritative API contract is available through the generated OpenAPI documentation.

After starting the application, access:

```text
http://localhost:8000/docs
```

or:

```text
http://localhost:8000/redoc
```

---

<!-- TECHNICAL DECISIONS -->

## Technical Decisions

The project prioritizes simplicity, low cost, maintainability, and the use of free or open-source technologies whenever technically appropriate.

### Backend

* **FastAPI** — HTTP API framework with asynchronous support and automatic OpenAPI documentation.
* **SQLAlchemy** — ORM and database access layer.
* **Pydantic** — Data validation and serialization.
* **Pydantic Settings** — Environment-based application configuration.
* **Alembic** — Database migrations and schema versioning.
* **psycopg** — PostgreSQL driver.
* **aiosqlite** — Async SQLite driver for local development and tests.
* **PyJWT** — JWT token handling.
* **pwdlib[argon2]** — Secure password hashing.
* **FastAPI Pagination** — Pagination support for API responses.
* **Redis** — Caching infrastructure.

### Document Processing

* **pdfplumber** — Extraction of text from text-based PDF documents.
* **pdf2image** — Conversion of PDF pages into images when direct text extraction is unavailable.
* **Pillow** — Image loading and processing.
* **pytesseract** — Python interface to Tesseract OCR.
* **Tesseract OCR** — Local and open-source OCR engine for extracting text from images and scanned documents.
* **Poppler** — PDF rendering backend required by `pdf2image`.

The processing strategy prioritizes:

```text
1. Existing PDF text
2. Deterministic parsing
3. PDF-to-image conversion when necessary
4. Local OCR
5. AI fallback
6. Paid services only when necessary
```

The application does not depend on a paid OCR service for the MVP.

### Testing

* **pytest** — Test framework.
* **pytest-asyncio** — Async test support.
* **pytest-cov** — Test coverage.
* **factory-boy** — Test data factories.
* **freezegun** — Controlled date and time in tests.
* **testcontainers** — Ephemeral infrastructure for integration tests.

### Development

* **Poetry** — Dependency and environment management.
* **Ruff** — Linting and formatting.
* **Make** — Common development commands.
* **Docker Compose** — Local PostgreSQL/Redis infrastructure.

These choices are intended to keep the project simple and inexpensive while providing a foundation that can evolve as the application grows.

---

<!-- BUILT WITH -->

## Built With

### Core

* [![Poetry][Poetry]][Poetry-url] - Dependency and environment management
* [![FastAPI][FastAPI]][FastAPI-url] - Asynchronous web framework
* [![SQLAlchemy][sqlalchemy]][sqlalchemy-url] - ORM and database access
* [![Alembic][Alembic]][Alembic-url] - Database migrations
* [![Pydantic][Pydantic]][Pydantic-url] - Data validation and serialization
* [![Pydantic Settings][PydanticSettings]][PydanticSettings-url] - Environment configuration
* [![PyJWT][PyJWT]][PyJWT-url] - JWT authentication
* [![pwdlib][Pwdlib]][Pwdlib-url] - Password hashing
* [![FastAPI Pagination][FastAPIPagination]][FastAPIPagination-url] - Pagination
* [![Redis][Redis]][Redis-url] - Caching
* [![psycopg][psycopg]][psycopg-url] - PostgreSQL driver
* [![aiosqlite][aiosqlite]][aiosqlite-url] - Async SQLite driver

### Document Processing

* [![pdfplumber][pdfplumber]][pdfplumber-url] - PDF text extraction
* [![pdf2image][pdf2image]][pdf2image-url] - PDF page rendering for OCR
* [![Pillow][Pillow]][Pillow-url] - Image processing
* [![pytesseract][pytesseract]][pytesseract-url] - Python interface for Tesseract OCR
* [![Tesseract OCR][Tesseract]][Tesseract-url] - Local OCR engine

### Development and Testing

* pytest
* pytest-asyncio
* pytest-cov
* factory-boy
* freezegun
* testcontainers
* Ruff
* Docker
* Docker Compose
* GitHub Actions

---

<!-- GETTING STARTED -->

## Getting Started

To run the project locally, follow the steps below.

### Prerequisites

The local development environment requires:

1. Python 3.13
2. Poetry
3. Docker
4. Docker Compose
5. Git
6. Tesseract OCR
7. Poppler

PostgreSQL and Redis do not need to be installed directly on the host because the development Docker Compose file provides both services.

### Tesseract OCR

Tesseract is required for processing image-based receipts and scanned PDF documents.

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-por
```

Verify the installation:

```bash
tesseract --version
```

Verify that Portuguese is available:

```bash
tesseract --list-langs
```

The `por` language package is required for Portuguese receipts.

### Poppler

Poppler is required by `pdf2image` to convert PDF pages into images before OCR.

On Ubuntu/Debian:

```bash
sudo apt install poppler-utils
```

Verify the installation:

```bash
pdftoppm -v
```

---

## Environment Configuration

Create a `.env` file at the project root.

The repository provides `.env.example` as the reference configuration.

```env
SECRET_KEY="change-me"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

POSTGRES_USER=machadoComprovante
POSTGRES_PASSWORD=machadoComprovante
POSTGRES_DB=machadoComprovanteDB
DATABASE_URL="postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:5432/${POSTGRES_DB}"

REDIS_HOST="127.0.0.1"
REDIS_PORT=6379
REDIS_CACHE_TTL_SECONDS=3600

RECEIPT_BATCH_MAX_FILES=10
RECEIPT_MAX_FILE_SIZE_MB=10
RECEIPT_BATCH_MAX_SIZE_MB=25
```

Do not commit `.env` or `.env.prod` to Git.

Both files are intentionally ignored by `.gitignore`.

### Generate the Secret Key

Never use `change-me` outside a local development environment.

Generate a cryptographically secure secret key with Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Example:

```text
<generated-secret-key>
```

Copy the generated value to the `SECRET_KEY` variable in `.env`:

```env
SECRET_KEY="<generated-secret-key>"
```

For production, generate a new secret key specifically for the production environment.

Do not reuse the production secret in `.env.example`, source code, tests, GitHub repositories, or documentation.

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd machado-comprovante-api
```

Install Python 3.13 and configure Poetry to use it:

```bash
poetry env use 3.13
```

Install project dependencies:

```bash
poetry install
```

Alternatively, use the Makefile:

```bash
make install
```

Create the local environment file:

```bash
cp .env.example .env
```

Generate a local `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Replace `change-me` in `.env` with the generated value.

---

## Local Infrastructure

The development environment uses Docker Compose for PostgreSQL and Redis.

Start the infrastructure:

```bash
docker compose up -d
```

Check the services:

```bash
docker compose ps
```

The development services are available at:

```text
PostgreSQL: 127.0.0.1:5432
Redis:      127.0.0.1:6379
```

The API itself runs locally through Python/Poetry.

Stop the infrastructure:

```bash
docker compose down
```

To remove the PostgreSQL development volume as well:

```bash
docker compose down -v
```

> The `-v` option permanently removes the PostgreSQL data stored in the development volume.

---

## Database Migrations

With PostgreSQL running and the `.env` configured:

```bash
alembic upgrade head
```

Or:

```bash
make migrate
```

The application uses Alembic to manage database schema versions.

New migrations should be created through Alembic and committed to the repository.

---

## Running the Application

Start the API locally:

```bash
fastapi dev app/main.py
```

Or:

```bash
make run
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

Alternative documentation:

```text
http://localhost:8000/redoc
```

---

<!-- DOCKER -->

## Docker

The project includes a `Dockerfile` containing the runtime dependencies required by the application, including:

* Python 3.13;
* Tesseract OCR;
* Portuguese Tesseract language data;
* Poppler;
* Poetry dependencies.

The Docker image installs only production dependencies.

Build the image:

```bash
docker build -t machado-comprovante-api .
```

Run the container only when the required external PostgreSQL and Redis services are available.

For normal local development, use the development Docker Compose environment described above.

---

<!-- PRODUCTION DOCKER ENVIRONMENT -->

## Production Docker Environment

The repository contains a separate `docker-compose.prod.yml`.

The development `docker-compose.yml` must remain dedicated to local development and should not be changed to production configuration.

The production Compose environment contains:

```text
API
PostgreSQL
Redis
```

The services communicate through the Docker Compose network.

The production configuration uses:

* PostgreSQL 17.2;
* Redis 8.6.1;
* persistent PostgreSQL storage;
* PostgreSQL healthcheck;
* Redis healthcheck;
* API dependency on healthy PostgreSQL and Redis services;
* Alembic migrations during API startup;
* Uvicorn as the production application server.

### Production Environment File

Create `.env.prod` locally or directly on the production host.

Do not commit it.

The production environment file contains application and PostgreSQL variables, while Docker Compose provides the internal service addresses:

```env
SECRET_KEY="<production-secret>"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

REDIS_CACHE_TTL_SECONDS=3600

RECEIPT_BATCH_MAX_FILES=10
RECEIPT_MAX_FILE_SIZE_MB=10
RECEIPT_BATCH_MAX_SIZE_MB=25

POSTGRES_USER=machadoComprovante
POSTGRES_PASSWORD="<production-password>"
POSTGRES_DB=machadoComprovanteDB
```

The production Compose file internally configures:

```text
DATABASE_URL → postgres:5432
REDIS_HOST   → redis
REDIS_PORT   → 6379
```

Do not use `127.0.0.1` for these connections inside the production containers.

### Production Secret

Generate the production secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Use a different secret from the development environment.

### Validate Production Configuration

Before starting the production environment:

```bash
docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  config
```

Start the production environment:

```bash
docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  up --build
```

Run it in the background:

```bash
docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  up --build -d
```

Check the services:

```bash
docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  ps
```

Check API logs:

```bash
docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  logs -f api
```

The API container automatically executes:

```text
Alembic migrations
      ↓
Uvicorn
      ↓
FastAPI
```

The production Docker environment has been validated locally.

External hosting infrastructure is intentionally not defined yet.

---

<!-- USAGE -->

## Usage

The API allows users to:

1. Authenticate.
2. Upload a payment receipt.
3. Process the receipt automatically.
4. Review the extracted information.
5. Correct information when necessary.
6. Confirm the receipt.
7. Register the corresponding payment.
8. Query registered payments.

Example processing flow:

```text
Upload Receipt
      ↓
Validate File
      ↓
Extract Text
      ↓
Interpret Receipt
      ↓
Review Data
      ↓
Confirm Receipt
      ↓
Resolve Beneficiary
      ↓
Resolve Institutions
      ↓
Create Payment
```

### Batch Processing

The batch endpoint accepts multiple receipt files.

The application validates:

* maximum number of files;
* maximum individual file size;
* maximum total batch size;
* supported content types;
* duplicate files.

Current limits are configured through:

```env
RECEIPT_BATCH_MAX_FILES=10
RECEIPT_MAX_FILE_SIZE_MB=10
RECEIPT_BATCH_MAX_SIZE_MB=25
```

For API exploration and testing, use the interactive documentation available at `/docs`.

---

<!-- TESTING -->

## Testing

Run the complete test suite:

```bash
pytest -v
```

Or:

```bash
make test
```

Run tests with coverage:

```bash
pytest --cov=app
```

Run linting:

```bash
ruff check .
```

Or:

```bash
make lint
```

Run formatting:

```bash
ruff format .
```

Or:

```bash
make format
```

The project uses:

* pytest;
* pytest-asyncio;
* pytest-cov;
* factory-boy;
* freezegun;
* testcontainers.

Integration tests can use ephemeral infrastructure through Testcontainers.

---

<!-- CI -->

## Continuous Integration

The project uses GitHub Actions for continuous integration.

The CI pipeline runs independently for:

```text
Lint
  ↓
Ruff

Test
  ↓
Pytest
```

CI is executed for pushes to:

```text
main
develop
```

and for pull requests targeting these branches.

Required application secrets are configured through GitHub Actions Secrets rather than committed to the repository.

The current CI configuration uses:

* `ALGORITHM`;
* `SECRET_KEY`;
* `DATABASE_URL`;
* `ACCESS_TOKEN_EXPIRE_MINUTES`.

The `main` branch requires the CI checks to pass before merging pull requests.

---

<!-- ROADMAP -->

## Roadmap

* [x] Domain structure
* [x] Async persistence
* [x] JWT authentication
* [x] Native pagination
* [x] Alembic migrations
* [x] Automated tests
* [x] Lint and format
* [x] PDF text extraction
* [x] PDF-to-image conversion
* [x] Image OCR
* [x] Deterministic receipt interpretation
* [x] Receipt confirmation flow
* [x] Payment creation during receipt confirmation
* [x] Batch receipt processing
* [x] Duplicate receipt detection
* [x] Docker runtime
* [x] Production Docker Compose
* [x] GitHub Actions CI
* [x] OpenAPI documentation
* [ ] Image preprocessing
* [ ] AI fallback for ambiguous receipts
* [ ] External file storage
* [ ] PWA / mobile upload flow
* [ ] Finance dashboard
* [ ] Advanced payment queries
* [ ] External production hosting

See the project issues for the full list of proposed features and known issues.

---

<!-- CONTRIBUTING -->

## Contributing

Contributions are welcome! Follow the steps below to collaborate:

1. Fork the project.

2. Create your feature branch:

   ```bash
   git checkout -b feature/FeatureName
   ```

3. Commit your changes:

   ```bash
   git commit -m 'feat: Feature description'
   ```

4. Push to the branch:

   ```bash
   git push origin feature/FeatureName
   ```

5. Open a Pull Request.

Suggestions for improvements can also be opened as issues with the tag `enhancement`.

---

<!-- LICENSE -->

## License

This project is licensed under the MIT License.

See the `LICENSE` file for details.

---

<!-- CONTACT -->

## Contact

Jorge Machado - [jorge.vmachado@gmail.com](mailto:jorge.vmachado@gmail.com)

---

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

This project uses and is inspired by the following open-source projects and technologies:

* FastAPI
* SQLAlchemy
* pdfplumber
* pdf2image
* Pillow
* pytesseract
* Tesseract OCR
* Pydantic
* Alembic
* Poetry
* Img Shields

---

<!-- MARKDOWN LINKS & IMAGES -->

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/yourusername
[Poetry]: https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json
[Poetry-url]: https://python-poetry.org/
[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/
[sqlalchemy]: https://img.shields.io/badge/SQLAlchemy-306998?logo=python&logoColor=white
[sqlalchemy-url]: https://www.sqlalchemy.org/
[Alembic]: https://img.shields.io/badge/Alembic-23374D?logo=alembic&logoColor=white
[Alembic-url]: https://alembic.sqlalchemy.org/
[Pydantic]: https://img.shields.io/badge/Pydantic-008489?logo=pydantic&logoColor=white
[Pydantic-url]: https://docs.pydantic.dev/latest/
[PydanticSettings]: https://img.shields.io/badge/Pydantic_Settings-008489?logo=pydantic&logoColor=white
[PydanticSettings-url]: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
[PyJWT]: https://img.shields.io/badge/PyJWT-FF9900?logo=python&logoColor=white
[PyJWT-url]: https://pyjwt.readthedocs.io/en/stable/
[Pwdlib]: https://img.shields.io/badge/pwdlib-3776AB?logo=python&logoColor=white
[Pwdlib-url]: https://frankie567.github.io/pwdlib/
[FastAPIPagination]: https://img.shields.io/badge/FastAPI--Pagination-005571?logo=fastapi&logoColor=white
[FastAPIPagination-url]: https://github.com/uriyyo/fastapi-pagination
[Redis]: https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white
[Redis-url]: https://redis.io/
[aiosqlite]: https://img.shields.io/badge/aiosqlite-003B57?logo=sqlite&logoColor=white
[aiosqlite-url]: https://aiosqlite.omnilib.dev/en/latest/
[psycopg]: https://img.shields.io/badge/psycopg-2C5E8A?logo=postgresql&logoColor=white
[psycopg-url]: https://www.psycopg.org/psycopg3/docs/
[pdfplumber]: https://img.shields.io/badge/pdfplumber-3776AB?logo=python&logoColor=white
[pdfplumber-url]: https://github.com/jsvine/pdfplumber
[pdf2image]: https://img.shields.io/badge/pdf2image-3776AB?logo=python&logoColor=white
[pdf2image-url]: https://github.com/Belval/pdf2image
[Pillow]: https://img.shields.io/badge/Pillow-3776AB?logo=python&logoColor=white
[Pillow-url]: https://python-pillow.org/
[pytesseract]: https://img.shields.io/badge/pytesseract-3776AB?logo=python&logoColor=white
[pytesseract-url]: https://github.com/madmaze/pytesseract
[Tesseract]: https://img.shields.io/badge/Tesseract_OCR-16A085?logo=tesseract&logoColor=white
[Tesseract-url]: https://github.com/tesseract-ocr/tesseract
[githubStar-url]: https://github.com/yourusername/machado-comprovante-api/stargazers
[githubStar-img]: https://img.shields.io/github/stars/yourusername/machado-comprovante-api?style=for-the-badge
[githubForks-url]: https://github.com/yourusername/machado-comprovante-api/network
[githubForks-img]: https://img.shields.io/github/forks/yourusername/machado-comprovante-api?style=for-the-badge
[githubIssues-url]: https://github.com/yourusername/machado-comprovante-api/issues
[githubIssues-img]: https://img.shields.io/github/issues/yourusername/machado-comprovante-api?style=for-the-badge
[githubLicense-url]: ./LICENSE
[githubLicense-img]: https://img.shields.io/github/license/yourusername/machado-comprovante-api?style=for-the-badge
