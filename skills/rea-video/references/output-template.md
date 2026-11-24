# Livraison à l'utilisateur

## Principes

- Les réponses et les rapports sont divisés en deux sections distinctes, sans mélange :
  - **Analyse** : une conclusion en une phrase (comment cette vidéo a été réalisée), deux ou trois lignes sur le contenu et les personnages (de quoi parle la vidéo, personnages principaux / scènes / produits), la structure du storyboard, le montage et l'habillage, le son, les vrais rushes, les points à confirmer. Écrire plan par plan, sans regrouper les plans par méthode de génération.
  - **Plan de reproduction** : selon le modèle choisi par l'utilisateur (deuxième partie du rapport, généré par `rea-video plan`). Si l'utilisateur n'a pas encore choisi et qu'il y a des plans IA, demandez d'abord quel modèle utiliser, ne choisissez pas à sa place.
- Le plan de reproduction doit d'abord fournir des instructions "à suivre" : le début de la deuxième partie du rapport (le pack d'analyse `video/remake.md` "à suivre") a déjà organisé les étapes par type de vidéo. Reprenez-les telles quelles, en restant concis : une phrase par étape, pour que l'utilisateur puisse agir. Les mesures numériques restent dans les sous-sections du rapport. Si le type est mal identifié, expliquez et donnez l'ordre des étapes pour le type correct. Indiquez clairement sur quelles capacités de quel modèle le plan est basé (première phrase de la deuxième partie du rapport).
- S'il y a des plans générés par IA, ajoutez une note : les prompts dans le rapport ont une structure générique ; modifiez-les à nouveau avant la génération en suivant le guide officiel des prompts du modèle ou la compétence de prompt correspondante.
- Le plan de reproduction doit être écrit selon l'organisation de la production réelle, et non plan par plan de montage :
  - Plans IA → **Unité de génération** : plusieurs plans consécutifs générés en une seule fois, quel modèle utiliser, matériel de référence (`@image` produit/personnage, `@video` extrait de la vidéo originale), prompt multi-plans combiné, comment les unités se raccordent. Si le moteur par défaut ne prend pas en charge plusieurs plans à la fois, copiez `engine_note` et expliquez qu'un changement de modèle peut réduire le nombre d'appels.
  - Plans filmés → **Séance de tournage** : quels plans sont de la même scène, du même angle de caméra, filmés ensemble ; l'éclairage de chaque scène ; d'abord les plans larges, puis les gros plans. Le storyboard lui-même reste détaillé plan par plan.
  - Plans avec des acteurs → Décrivez clairement l'émotion et la performance de chaque plan et comment les reproduire (rapport "Performance et émotion" : expressions, actions, ton, et si l'expression est définie par la première image, si la voix off est enregistrée avant l'animation, si c'est une migration de performance ou si l'acteur joue en suivant).
  - Rendu par code → Plusieurs segments de code combinés, décrivez clairement les éléments visuels et les animations de chaque plan (chronologie d'animation plan par plan de la section "Composition par code" du rapport : position des éléments, temps d'apparition, direction, vitesse, valeurs de couleur, captures d'écran des éléments dans `shots/`) ; image fixe animée (pan/zoom) → reconstruction locale.
- Si les prompts sont manquants (VLM non activé), complétez-les en regardant les images : remplissez `replication.image_prompt / video_prompt / video_prompt_en` pour chaque plan dans la réponse de `rea-video review`. Après `apply-review`, les unités de génération les incluront automatiquement.
- Indiquez le chemin du fichier de rapport (`report.html`) à l'utilisateur. S'il y a des plans rendus par code et que l'utilisateur souhaite les reproduire, informez-le que la reproduction nécessite l'intégralité du répertoire du rapport (captures d'écran des éléments et barres d'images clés dans `shots/`, fichiers de sous-titres dans `packaging/`). Fournir uniquement le HTML ou le PDF manquera des captures d'écran individuelles. Ne collez pas l'intégralité du `breakdown.json` dans la conversation.

## Langue

La langue du rapport suit `--lang` (zh / en), la langue de la réponse suit l'utilisateur ; l'ordre de détermination des deux est décrit dans SKILL.md "Livraison à l'utilisateur". Le modèle ci-dessous est en chinois, les réponses en français utiliseront la même structure : verdict en une ligne → contenu et personnages → plan de reproduction → liste des plans → habillage → audio → matériel que vous devez fournir → points à confirmer → chemin du rapport.

## Modèle de réponse (français)

**Verdict en une ligne** : Production mixte – 62% de vidéo générée par IA pour les images de fond, 30% de modèle de code, 8% de tournage réel ; sous-titres superposés par code sur toute la vidéo ; 2 extraits d'écran réels insérés ; voix TTS féminine + BGM pop à 110 BPM, coupes synchronisées sur le rythme.

**Contenu et personnages** : Court métrage narratif, 4 plans ; personnage principal A "Xiaohuang" (petit hippopotame jaune de dessin animé, combinaison rose, sac rose en bandoulière, présent tout au long du film), B petit ami (mêmes couleurs, #3–#4) ; scène S1 rue de ville de jour. Pour la reproduction, A et B auront chacun une image de référence fixe utilisée dans toutes les unités de génération.

**Storyboard**

| # | Temps | Visible à l'écran | Incrustation | Méthode de production (déduction, confiance) | Preuve de déduction | Source du matériel | Route de reproduction |
|---|---|---|---|---|---|---|---|
| 1 | 0:00–0:02.5 | Xiaohuang salue dans la rue ; déformation des doigts de la main gauche | Sous-titres, titre | Vidéo IA (86%) | 24→30 images répétées | Généré par IA | Images de début et de fin de capsule-cinema |

Dans "Visible à l'écran", n'écrivez que ce qui peut être vérifié à partir de la capture d'écran (contenu, mouvement de caméra, défauts) ; le taux de rafraîchissement, le bruit, les métadonnées et autres mesures de l'outil sont écrits dans "Preuve de déduction", et la méthode de production est indiquée comme une déduction. Si les deux ne correspondent pas, indiquez-le.

**Tournage, éclairage et montage** (à écrire s'il y a des plans filmés, correspondant aux lignes de cadrage / angle de caméra / éclairage / montage / format à la fin de `rea-video summary`) : format vidéo (face caméra/tabletop/vlog), valeur de plan et angle de caméra, caméra à la main ou sur trépied, nombre de caméras/scènes ; plan d'éclairage (direction et hauteur de la lumière principale, rapport de contraste, dureté/douceur, température de couleur, présence de lumière d'appoint/contre-jour, sources lumineuses dans l'image) ; techniques de montage (coupes franches sur les respirations, coupes rapprochées, proportion d'insertion de captures d'écran/enregistrements d'écran) ; fournir une liste d'équipement de reproduction. Si les valeurs mesurées et vos conclusions visuelles sont en conflit, indiquez la preuve.

**Habillage** : Sous-titres (nombre de phrases, position, couleur / contour / fond, surbrillance des mots-clés, mode d'apparition, chemin du fichier SRT/ASS) ; texte stylisé, titres, cartons de chapitre, étiquettes de suivi (temps, texte, style, animation) ; stickers / GIF / emojis / image dans l'image (temps, position, ce qui est collé, si c'est en boucle) ; quels effets sonores sont synchronisés avec l'apparition du texte ou des stickers ; quels textes stylisés / stickers sont liés à quelle ligne de dialogue ("positionnement par dialogue"), quels sont des calques permanents. Indiquez ce que l'outil n'a pas mesuré et que vous avez complété visuellement.

**Son** : Voix (TTS ou humaine, timbre, dialogue voir tableau de script du rapport) / BGM (titre de la chanson supposé, style, BPM, tonalité, source et risque de droits d'auteur, sections) / Effets sonores (point temporel → événement visuel correspondant) / Mixage (si la musique est atténuée). Chaque élément de la section "Son" du rapport est une carte, il suffit de la copier.

**Matériel réel que vous devez fournir** : Capture d'écran de la page GitHub au milieu du plan #4...

**Plan de reproduction** : Écrire selon `production_plan`. Pour les plans IA, écrire les unités de génération (plage de plans, modèle, matériel de référence, prompt multi-plans, raccord) ; pour les plans filmés, écrire les séances de tournage (scène → angle de caméra → plan, éclairage) ; pour le rendu par code, écrire comment plusieurs segments de code sont combinés, quelle approche est utilisée pour chaque segment, et pointer vers la chronologie d'animation plan par plan et les captures d'écran des éléments ; une phrase pour l'image fixe animée (pan/zoom). Confirmez les opérations payantes avant de les mentionner.

> Ex : 8 plans IA → 3 unités de génération, 3 appels Seedance 2.5 (Seedance 2.0 par défaut ne prend pas en charge plusieurs plans à la fois, 8 appels seraient nécessaires plan par plan). G1 #1–#5 (9.0s) : @image1 image produit + @video1 vidéo originale 0–9s, génère 5 plans en une seule fois...

**Points à confirmer** : #7 tournage réel ou IA à confirmer (tendance IA 64%) : pas de mains ni de texte pour juger, il est suggéré de...

**Rapport** : out/ref/report.html

**VLM** : Copiez la ligne `VLM:` de `rea-video summary` (activé / partiellement activé / tous les appels ont échoué / non configuré / non activé). Si non activé, et que vous ne pouvez pas non plus voir les images, ajoutez une suggestion : "Re-exécutez avec --vlm après avoir configuré GEMINI_API_KEY, le jugement tournage réel/IA/3D sera plus précis." Si vous pouvez voir les images, écrivez simplement "vérifié par l'agent visuellement".
