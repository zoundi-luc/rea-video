# Règles de révision visuelle

Complément à la section 1 du processus SKILL.md : comment intégrer les résultats de l'analyse visuelle avec l'outil, et les cas où les erreurs de jugement sont fréquentes.

## Règles d'intégration

Déduites des tests réels (répertoire `eval/RESULTS.md`) :

- Lorsqu'il n'y a qu'une seule source d'analyse visuelle (seulement le VLM ou seulement vous), le résultat de l'analyse visuelle ne peut être choisi que parmi les deux premières options de l'outil. L'outil ne sera pas modifié s'il est sûr de "IA / tournage réel / avatar IA" ; un plan avec des images répétées 24→30 après transcodage ne sera pas modifié en tournage réel simplement parce qu'il "semble réel". Si le plan lui-même n'a pas d'images répétées (rythme natif de 30 ips), votre jugement de tournage réel sera accepté, même si le film entier n'a pas été marqué comme natif 30 ips en raison d'un mélange d'IA au début ; si les trois premières options de l'outil sont inférieures à 0,4 et que la catégorie que vous avez choisie n'est que légèrement inférieure à la deuxième meilleure option, votre jugement prévaudra également. Le résultat de l'analyse visuelle est le plus utile pour distinguer entre le rendu 3D / le rendu par code / la capture d'écran. L'animation 2D, l'animation image par image (stop motion) et les extraits de film/série sont des exceptions : l'outil ne peut pas détecter ces trois catégories, et votre jugement sera directement accepté si vous les choisissez, mais la conclusion restera "point à confirmer" si une seule partie a effectué l'analyse visuelle.
- Le VLM et vous avez tous deux répondu : jugez d'abord la catégorie principale (génération / rendu / tournage réel / capture d'écran / image fixe), puis la sous-catégorie. Si la première option de l'outil est soutenue par l'un de vous (même sous-catégorie ou même catégorie principale, par exemple l'outil juge vidéo IA, vous jugez avatar IA), suivez la catégorie principale de la première option de l'outil ; si vous êtes tous deux en désaccord avec l'outil, suivez l'intégration normale.
- Les plans marqués "désaccord" (l'outil et le VLM ont des opinions opposées sur le fait qu'il s'agisse d'un tournage réel) doivent être examinés : vérifiez si les preuves écrites par le VLM sont réellement visibles dans la capture d'écran, car le VLM peut inventer des raisons.
- Les plans où `review_tasks.json` indique "l'utilisateur a modifié X jugé par l'outil en Y n fois par le passé" sont des types que l'utilisateur a corrigés à plusieurs reprises et doivent être examinés attentivement.

## Règles lorsque l'image ne peut pas être vue (important)

Confirmez d'abord si vous pouvez voir l'image (si vous pouvez lire `storyboard.jpg`, `shots/*.jpg` et décrire le contenu de l'image). **Si vous ne pouvez pas voir l'image et que le VLM n'est pas activé :**

- **Ne rejetez pas le jugement de l'outil sur la méthode de production** (tournage réel / IA / 3D / code / capture d'écran). Les statistiques de pixels (nombre de couleurs, blocs plats, bruit) sont des preuves déjà utilisées par l'outil, et les réutiliser ne fera que produire les mêmes conclusions ou de moins bonnes. Test réel : l'agent qui ne pouvait pas voir l'image a jugé un croquis au crayon généré par IA comme une "carte de mise en page sur fond blanc" et des éléments 3D texturés en verre comme une "interface de code".
- Ce que vous pouvez et devez faire : vérifier la chronologie et les points de coupe, lire la piste de texte OCR pour identifier les erreurs de lecture, utiliser les niveaux de `stems/` pour déterminer la présence de voix, lire les métadonnées (identifiants AIGC, marques de transcodage de plateforme), et lister les plans à faible confiance de l'outil dans les "points incertains".
- Indiquez clairement dans la conclusion en une phrase "VLM non activé, image non vue", et conservez les plans marqués par l'outil comme "tournage réel ou IA à confirmer" tels quels.

## Matériel original / de référence : écrivez d'abord les preuves contraires avant de juger l'IA

Pour une vidéo réaliste ou artisanale (animation image par image, vidéo de vie filmée en plongée, scènes miniatures faites à la main) qui ne contient qu'un seul plan continu, sans identifiant AIGC, et sans images répétées 24→30, l'outil la jugera souvent comme de l'IA. Si, après avoir vu l'image, vous ne trouvez pas de défauts clairs de l'IA (déformation, scintillement de texture, erreurs physiques, texte corrompu), **ne donnez pas une confiance élevée** : écrivez "IA ou tournage réel / animation image par image à confirmer (tendance X)", listez les preuves pour et contre, et ne dépassez pas 0,7 de confiance.

## Commentaires de films, montages : déterminez d'abord s'il s'agit d'extraits de films/séries

Lorsque l'image est encadrée de barres noires, l'outil écrira "indice d'extrait de film/série" dans les preuves et marquera le plan comme "vidéo IA ou extrait de film/série à confirmer" ou "tournage réel ou extrait de film/série à confirmer". L'outil ne peut pas déterminer qui a filmé, cette étape nécessite votre analyse visuelle :

- Reconnaissance d'acteurs ou de séries, éclairage et décors à l'échelle d'une équipe de tournage, figurants, logos de chaînes ou filigranes de plateformes, texte de scène clair et lisible → `film_footage`.
- Visages trop parfaits, personnages différents se ressemblant beaucoup, erreurs de mains et de texte, dérive de texture → `ai_video` (le format des commentaires de courts métrages IA est identique à celui des commentaires de séries avec de vrais acteurs, ne vous fiez pas uniquement au format).
- Les prises de parole de l'auteur face caméra, les captures d'écran insérées ou les images IA, sont marquées séparément par plan.
- `live_action` est uniquement pour les images filmées par l'auteur ou le client lui-même.

## Vidéos transcodées par la plateforme (fichiers téléchargés depuis WeChat / Douyin / TikTok)

Lorsque les métadonnées contiennent `Tencent CAPD MTS`, `Wxmm_` ou `vid:v…`, l'outil marquera `video_context.transcoded`. La recompression efface le bruit du capteur et introduit un faux rythme d'interpolation d'images, donc :

- Les preuves de bruit sont invalidées, "pas de bruit" n'indique plus l'IA ; l'outil marquera ces plans comme "tournage réel ou IA à confirmer".
- Preuves toujours fiables : images répétées 24→30 régulières (les modèles de génération produisent souvent 24 ips ; un film entier natif 30 ips sans images répétées ressemble plus à une sortie directe de téléphone), identifiants implicites AIGC, contenu de l'image (vraies mains, environnement réel, physique naturelle ou non – ceci doit être vérifié visuellement ou avec le VLM).
- Priorité en cas de conflit de preuves : la présence simultanée d'**images répétées 24→30 régulières + identifiants implicites AIGC** a plus de poids que "l'analyse visuelle n'a pas trouvé de défauts d'IA", ne modifiez pas le jugement du plan en tournage réel sur cette base ; écrivez au maximum "tendance IA, tournage réel à confirmer". Inversement, un film entier natif 30 ips, sans images répétées, sans identifiant AIGC, et avec une image normale après analyse visuelle, est jugé comme tournage réel.
- Les fichiers recompressés dont les marques de plateforme ont été effacées (outils de téléchargement ayant supprimé les métadonnées, échantillons du répertoire `docs/cases/videos/`) ne seront pas marqués comme transcodés, mais présentent également un faux rythme d'interpolation d'images. Les plans avec seulement des "fluctuations périodiques de clarté" et sans images répétées seront marqués par l'outil comme "IA ou tournage réel à confirmer", et la conclusion de l'analyse visuelle peut directement modifier le jugement.
