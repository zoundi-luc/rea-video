# capsule-cinema

Flux de génération local open-source : https://github.com/JuneYaooo/capsule-cinema

## Ce que cela peut faire

`rea-video` est responsable de la décomposition et de la reproduction des solutions, tandis que `capsule-cinema` est responsable de la génération, de l'assemblage et de la validation. `rea-video remake` / `remake-run` / `assemble` lui seront transférés.

## Coût

- `capsule-cinema` est gratuit, open-source et déployé localement.
- Les modèles et les clés sont configurés par l'utilisateur, et la facturation se fait par appel de modèle, les frais étant payés à la plateforme du modèle.
- Avant la génération, un `--dry-run` est effectué pour montrer à l'utilisateur le nombre d'appels et les coûts, et l'exécution n'a lieu qu'après l'accord de l'utilisateur.

## Lorsque l'utilisateur souhaite l'utiliser : aidez-le à l'installer et à le connecter

Vous devez aider l'utilisateur à l'installer et à le connecter afin qu'il puisse commencer directement. Avant l'installation, expliquez ce qui sera installé et d'où ; les questions d'argent sont à la discrétion de l'utilisateur. Ne posez plus de questions sur ce qui est déjà connu (vidéo de référence, rapport, ce qui doit être remplacé).

1. Non installé ( `rea-video remake-plan` signale que le dépôt est introuvable) : Lisez https://raw.githubusercontent.com/JuneYaooo/capsule-cinema/main/docs/install.md et suivez les instructions d'installation ; une fois installé, utilisez `rea-video prefs capsule_root <répertoire d'installation>` pour l'enregistrer, et `remake-run` utilisera le Python avec ses dépendances installées (`--python`).
2. Demandez à l'utilisateur de saisir ses clés dans le fichier `.env` du répertoire d'installation. Indiquez-lui uniquement les noms des variables à renseigner, ne lui demandez pas de coller les clés dans la conversation.
3. Suivez SKILL.md « Reproduction » pour interroger le modèle et demander ce qui doit être remplacé, `rea-video plan` générera la solution, puis suivez les étapes ci-dessous pour créer les tâches, effectuer un dry-run, exécuter et réassembler la chronologie originale.

## Comment exécuter

`prepare` appelle `rea-video remake-plan` pour générer les tâches et le fichier de transfert `remake/handoff.json` (chaque unité appelle une tâche à la fois, en utilisant le prompt final dans `remake/prompts.json`) selon la solution de la deuxième partie du rapport ; si la vérification de la solution contient ❌, aucune tâche n'est générée ; `run` génère, `assemble` divise le film original en plans, les réassemble et valide la structure. La solution ne s'adapte pas à l'exécution : les modèles non encore connectés à `capsule-cinema` provoqueront une erreur lors de `remake-run`. Dans ce cas, remettez le prompt et les références dans `remake/refs/` à l'utilisateur pour qu'il les génère sur la plateforme de son propre modèle.

La génération doit utiliser l'environnement Python de `capsule-cinema`. `rea-video remake-run` / `capsule-draft` recherchera automatiquement `$CAPSULE_CINEMA_PYTHON` ou `<capsule-root>/.venv/bin/python`, ou vous pouvez spécifier avec `--python`.

```bash
CC=$CAPSULE_CINEMA_ROOT   # Chemin du dépôt capsule-cinema
cd $CC
python3.12 scripts/remake_reference.py recipes /abs/out/ref                 # Vérifiez d'abord s'il existe des recettes appropriées ; si oui, suivez la recette, sinon suivez le processus générique ci-dessous
python3.12 scripts/remake_reference.py prepare /abs/out/ref                 # Génère les tâches et les fichiers de transfert, sans facturation
python3.12 scripts/remake_reference.py run /abs/out/ref/remake/jobs.json --dry-run   # Montre d'abord les tâches à l'utilisateur ; --only G2 n'exécute qu'une seule unité
python3.12 scripts/remake_reference.py run /abs/out/ref/remake/jobs.json    # Exécute après confirmation de l'utilisateur (facturation)
python3.12 scripts/remake_reference.py assemble /abs/out/ref                # Réassemble la chronologie originale + compare.mp4 + validation de la structure
rea-video capsule-draft out/ref/breakdown.json --capsule-root $CC --capsule-name xxx [--write-capsule]
```

- Valeurs de `executor` pour chaque tâche dans jobs.json :
  - `capsule_cinema` : appelle le modèle pour la génération
  - `local_ffmpeg` : reconstruction locale d'images statiques
  - `keep_original` : conserve le film original, par exemple le rendu de code, l'enregistrement d'écran, le matériel réel
- `user_assets` : ce plan nécessite du matériel réel fourni par l'utilisateur. Le résultat généré n'est qu'une approximation, il faut en informer l'utilisateur.
- `capsule-draft` : injecte les résultats de la décomposition via le `tool_factory` intégré de `capsule-cinema`, sans modifier le code de `capsule-cinema`. Le brouillon de recette généré est par défaut `review_required`.
