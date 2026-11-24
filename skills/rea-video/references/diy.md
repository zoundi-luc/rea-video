# Faites-le vous-même

L'utilisateur filme et monte lui-même, ou génère manuellement sur d'autres plateformes (Jiemeng, Keling, etc.), en suivant le plan de tournage et le storyboard du rapport. Vous assemblez ensuite les rushes sur la timeline originale.

## Coût

- `rea-video` est gratuit.
- La génération manuelle sur d'autres plateformes est facturée par ces plateformes ; le matériel et le lieu de tournage sont à la charge de l'utilisateur.

## Quand l'utilisateur le fait lui-même : aidez-le à se connecter

1. Donnez d'abord les étapes de la deuxième partie du rapport « Suivez les instructions » (voir `remake.md` « Suivez les instructions ») et la liste des rushes à préparer (quoi filmer, la durée de chaque segment, où trouver les prompts pour les unités de génération).
2. Une fois que l'utilisateur a filmé ou généré, il vous envoie simplement les chemins des fichiers, et vous vous occupez du reste : faire correspondre les plans, écrire `mine.json`, exécuter `rea-video remake`, montrer `remake/compare.mp4` à l'utilisateur, et lui indiquer les plans et sons restants à faire selon `remake/status.md`.

## Réassembler sur la timeline originale

1. Faites correspondre les rushes aux plans selon le storyboard (numéro de plan et durée dans `report.md`). Si un rush long couvre plusieurs plans, utilisez d'abord ffmpeg pour le découper par action ; si vous n'êtes pas sûr de la correspondance, montrez des captures d'écran à l'utilisateur pour confirmation.
2. Écrivez dans `out/ref/remake/mine.json` : `{"results": {"<numéro de plan>": {"video": "<chemin absolu du rush>"}, ...}}`. Si une vidéo d'« unité de génération » générée manuellement couvre plusieurs plans, écrivez : `{"G2": {"unit": "G2", "shots": [4, 5, 6], "video": "<chemin>", "trim_to": <secondes de l'unité>}}`. `remake` la découpera en plans individuels selon les points de coupe du film original.
3. `rea-video remake out/ref` : chaque rush est inséré dans la durée du plan original en faisant correspondre le rythme de l'action au plan original (début/fin de l'action, points culminants alignés sur le temps du film original ; maximum 3x plus rapide, 1.25x plus lent, le surplus est coupé ; les rushes sans action sont accélérés/ralentis uniformément sur toute la durée), les points de coupe sont alignés sur les numéros de trame du film original et ne dériveront pas, les plans non remplis sont temporairement remplacés par le film original, et le son du film original est conservé ; la sortie est `remake/remake.mp4`, `remake/compare.mp4` pour la comparaison côte à côte, et `remake/status.md`. Informez l'utilisateur des plans qui sont encore des remplacements du film original et des sons qui doivent être remplacés. Si vous voulez seulement assembler sans redessiner les plans de code, utilisez `rea-video assemble out/ref/breakdown.json <chemin de results.json>`.
   - Superposition des sous-titres (`remake` les superpose par défaut, `assemble` nécessite `--overlays`) : les sous-titres / textes stylisés / titres détectés sont superposés sur les plans remplacés dans leur style original (les plans remplacés par le film original ont déjà du texte et ne sont pas superposés à nouveau). La police est une police sans empattement générique, la couleur et le cadre sont des valeurs mesurées et peuvent différer du film original ; les stickers ne sont listés que dans `stickers_to_add` de `assemble_log.json`, vous devez trouver les rushes et les coller vous-même.
