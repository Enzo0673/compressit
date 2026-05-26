# CompressIt

**Outils fichiers gratuits, 100% locaux — images, PDF, vidéos, archives.**

CompressIt est une application web qui tourne sur votre propre machine. Vos fichiers ne quittent jamais votre ordinateur : aucun serveur externe, aucun tracking, aucune publicité.

---

## Outils disponibles

### PDF (11 outils)
| Outil | Description |
|---|---|
| Compresser PDF | Réduire le poids d'un PDF |
| Fusionner PDF | Combiner plusieurs PDF en un seul |
| Diviser PDF | Extraire des pages ou découper un PDF |
| PDF → JPG | Convertir chaque page en image JPG |
| JPG → PDF | Assembler des images en PDF |
| Rotation PDF | Faire pivoter des pages |
| Filigrane PDF | Ajouter un texte en filigrane |
| Numéroter pages | Ajouter des numéros de page |
| Supprimer pages | Retirer des pages d'un PDF |
| Déverrouiller PDF | Supprimer la protection par mot de passe |
| Protéger PDF | Ajouter un mot de passe |

### Images (5 outils)
| Outil | Description |
|---|---|
| Compresser image | Réduire le poids — JPEG, PNG, WebP, GIF, BMP, TIFF |
| Redimensionner | Changer les dimensions |
| Convertir format | Passer d'un format à un autre |
| Recadrer | Rogner une image |
| Rotation / Flip | Faire pivoter ou retourner |

### Vidéo
- **Compresser vidéo** — MP4, MOV, AVI, MKV, WebM (codecs H.264 / H.265 / VP9)

### Archives
- **Compresser archive** — ZIP, 7z, RAR, TAR, GZ, BZ2, ZST (algorithmes zstd, lzma, gzip, brotli)

---

## Pourquoi CompressIt ?

Les outils en ligne comme iLovePDF ou Smallpdf envoient vos fichiers sur leurs serveurs. CompressIt tourne entièrement sur votre machine :

- **100% local** — vos fichiers ne transitent jamais par internet
- **Aucune collecte** — pas de cookies, pas d'analytics, pas de compte requis
- **Open source** — le code est auditable
- **PWA** — installable comme une app, fonctionne hors-ligne

---

## Installation

### Prérequis

- Python 3.10+
- FFmpeg installé et accessible dans le PATH (pour la compression vidéo)
- Poppler (pour PDF → JPG) : `apt install poppler-utils` / `brew install poppler` / [Windows binaries](https://github.com/oschwartz10612/poppler-windows/releases)

### Démarrage rapide

```bash
git clone https://github.com/Enzo0673/compressit.git
cd compressit
pip install -r requirements.txt
py main.py        # Windows
python main.py    # Linux / Mac
```

L'application s'ouvre automatiquement sur `http://localhost:8000`.

---

## Stack technique

| Composant | Technologie |
|---|---|
| Backend | Python 3, FastAPI, Uvicorn |
| Images | Pillow |
| PDF | pikepdf, pdf2image |
| Vidéo | ffmpeg-python + FFmpeg |
| Archives | zstandard, brotli, lzma, gzip |
| Frontend | HTML / CSS / JavaScript vanilla |
| Aperçu PDF | pdf.js (servi en local) |
| PWA | Service Worker + manifest.json |

---

## Sécurité

- CORS restreint à `localhost`
- Validation des paramètres côté serveur (whitelists codec, DPI, qualité…)
- Protection path traversal sur les téléchargements
- Protection zip bomb sur les archives (ratio, taille décompressée)
- Fichiers temporaires supprimés automatiquement après 1 heure
- Aucune stack trace exposée au client

---

## Licence

MIT
