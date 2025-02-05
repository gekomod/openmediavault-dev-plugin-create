# create_binary_debian.py
import os
import re
import subprocess
import sys
from pathlib import Path

def check_and_install_debhelper():
    """Sprawdza, czy debhelper jest zainstalowany, i instaluje go, jeśli nie."""
    try:
        subprocess.run(["dpkg-query", "-L", "debhelper"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("debhelper jest już zainstalowany.")
    except subprocess.CalledProcessError:
        print("debhelper nie jest zainstalowany. Próba instalacji...")
        try:
            subprocess.run(["sudo", "apt-get", "install", "-y", "debhelper"], check=True)
            print("debhelper został pomyślnie zainstalowany.")
        except subprocess.CalledProcessError as e:
            print(f"Błąd podczas instalacji debhelper: {e}")
            sys.exit(1)

def get_package_version(changelog_path: str) -> str:
    """Pobiera wersję pakietu z pliku debian/changelog."""
    try:
        with open(changelog_path, 'r') as f:
            first_line = f.readline().strip()
            match = re.match(r"^.* \((.*?)\)", first_line)
            print(f"Znaleziona Wersja: {match.group(1)}")
            if match:
                return match.group(1)
    except FileNotFoundError:
        print(f"Błąd: Plik {changelog_path} nie istnieje!")
    return None

def build_deb_package(source_dir: str, output_dir: str):
    """Check Debian Package Installed"""
    check_and_install_debhelper()
    """Buduje pakiet DEB z danego katalogu."""
    # Ścieżki
    source_dir = Path(source_dir).absolute()
    output_dir = Path(output_dir).absolute()
    changelog_path = os.path.join(source_dir, "debian", "changelog")

    version = get_package_version(changelog_path)
    if not version:
        print("Nie udało się pobrać wersji pakietu. Zakończono.")
        sys.exit(1)
    
    package_name = source_dir.name  # Nazwa katalogu źródłowego

    # Utwórz katalog wyjściowy
    output_dir.mkdir(parents=True, exist_ok=True)

    # Budowanie pakietu DEB
    deb_filename = f"{package_name}_{version}_all.deb"
    deb_path = output_dir / deb_filename

    print(f"Budowanie pakietu {deb_filename}...")

    try:
        # Użyj fakeroot do budowania pakietu
        subprocess.run(
            ["fakeroot", "dpkg-buildpackage", "-b", "-uc", "-us"],
            cwd=source_dir,
            check=True
        )

        # Przenieś plik DEB do katalogu wyjściowego
        built_deb = source_dir.parent / f"{package_name}_{version}_all.deb"
        if built_deb.exists():
            built_deb.rename(deb_path)
            print(f"Pakiet DEB został utworzony: {deb_path}")
        else:
            raise FileNotFoundError(f"Nie znaleziono wygenerowanego pliku DEB: {built_deb}")

    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas budowania pakietu: {e}")
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    # Konfiguracja
    source_directory = input("Podaj ścieżkę do katalogu źródłowego: ").strip()
    output_directory = input("Podaj ścieżkę do katalogu wyjściowego: ").strip()

    # Budowanie pakietu
    build_deb_package(source_directory, output_directory)