#!/usr/bin/env python3
"""
================================================================================
Entrust Identity Verification SDK — Artifact Downloader
================================================================================

PURPOSE
-------
This script downloads the Entrust IDV SDK artifacts and their transitive
Entrust dependencies from Maven Central, then packages them into a zip
archive that is structured as a standard Maven 2 repository.

It is aimed at enterprise integrators — such as financial institutions — whose
security policy requires all third-party libraries to pass an internal vetting
process and be served from an internal repository (e.g., Sonatype Nexus, JFrog
Artifactory) rather than fetched directly from the public internet at build time.

REQUIREMENTS
------------
- Python 3.9 or later (standard library only — no pip install needed)
- Internet access to https://repo1.maven.org at the time you run this script

USAGE
-----
Run from the same directory as this script (where libs.versions.toml lives):

    python3 download-sdk-artifacts.py

The SDK version is read automatically from libs.versions.toml. All options:

    # Use a specific SDK version instead of the one in libs.versions.toml:
    python3 download-sdk-artifacts.py --version 100.2.0

    # Write the output zip to a different directory (default: current directory):
    python3 download-sdk-artifacts.py --output ~/Downloads

    # Also keep the unzipped repository directory (skips having to unzip later):
    python3 download-sdk-artifacts.py --keep-dir

OUTPUT
------
A zip archive named  entrust-idv-sdk-<version>.zip  is created in the output
directory. Inside, the contents follow the standard Maven 2 repository layout:

    entrust-idv-sdk-100.2.0/
      com/entrust/identity/verification/sdk/
        core/100.2.0/
          core-100.2.0.aar
          core-100.2.0.pom
          core-100.2.0.module
        welcome/100.2.0/
          welcome-100.2.0.aar
          welcome-100.2.0.pom
          welcome-100.2.0.module
        ... (17 artifacts total)

Each artifact folder contains:
  .aar  — Android library (or .jar for pure-JVM libraries such as analytics-events)
  .pom  — Maven POM descriptor
  .module — Gradle module metadata (present for most artifacts)

ARTIFACTS INCLUDED
------------------
The following are the 6 primary artifacts declared in libs.versions.toml, plus
11 Entrust transitive dependencies resolved automatically from POM files:

  Primary (SDK version):
    core, welcome, face.motion, face.photo, document, nfc

  Transitive (versions determined by each primary artifact's POM):
    shared, shared.compose, common.screens, ui.components, camera,
    security, translations, api, contract, analytics-events, translation-keys

Third-party dependencies (AndroidX, Kotlin stdlib, Retrofit, etc.) are NOT
included — they are expected to already be available in your build environment.

================================================================================
OPTION A — USE AS A LOCAL DIRECTORY REPOSITORY (simplest)
================================================================================
If your build machines can access a shared network path (or if you are working
locally), you can point Gradle directly at the unzipped directory without
uploading anything to a remote server.

Step 1 — Run this script with --keep-dir:

    python3 download-sdk-artifacts.py --output /path/to/shared/libs --keep-dir

    This creates:
      /path/to/shared/libs/entrust-idv-sdk-100.2.0/   ← the repository directory
      /path/to/shared/libs/entrust-idv-sdk-100.2.0.zip

Step 2 — Add the repository directory to settings.gradle.kts:

    dependencyResolutionManagement {
        repositories {
            google()
            mavenCentral()

            // Entrust IDV SDK — served from local/shared directory
            maven {
                url = uri("/path/to/shared/libs/entrust-idv-sdk-100.2.0")
            }
        }
    }

    Use a relative path if the directory is checked into your project:

            maven {
                url = uri(rootDir.resolve("libs/entrust-idv-sdk-100.2.0"))
            }

Step 3 — No changes to build.gradle.kts or libs.versions.toml are required.
         Gradle will find the Entrust artifacts in the local repository and
         everything else (AndroidX, Kotlin, etc.) in Google/Maven Central as usual.

================================================================================
OPTION B — UPLOAD TO SONATYPE NEXUS
================================================================================
Step 1 — Run this script and transfer the zip to a machine with Nexus access:

    python3 download-sdk-artifacts.py --output ~/Downloads

Step 2 — Unzip:

    cd ~/Downloads
    unzip entrust-idv-sdk-100.2.0.zip

Step 3 — Upload the entire repository tree using the Nexus REST API:

    NEXUS_URL="https://nexus.your-company.com"
    NEXUS_REPO="your-internal-releases"
    REPO_DIR="entrust-idv-sdk-100.2.0"

    find "$REPO_DIR" -type f | while read FILE; do
        REL_PATH="${FILE#$REPO_DIR/}"
        curl -s -u "admin:your-password" \\
            --upload-file "$FILE" \\
            "$NEXUS_URL/repository/$NEXUS_REPO/$REL_PATH"
        echo "Uploaded: $REL_PATH"
    done

    Alternatively, use the Nexus UI: Repositories → your repo → Upload Component.

Step 4 — Update settings.gradle.kts to point at your Nexus instance:

    dependencyResolutionManagement {
        repositories {
            google()

            // Entrust IDV SDK — served from internal Nexus
            maven {
                url = uri("https://nexus.your-company.com/repository/your-internal-releases/")
                credentials {
                    username = providers.gradleProperty("nexusUsername").orNull
                    password = providers.gradleProperty("nexusPassword").orNull
                }
            }

            mavenCentral()  // still needed for AndroidX and other third-party deps
        }
    }

    Add credentials to gradle.properties (never commit this file to source control):

        nexusUsername=your-user
        nexusPassword=your-password

================================================================================
OPTION C — UPLOAD TO JFROG ARTIFACTORY
================================================================================
Step 1–2: same as Nexus (run script, unzip).

Step 3 — Upload using the Artifactory REST API:

    ARTIFACTORY_URL="https://artifactory.your-company.com/artifactory"
    REPO="your-internal-releases"
    REPO_DIR="entrust-idv-sdk-100.2.0"

    find "$REPO_DIR" -type f | while read FILE; do
        REL_PATH="${FILE#$REPO_DIR/}"
        curl -s -H "X-JFrog-Art-Api: your-api-key" \\
            -T "$FILE" \\
            "$ARTIFACTORY_URL/$REPO/$REL_PATH"
        echo "Uploaded: $REL_PATH"
    done

Step 4 — Update settings.gradle.kts:

    dependencyResolutionManagement {
        repositories {
            google()

            maven {
                url = uri("https://artifactory.your-company.com/artifactory/your-internal-releases/")
                credentials {
                    username = providers.gradleProperty("artifactoryUsername").orNull
                    password = providers.gradleProperty("artifactoryPassword").orNull
                }
            }

            mavenCentral()
        }
    }

================================================================================
"""

import argparse
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAVEN_CENTRAL = "https://repo1.maven.org/maven2"
ENTRUST_GROUP = "com.entrust.identity.verification.sdk"
ENTRUST_GROUP_PATH = ENTRUST_GROUP.replace(".", "/")

# Top-level artifacts requested by this integration sample.
# These match the [libraries] entries in libs.versions.toml.
INITIAL_ARTIFACTS = [
    "core",
    "welcome",
    "face.motion",
    "face.photo",
    "document",
    "nfc",
]

# Dependency scopes that should NOT be pulled into the transitive closure
EXCLUDED_SCOPES = {"test", "provided", "optional"}

# libs.versions.toml lives next to this script in the integration-sample directory
TOML_FILENAME = "libs.versions.toml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def artifact_base_url(artifact_id: str, version: str) -> str:
    return f"{MAVEN_CENTRAL}/{ENTRUST_GROUP_PATH}/{artifact_id}/{version}"


def local_dir(repo_root: str, artifact_id: str, version: str) -> str:
    return os.path.join(repo_root, ENTRUST_GROUP_PATH, artifact_id, version)


def download_file(url: str, dest: str) -> bool:
    """Download *url* to *dest*, creating parent directories as needed.
    Returns True on success, False on 404."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        with urllib.request.urlopen(url) as resp:
            with open(dest, "wb") as fh:
                fh.write(resp.read())
        return True
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise


def download_with_signature(base_url: str, filename: str, dest_dir: str) -> bool:
    """Download *filename* and its PGP signature (*filename*.asc) into *dest_dir*.
    Returns True if the main file was downloaded successfully."""
    url = f"{base_url}/{filename}"
    dest = os.path.join(dest_dir, filename)
    ok = download_file(url, dest)
    if ok:
        # Always download the .asc signature sidecar alongside the main file
        download_file(f"{url}.asc", f"{dest}.asc")  # silently skipped on 404
    return ok


def detect_extension(artifact_id: str, version: str) -> str | None:
    """Return 'aar' or 'jar' depending on which file exists on Maven Central."""
    base = artifact_base_url(artifact_id, version)
    for ext in ("aar", "jar"):
        url = f"{base}/{artifact_id}-{version}.{ext}"
        try:
            req = urllib.request.Request(url, method="HEAD")
            urllib.request.urlopen(req)
            return ext
        except (urllib.error.HTTPError, urllib.error.URLError):
            continue
    return None


def parse_entrust_deps(pom_path: str) -> list[tuple[str, str]]:
    """Return [(artifactId, version)] for all compile/runtime Entrust deps in *pom_path*."""
    tree = ET.parse(pom_path)
    root = tree.getroot()
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}

    deps: list[tuple[str, str]] = []
    for dep in root.findall(".//m:dependency", ns):
        group_el = dep.find("m:groupId", ns)
        artifact_el = dep.find("m:artifactId", ns)
        version_el = dep.find("m:version", ns)
        scope_el = dep.find("m:scope", ns)

        if group_el is None or group_el.text != ENTRUST_GROUP:
            continue
        if artifact_el is None or version_el is None:
            continue
        scope = scope_el.text if scope_el is not None else "compile"
        if scope in EXCLUDED_SCOPES:
            continue

        deps.append((artifact_el.text.strip(), version_el.text.strip()))

    return deps


def read_version_from_toml(toml_path: str) -> str | None:
    """Extract the `entrust-idv` version from a TOML version catalog."""
    with open(toml_path) as fh:
        content = fh.read()
    match = re.search(r'entrust-idv\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# Core download logic
# ---------------------------------------------------------------------------

def download_artifact(
    artifact_id: str,
    version: str,
    repo_root: str,
    downloaded: set,
    depth: int = 0,
) -> None:
    """Download an artifact and recurse into its Entrust transitive dependencies."""
    key = f"{artifact_id}:{version}"
    if key in downloaded:
        return
    downloaded.add(key)

    indent = "  " * depth
    print(f"{indent}→ {ENTRUST_GROUP}:{artifact_id}:{version}")

    dest_dir = local_dir(repo_root, artifact_id, version)
    base_url = artifact_base_url(artifact_id, version)

    # --- POM + signature (required for dependency resolution) ---
    pom_filename = f"{artifact_id}-{version}.pom"
    pom_dest = os.path.join(dest_dir, pom_filename)

    if not download_with_signature(base_url, pom_filename, dest_dir):
        print(f"{indent}  WARNING: POM not found at {base_url}/{pom_filename}")
        return

    # --- Main artifact (AAR / JAR) + signature ---
    ext = detect_extension(artifact_id, version)
    if ext:
        art_filename = f"{artifact_id}-{version}.{ext}"
        if download_with_signature(base_url, art_filename, dest_dir):
            print(f"{indent}  ✓ {art_filename}")
        else:
            print(f"{indent}  WARNING: artifact file not found: {base_url}/{art_filename}")
    else:
        print(f"{indent}  WARNING: no AAR or JAR found for {artifact_id}:{version}")

    # --- Gradle module metadata + signature ---
    module_filename = f"{artifact_id}-{version}.module"
    download_with_signature(base_url, module_filename, dest_dir)  # silently skipped on 404

    # --- Recurse into Entrust transitive dependencies ---
    for dep_id, dep_version in parse_entrust_deps(pom_dest):
        if dep_id != artifact_id:
            download_artifact(dep_id, dep_version, repo_root, downloaded, depth + 1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Download Entrust IDV SDK artifacts from Maven Central and package "
            "them as a local Maven repository zip archive."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "See the top of this script for full documentation:\n"
            "  Option A — use as a local directory repository (simplest)\n"
            "  Option B — upload to Sonatype Nexus\n"
            "  Option C — upload to JFrog Artifactory"
        ),
    )
    parser.add_argument(
        "--version",
        help=(
            "SDK version to download (e.g. 100.2.0). "
            "If omitted, the version is read from libs.versions.toml in the same directory."
        ),
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Directory where the zip archive is written (default: current directory).",
    )
    parser.add_argument(
        "--keep-dir",
        action="store_true",
        help="Keep the expanded repository directory alongside the zip archive.",
    )
    args = parser.parse_args()

    # Resolve SDK version — prefer explicit arg, fall back to libs.versions.toml
    version = args.version
    if not version:
        # libs.versions.toml lives in the same directory as this script
        toml_path = Path(__file__).resolve().parent / TOML_FILENAME
        if toml_path.exists():
            version = read_version_from_toml(str(toml_path))
            if version:
                print(f"Using SDK version {version!r} from {toml_path.name}")

    if not version:
        print(
            "ERROR: Could not determine the SDK version.\n"
            f"Ensure {TOML_FILENAME} is present next to this script, "
            "or pass --version explicitly.",
            file=sys.stderr,
        )
        sys.exit(1)

    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    archive_name = f"entrust-idv-sdk-{version}"
    repo_root = os.path.join(output_dir, archive_name)

    print(f"\nDownloading Entrust IDV SDK {version} artifacts from Maven Central…\n")

    downloaded: set[str] = set()
    for artifact_id in INITIAL_ARTIFACTS:
        download_artifact(artifact_id, version, repo_root, downloaded)

    # Create zip archive
    zip_path = os.path.join(output_dir, f"{archive_name}.zip")
    print(f"\nCreating archive: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for dirpath, _dirnames, filenames in os.walk(repo_root):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                arcname = os.path.relpath(file_path, output_dir)
                zf.write(file_path, arcname)

    if not args.keep_dir:
        shutil.rmtree(repo_root)

    zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)

    print(
        f"\n{'=' * 72}\n"
        f"Done! {len(downloaded)} artifact(s) packaged into:\n"
        f"  {zip_path}  ({zip_size_mb:.1f} MB)\n"
        f"{'=' * 72}\n"
        "Next steps — choose one:\n\n"
        "  A) LOCAL DIRECTORY REPO (simplest — no server needed)\n"
        f"     Unzip: unzip {archive_name}.zip\n"
        "     Then add to settings.gradle.kts:\n"
        "       maven {\n"
        f'         url = uri("/absolute/path/to/{archive_name}")\n'
        "       }\n\n"
        "  B) UPLOAD TO NEXUS / ARTIFACTORY\n"
        f"     Transfer {archive_name}.zip to your server, unzip, then upload.\n"
        "     See the top of this script for upload commands.\n"
    )


if __name__ == "__main__":
    main()
