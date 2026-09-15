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
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
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
* caching support;
* automated tests.

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

Finance operations are exposed through the `finance` route:

```text
POST /finance/receipt/upload
POST /finance/receipt/{receipt_id}/confirm
```

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
* PostgreSQL as the primary database.
* Deterministic document processing before AI fallback.
* Local OCR instead of a paid OCR API.
* `pdfplumber` for direct PDF text extraction.
* `pdf2image` for converting scanned PDF pages into images when OCR is required.
* `pytesseract` as the Python interface to Tesseract OCR.
* Environment-driven configuration using Pydantic Settings.
* JWT authentication.
* Alembic for database migrations.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- API ROUTE MAP -->

## API Route Map

### Auth

* `POST /auth/login` — Authenticate user and return JWT token.
* `POST /auth/register` — Register a new user.

### Finance

#### Receipt

* `POST /finance/receipt/upload` — Upload and process a payment receipt.
* `POST /finance/receipt/{receipt_id}/confirm` — Confirm the extracted receipt data and create the corresponding payment.

The confirmation operation coordinates Receipt, Payment, Beneficiary, and Institution.

> For a complete list and details of all endpoints, see the interactive API documentation at `/docs` after running the project.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

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
* **pytesseract** — Python interface for Tesseract OCR.
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

These choices are intended to keep the project simple and inexpensive while providing a foundation that can evolve as the application grows.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

To run the project locally, follow the steps below.

### Prerequisites

1. Python 3.13
2. Poetry
3. Tesseract OCR
4. Poppler
5. PostgreSQL or SQLite

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

### Environment

Create a `.env` file at the project root:

```env
ALGORITHM=HS256
SECRET_KEY=change-me
DATABASE_URL=sqlite+aiosqlite:///./dev.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

For PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/machadoComprovanteDB
```

### Installation

You can use the Makefile for common tasks:

* Install dependencies:

  ```bash
  make install
  ```

* Run database migrations:

  ```bash
  make migrate
  ```

* Start the API:

  ```bash
  make run
  ```

* Run tests:

  ```bash
  make test
  ```

* Lint:

  ```bash
  make lint
  ```

* Format:

  ```bash
  make format
  ```

Or manually:

```bash
git clone https://github.com/yourusername/machado-comprovante-api.git
cd machado-comprovante-api
```

Install dependencies:

```bash
poetry env use 3.13
poetry install
```

Run migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
fastapi dev app/main.py
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
http://localhost:8000/redoc
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

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

For API exploration and testing, use the interactive documentation available at `/docs`.

To run the tests:

```bash
pytest -v
```

For linting:

```bash
ruff check .
```

For formatting:

```bash
ruff format .
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

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
* [ ] Image preprocessing
* [ ] AI fallback for ambiguous receipts
* [ ] External file storage
* [ ] PWA / mobile upload flow
* [ ] Finance dashboard
* [ ] Advanced payment queries

See the [open issues](https://github.com/yourusername/machado-comprovante-api/issues) for the full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

This project is licensed under the MIT License.

See the [LICENSE](./LICENSE) file for details.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

Jorge Machado - [jorge.vmachado@gmail.com](mailto:jorge.vmachado@gmail.com)

Project Link: https://github.com/yourusername/machado-comprovante-api

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

This project uses and is inspired by the following open-source projects and technologies:

* [FastAPI](https://fastapi.tiangolo.com/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [pdfplumber](https://github.com/jsvine/pdfplumber)
* [pdf2image](https://github.com/Belval/pdf2image)
* [Pillow](https://python-pillow.org/)
* [pytesseract](https://github.com/madmaze/pytesseract)
* [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
* [Pydantic](https://docs.pydantic.dev/)
* [Alembic](https://alembic.sqlalchemy.org/)
* [Poetry](https://python-poetry.org/)
* [Img Shields](https://shields.io)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

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
