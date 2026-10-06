import argparse
import zipfile
from datetime import datetime
import re
import shutil
from pathlib import Path

from tempfile import TemporaryDirectory

DATE_PATTERNS = (
    re.compile(r"(?<!\d)\d{4}\d{2}\d{2}(?!\d)"),
    re.compile(r"(?<!\d)\d{4}_\d{2}_\d{2}(?!\d)"),
)

ALLOWED_FILE_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Organiza documentos de pagamento.")

    parser.add_argument(
        "--source-dir",
        required=True,
        help="Diretório de origem dos documentos de pagamento.",
    )
    parser.add_argument(
        "--target-dir",
        default=Path.cwd() / "comprovantes",
        help="Diretório de destino para os documentos organizados.",
    )

    return parser


def resolve_target_dir(target_dir: str | Path) -> Path:
    normalized_target_dir = str(target_dir).strip()

    if normalized_target_dir == "/~":
        normalized_target_dir = "~"
    elif normalized_target_dir.startswith("/~/"):
        normalized_target_dir = "~/" + normalized_target_dir[3:]

    resolved_target_dir = Path(normalized_target_dir).expanduser().resolve()
    resolved_target_dir.mkdir(parents=True, exist_ok=True)
    return resolved_target_dir


def get_file_date(filename: str) -> datetime | None:
    for pattern in DATE_PATTERNS:
        match = pattern.search(filename)

        if not match:
            continue

        value = match.group(0)

        try:
            if "_" in value:
                return datetime.strptime(value, "%Y_%m_%d")

            return datetime.strptime(value, "%Y%m%d")
        except ValueError:
            continue

    return None


def has_date(filename: str) -> bool:
    return get_file_date(filename) is not None


def is_payment_file(file: Path) -> bool:
    return file.suffix.lower() in ALLOWED_FILE_EXTENSIONS and has_date(file.name)


def get_files_from_zip(source_dir: Path, target_dir: Path) -> list[Path]:
    with zipfile.ZipFile(source_dir) as zip_file:
        zip_file.extractall(target_dir)

    return [file for file in target_dir.rglob("*") if file.is_file()]


def get_files(source_dir: Path) -> list[Path]:
    return [file for file in source_dir.iterdir() if file.is_file()]


def resolve_files_dir(target_dir: Path, directory_name: str) -> Path:
    files_dir = target_dir / directory_name
    files_dir.mkdir(parents=True, exist_ok=True)

    return files_dir


def copy_files(files: list[Path], target_dir: Path) -> None:
    if not files:
        return

    print(f"Iniciando cópia dos arquivos para a pasta {target_dir.name}...")

    for file in files:
        shutil.copy2(file, target_dir / file.name)
        print(f"Arquivo copiado: {file.name}")

    print(f"{len(files)} arquivos enviados para a pasta {target_dir.name}.")


def resolve_files_by_date(files: list[Path]) -> dict[str, dict[str, list[Path]]]:
    files_by_date: dict[str, dict[str, list[Path]]] = {}

    for file in files:
        file_date = get_file_date(file.name)

        if not file_date:
            continue

        year = file_date.strftime("%Y")
        month = file_date.strftime("%m")

        files_by_date.setdefault(year, {})
        files_by_date[year].setdefault(month, []).append(file)

    return files_by_date


def copy_files_date(target_dir: Path, files: list[Path]) -> None:
    files_by_date = resolve_files_by_date(files)

    for year, files_by_month in files_by_date.items():
        year_dir = resolve_files_dir(target_dir, year)

        for month, month_files in files_by_month.items():
            month_dir = resolve_files_dir(year_dir, month)
            copy_files(month_files, month_dir)


def process_files(files: list[Path], target_dir: Path) -> tuple[int, int]:
    files_with_date = [file for file in files if is_payment_file(file)]
    if files_with_date:
        copy_files_date(target_dir, files_with_date)

    return len(files), len(files_with_date)


def resolve_files(source_dir: str | Path, target_dir: Path) -> tuple[int, int]:
    source = Path(source_dir).expanduser().resolve()

    if source.is_file() and source.suffix.lower() == ".zip":
        with TemporaryDirectory() as temporary_dir:
            files = get_files_from_zip(source, Path(temporary_dir))
            return process_files(files, target_dir)

    files = get_files(source)
    return process_files(files, target_dir)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    source_dir = Path(args.source_dir).expanduser().resolve()
    target_dir = resolve_target_dir(args.target_dir)

    total_files, total_with_date = resolve_files(source_dir, target_dir)

    print("Organizando documentos de pagamento...")
    print(f"Diretório de origem: {source_dir}")
    print(f"Diretório de destino: {target_dir}")
    print()
    print(f"Total de arquivos: {total_files}")
    print(f"Arquivos com data: {total_with_date}")
    print(f"Arquivos ignorados: {total_files - total_with_date}")
    print()
    print("Documentos de pagamento organizados com sucesso.")


if __name__ == "__main__":
    main()
