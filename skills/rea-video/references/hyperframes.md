# HyperFrames

[HyperFrames](https://github.com/heygen-com/hyperframes) est un framework vidéo HTML open source : un assistant de programmation IA écrit des animations HTML/CSS, qui sont ensuite rendues en MP4. Les plans de type rendu par code, animation graphique (MG) et animation d'illustration sont créés de cette manière. Le fait de les reproduire en un projet modifiable avec HyperFrames est plus proche du matériel original que les ébauches `code-remake` intégrées à rea-video.

## Coût

- Le framework est open source et gratuit (Apache-2.0), avec un rendu local.
- Son application Studio propose des forfaits payants (intégrant les modèles de génération de HeyGen), mais ils ne sont pas nécessaires pour reproduire uniquement des plans de type code.

## Comment l'installer

Nécessite Node.js 22 ou supérieur. Dans Claude Code :

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

Pour les autres assistants de programmation (Codex, Cursor, etc.), exécutez une fois `npx hyperframes skills update`. Une fois installé, suivez ses compétences pour que l'assistant écrive la vidéo.

## Que lui donner

Fournissez ces éléments à l'assistant qui écrit le projet HyperFrames, en lui indiquant : « Reproduisez ceci en respectant le rythme et les visuels, sans utiliser les pixels du matériel original » :

1. `video/rhythm.md` : le temps de chaque coupe et transition, le type et la durée de la transition, les images clés de chaque plan (temps + type : début/fin d'action, tournant, entrée/sortie d'éléments, changement de composition...). Le @nombre après chaque temps est le numéro de trame du matériel original, à classer par numéro de trame (HyperFrames utilise la même fréquence d'images), et non par secondes arrondies ; les images clés de l'animation sont classées ici, le reste étant géré par l'interpolation.
2. Les images clés de chaque plan `shots/shot_XXX.jpg`, et la section « Synthèse de code » du rapport : mise en page, palette de couleurs (valeurs de couleur), quels sont les éléments et comment ils apparaissent.
3. Le son : `stems/music.wav` comme musique de fond, ou remplacez-la par une autre selon le BPM et l'ambiance de `video/sound.md` ; les points temporels des effets sonores se trouvent dans `video/sound.md`.
4. Les sous-titres et le texte stylisé : `packaging/timeline.json` (temps, position, style).

Si vous souhaitez reproduire seulement quelques plans, précisez les numéros de plan et les plages horaires ; les autres plans peuvent être des placeholders du matériel original, et les segments réalisés peuvent être écrits dans `remake/mine.json`, puis réassemblés sur la timeline originale avec `rea-video remake out/ref` (voir `diy.md`).
