# Installation et configuration du VLM

## Installation (une seule fois)

```bash
pip install "rea-video[ocr] @ git+https://github.com/JuneYaooo/rea-video"   # Nécessite ffmpeg ; Python ≥ 3.10
# Ou dans le dépôt : bash scripts/install_skill.sh (installe la CLI et lie la skill aux répertoires des agents)
rea-video --help
```

**Windows** ( `install_skill.sh` est un script bash, suivez ces étapes manuellement si Git Bash n'est pas installé) :

```powershell
winget install Gyan.FFmpeg     # Ou choco install ffmpeg ; ouvrez un nouveau terminal après l'installation
git clone https://github.com/JuneYaooo/rea-video; cd rea-video
pip install ".[ocr]"
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
New-Item -ItemType Junction -Path "$HOME\.claude\skills\rea-video" -Target "$PWD\skills\rea-video"
```

Sous Windows, `pip` utilise le premier Python dans le PATH : sur une machine avec Python 3.8 et 3.12 installés, si l'interpréteur par défaut est inférieur à 3.10, cette étape échouera avec `requires a different Python: 3.8.10 not in '>=3.10'`. Vérifiez d'abord les versions disponibles avec `py -0p`, puis utilisez `py -3.12 -m pip install ".[ocr]"`. Si la commande `rea-video` n'est pas trouvée après l'installation, exécutez-la avec `py -3.12 -m rea_video`.

`Junction` ne nécessite pas de droits d'administrateur (contrairement à `SymbolicLink`) ; les chemins de dépôt contenant des caractères chinois ou des espaces n'ont pas besoin d'être traités spécialement. `rea-video pdf` utilisera Chrome / Edge de `Program Files` ou `%LOCALAPPDATA%` ; si installé ailleurs, définissez `REA_CHROME`.

Si pip signale `externally-managed-environment` (Homebrew / Python système des nouvelles versions d'Ubuntu), n'ajoutez pas `--break-system-packages`, utilisez plutôt
`pipx install "rea-video[ocr] @ git+https://github.com/JuneYaooo/rea-video"`, ou exécutez directement `install_skill.sh` (qui basculera automatiquement vers pipx ou le `.venv` du dépôt).

Si `onnxruntime` ne trouve pas de paquet d'installation correspondant (par exemple `no wheels with a matching Python ABI tag`), cela signifie que le Python par défaut est trop récent et que les dépendances n'ont pas encore de version correspondante : changez pour un interpréteur Python 3.10–3.14, `pipx install --python python3.12 "rea-video[ocr] @ git+https://github.com/JuneYaooo/rea-video"` ou `PYTHON_BIN=python3.12 bash scripts/install_skill.sh`. `install_skill.sh` priorise déjà Python 3.10–3.14 lors de la sélection automatique de l'interpréteur. Python 3.10–3.14 peuvent tous installer `[ocr]` : 3.12 et inférieurs utilisent `rapidocr-onnxruntime`, à partir de 3.13, il passe automatiquement à `rapidocr` 3.

Si vous avez installé `[ocr]` manuellement avec Python 3.12 ou une version antérieure, les dépendances OCR installeront un ensemble `opencv-python`, qui entrera en conflit avec `opencv-python-headless` utilisé par rea-video pour le même répertoire `cv2`. Après l'installation, exécutez une fois :
`pip uninstall -y opencv-python && pip install --force-reinstall --no-deps "opencv-python-headless>=4.8,<5"` (`install_skill.sh` le fera automatiquement).

## Reconnaissance vocale locale (facultatif)

D'où viennent les dialogues s'il n'y a pas de sous-titres incrustés et qu'aucun VLM capable d'entendre n'est activé ? Installez la reconnaissance vocale facultative :

```bash
pip install "rea-video[ocr,asr] @ git+https://github.com/JuneYaooo/rea-video"   # Si déjà installé, faites pip install sherpa-onnx
```

Une fois installé, `decompose` effectuera automatiquement la reconnaissance sur les pistes vocales isolées (SenseVoice, chinois / anglais / japonais / coréen / cantonais ; la première utilisation télécharge un modèle d'environ 160 Mo vers `$REA_VIDEO_MODELS`, par défaut `~/.cache/rea-video/models`),
cela prend quelques secondes pour une vidéo d'une minute. Les résultats se trouvent dans `breakdown.json` sous `speech.lines` (chaque phrase a des heures de début et de fin), le tableau "script" du rapport et le champ `said` de chaque plan dans `review_tasks.json` l'utiliseront. `--no-asr` permet de l'ignorer.
Si les dialogues sont en bengali, ajoutez `--asr-lang bn` (ou `rea-video prefs asr_lang bn` pour le définir par défaut) : SenseVoice ne reconnaît pas le bengali et le transcrira comme du charabia en anglais / japonais / coréen ;
`bn` utilise un modèle de reconnaissance en continu pour le bengali (téléchargement supplémentaire d'environ 90 Mo), `speech.language` sera `bn`, et les phrases reconnues n'auront pas de ponctuation.
Le même paquet facultatif séparera également les locuteurs (téléchargement supplémentaire d'environ 35 Mo) : pour les dialogues à plusieurs, les dialogues incluront qui a parlé, et une piste audio sera générée pour chaque personne, voir `audio.md`.

Il s'agit d'une transcription automatique, il peut y avoir des homophones incorrects et des noms propres mal transcrits : si des sous-titres sont présents à l'écran, ils priment ; si le VLM a fourni les dialogues, le rapport utilisera ceux du VLM ; lors de la citation des dialogues à l'utilisateur, indiquez "reconnaissance vocale, non révisée".
Les temps phrase par phrase dans les phrases longues sont estimés par le nombre de mots (`timing: estimated`), les débuts et fins de sections entières sont mesurés. Si non installé, `speech.reason` sera `not_installed`, le reste fonctionnera normalement.

## Configuration VLM (recommandée, non obligatoire)

**VLM (configuration recommandée, non obligatoire)** : Un VLM est un grand modèle multimodal capable de visualiser des images/vidéos (Gemini, GPT-4o, Doubao, Qwen-VL, etc.). Sans VLM, l'outil se base uniquement sur les statistiques de pixels, le taux de rafraîchissement, l'OCR et les métadonnées pour fonctionner et générer des rapports, mais la **distinction entre tournage réel / IA / 3D est nettement affaiblie**, et la liste des effets sonores ne contient que des candidats à faible confiance au niveau du signal. Avec un VLM, l'outil envoie de courts extraits vidéo et des images clés de chaque plan au VLM, puis fusionne les résultats avec les résultats déterministes.

Deux configurations :

- Gemini : Définissez `GEMINI_API_KEY` (le modèle peut être modifié avec `REA_GEMINI_MODEL`), utilisez l'API officielle de Gemini pour visualiser les extraits vidéo avec le son ; les vidéos seront téléchargées sur Google et supprimées après utilisation.
- Autres modèles multimodaux : Définissez `REA_VLM_BASE_URL` / `REA_VLM_API_KEY` / `REA_VLM_MODEL` (vous pouvez spécifier plusieurs modèles séparés par des virgules, le suivant est utilisé si le précédent échoue). Si cet ensemble est défini, il est prioritaire.

Utilisez `--env-file <un fichier .env>` pour lire la configuration. **Ne mettez pas les clés secrètes dans les dialogues, les dépôts ou les rapports, et n'ouvrez pas le fichier .env pour en voir le contenu.**

Si l'utilisateur n'a pas configuré de VLM : exécutez normalement sans `--vlm`, ne mettez pas fin à la tâche pour cette raison.

- **Vous pouvez visualiser les images (agent multimodal)** : Vous êtes le "VLM" pour cette fois, il n'est pas nécessaire de suggérer à l'utilisateur d'en configurer un autre. Suivez la section 1 de SKILL.md "Révision visuelle intégrée" : `rea-video review` → examinez chaque plan et remplissez les réponses → `rea-video apply-review`, votre jugement sera intégré aux conclusions de l'outil et au rapport. Dans les conclusions, écrivez "VLM non activé, révision visuelle effectuée par l'agent".
- **Vous ne pouvez pas visualiser les images** : Respectez les "Règles en cas d'impossibilité de visualiser les images" de `review.md`, et à la fin de votre réponse, suggérez en une phrase de configurer un VLM (en expliquant que cela peut améliorer la distinction entre tournage réel/IA/3D et la reconnaissance des effets sonores).
- Tests réels (dépôt eval/RESULTS.md) : la révision visuelle intégrée par l'agent est plus précise que l'utilisation d'un VLM Gemini seul ; Gemini a tendance à juger les vidéos IA de style dessin animé 3D comme des rendus 3D, et les interfaces de jeu incrustées dans l'image comme des captures d'écran. Par conséquent, si vous pouvez visualiser les images, **vous devez effectuer une révision visuelle**, même si un VLM est activé, et juger de manière indépendante, sans copier le VLM.
- Le VLM externe a toujours des parties que vous ne pouvez pas remplacer : il peut directement visualiser le mouvement des extraits vidéo et écouter les pistes audio. Si vous ne pouvez voir que des images fixes et ne pouvez pas entendre le son, les effets sonores et les sources vocales seront toujours marqués "à confirmer".

**Pour savoir si le VLM est réellement actif, référez-vous à la ligne `VLM:` de `rea-video summary`** (également dans `breakdown.json` sous `analysis.vlm.status`) : `ok` est actif, `partial` certains plans ont des résultats, `failed` a été demandé mais tous les appels ont échoué (par exemple, serveur 503), `not_configured` a été demandé mais aucune configuration n'a été trouvée, `off` n'a pas été demandé. `failed` / `not_configured` équivaut à un VLM non activé, le rapport doit le mentionner honnêtement et ne pas écrire "VLM activé". Si le nombre de plans est élevé, cette ligne indiquera "seulement a/n plans envoyés" : par défaut, un maximum de 60 appels, les plans non envoyés ne dépendent que de preuves déterministes. Pour tout visualiser, relancez avec `--max-vlm-shots N`, ou effectuez une révision visuelle pour ces plans.
