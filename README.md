# CompressIt

Application bureau locale pour compresser vos fichiers — images, vidéos, PDF et archives — sans que vos données ne quittent votre ordinateur.

## Pourquoi CompressIt ?

La plupart des outils de compression en ligne envoient vos fichiers sur des serveurs externes. CompressIt fonctionne **100% en local** : vos fichiers ne quittent jamais votre machine.

## Fonctionnalités

- **Images** — JPEG, PNG, WebP, GIF, BMP, TIFF
- **Vidéos** — MP4, MOV, AVI, MKV, WebM
- **PDF** — compression avec options avancées (DPI, suppression des métadonnées)
- **Archives** — ZIP, 7z, RAR, GZ, TAR, BZ2, ZST

### Niveaux de compression

Trois modes disponibles selon vos besoins :
- `light` — compression légère, qualité maximale
- `standard` — bon équilibre taille/qualité
- `aggressive` — compression maximale

### Options avancées (mode expert)

- **Image** : qualité personnalisée, format de sortie, largeur maximale
- **Vidéo** : codec (H.264 / H.265 / VP9), preset, résolution maximale, CRF
- **PDF** : DPI des images internes, suppression des métadonnées
- **Archive** : algorithme (zstd, lzma, gzip, brotli), niveau de compression

## Stack technique

- **Backend** : Python, FastAPI, Uvicorn
- **Interface** : HTML / CSS / JavaScript
- **Distribution** : exécutable Windows (.exe) via PyInstaller
- **Dépendances vidéo** : FFmpeg (embarqué)

## Installation

### Version exécutable (recommandée)

Télécharger le `.exe` depuis les [Releases](../../releases) et le lancer directement — aucune installation requise.

### Version développement

```bash
# Cloner le projet
git clone https://github.com/Enzo0673/compressit.git
cd compressit

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
py main.py
```

L'application s'ouvre automatiquement dans le navigateur sur `http://localhost:8000`.

## Statut

> **En cours de développement** — fonctionnalités à venir : fusion de PDF, redimensionnement d'images, interface améliorée.

## Licence

Projet personnel — tous droits réservés.
