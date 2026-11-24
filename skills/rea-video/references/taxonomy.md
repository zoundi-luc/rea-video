# Classification des modes de production et comparaisons pour éviter les confusions

## 11 types de plans de base

| Étiquette | Français | Preuves typiques | Méthode de reproduction |
|---|---|---|---|
| live_action | Tournage réel | Bruit du capteur σ>1, bruit temporel >0.8, rapport pixel par pixel inchangé <0.55, tremblement de la caméra à la main, 60fps natifs, métadonnées de l'équipement de tournage | Matériel de tournage réel (fourni par l'utilisateur) ou approximation par IA image-vers-vidéo |
| ai_video | Vidéo générée par IA | Texture photographique sans bruit de capteur, répétition de 24→30 images ou cycle d'interpolation, mouvements de caméra fluides et flottants ; le VLM détecte des doigts, du texte, des déformations d'objets ou des scintillements de texture | Génération des images de début et de fin par capsule-cinema |
| avatar | Avatar IA | Caméra fixe, face avant, seuls la bouche et la tête bougent, piloté par l'audio | TTS/clonage + avatar IA |
| cg_3d | Rendu 3D | Matériaux plats/propres mais l'arrière-plan n'est pas figé pixel par pixel, géométrie stable, pas de déformation | Blender/C4D, ou approximation par IA des images de début et de fin |
| code_render | Rendu par code/modèle | Blocs plats >20%, moins de 70 couleurs, beaucoup de bords droits horizontaux et verticaux ; arrière-plan figé pixel par pixel, seuls des éléments locaux bougent ; pas de textures de matériaux (dégradés de couleurs lisses, grandes zones de couleurs saturées pures, lueurs sur fond sombre, champs de couleurs fractales/shaders) ; sur fond sombre, les zones lumineuses sont toutes de petits points/lignes (particules, nuages de points, fil de fer) | Reconstruction Remotion/HTML ; le rapport donne la méthode en fonction du type de plan (particules → Three.js, champ de couleurs → GLSL, dégradé → CSS blur, graphique → SVG/D3) |
| screen_capture | Capture d'écran | Grande surface d'interface claire, texte dense de petite taille, faible saturation, défilement de page entière | Enregistrement d'interface réelle (fourni par l'utilisateur) |
| still_motion | Image fixe animée (pan/zoom) | Taux de points internes de transformation rigide >95%, résidu <0.3px, pas de résidu après compensation, pas de traces de fréquence d'images 24fps | Une image + ffmpeg local pour reconstruire selon les paramètres mesurés |
| static_hold | Image fixe | Plus de 85% des images sont répétées pixel par pixel | Une image |
| anim_2d | Animation 2D | Non détectable par l'outil, à juger visuellement : lignes et blocs de couleurs plates stables, personnages avec squelettes ou mouvements image par image, "on two" courant | Image de référence du personnage + génération des images de début et de fin ; pour des mouvements labiaux précis, utiliser AE / Live2D / Spine |
| stop_motion | Animation image par image (stop motion) | Non détectable par l'outil, à juger visuellement : matériaux réels (argile, feutre, papier), mouvements saccadés, léger scintillement entre les images, éclairage du même objet réel inchangé | Privilégier le tournage réel (caméra fixe, environ 12 images par seconde) ; l'IA ne peut qu'approximer |
| film_footage | Extrait de film/série | Non détectable par l'outil, seulement des indices : plan encadré par des barres noires, source 24/25fps. À juger visuellement : acteurs ou séries reconnaissables, éclairage professionnel et plusieurs caméras en champ/contre-champ, nombreux figurants et décors complets, logo de chaîne ou filigrane de plateforme | Trouver l'extrait original correspondant et le monter (droits d'auteur appartenant à la production, autorisation nécessaire pour usage commercial) ; si l'extrait original n'est pas utilisé, filmer soi-même avec le même cadrage et éclairage, ou approximation par IA |

`anim_2d` / `stop_motion` / `film_footage` sont jugés uniquement par l'inspection visuelle : si une seule partie a inspecté visuellement, la conclusion est marquée "point à confirmer" ; elle est retirée lorsque le VLM et l'agent ont tous deux inspecté.

`live_action` est utilisé uniquement pour les plans filmés par l'auteur de la vidéo ou le client lui-même ; les plans coupés de films, séries télévisées ou courts métrages existants sont toujours `film_footage`, même s'ils ressemblent beaucoup à du tournage réel.

## Traitement IA sur du tournage réel (ai_edits)

Si le plan de base est du tournage réel ou de l'animation image par image, on vérifie ensuite s'il a été post-traité par IA, ce qui est indiqué dans `ai_edits`. La solution de reproduction ajoutera "traitement IA à effectuer après le tournage" après les scènes de tournage :

| type | Français | À quoi regarder | Reproduction |
|---|---|---|---|
| face_swap | Échange de visage | Scintillement des bords du visage et de la ligne des cheveux, couleur/lumière de la peau du visage et du cou incohérentes, dérive des traits du visage de profil | Modèle d'édition vidéo R12 pour changer de personne |
| lip_sync | Synchronisation labiale/modification de dialogue | Mouvements de la bouche et du menton incohérents, dents floues, seule la zone de la bouche a une qualité d'image différente | Resynchronisation labiale R13 |
| restyle | Restylisation de segment entier | Les mouvements sont ceux d'une personne réelle, mais l'image est dans un style anime/peinture à l'huile/argile, etc., les textures flottent entre les images | Modèle d'édition vidéo R12 |
| outfit_swap | Changement de tenue par IA | Scintillement de la texture des vêtements, flou à la jonction avec les bras | Image d'essayage R05 + vidéo |
| bg_replace | Détourage/remplacement de fond | Halo ou crénelage sur les bords des cheveux, direction de la lumière incohérente entre la personne et le fond, perspective du fond incorrecte | Détourage sur fond vert, ou R12 |
| object_edit | Ajout/suppression/remplacement d'objet | Scintillement des bords de l'objet, ombre manquante | R12 |
| beautify | Embellissement/amincissement du visage | Peau excessivement lisse, lignes droites de l'arrière-plan courbées près du visage | Embellissement comme Jianying |

## Points clés de jugement rapide

| Phénomène | Indique |
|---|---|
| Images adjacentes répétées pixel par pixel, pas de changement du début à la fin | Image fixe ; si c'est une carte rendue en aplat, classée comme rendu par code |
| L'image entière est mise à l'échelle/translatée par une transformation rigide, pas de résidu après compensation, et **pas** de traces de fréquence d'images de source 24fps | Image fixe animée (pan/zoom) |
| Beaucoup de blocs de couleurs plates, peu de couleurs utilisées, beaucoup de bords droits horizontaux et verticaux | Rendu (code ou 3D) ; pixels d'arrière-plan complètement inchangés image par image, seuls des éléments locaux bougent → animation 2D par code |
| Environ 20% des images répétées, cycle 4–6 (24→30) | La source est 24fps : généré par IA / 3D / matériel de film ou de série télévisée, pas de tournage natif par téléphone |
| Dans un écran vertical, un plan 16:9 ou plus large est encadré par des barres noires au milieu, avec un titre en haut et des sous-titres explicatifs en bas | Format de commentaire de film/série → tendance à l'extrait de film/série ; les courts métrages d'IA avec un aspect cinématographique peuvent aussi ajouter des barres noires, à juger visuellement |
| L'image contient « Année ·《Titre de la série》», logo de chaîne, filigrane de plateforme, ou plusieurs segments de styles et d'étalonnages différents qui changent rapidement | Montage de films/séries / compilation de scènes célèbres → tendance à l'extrait de film/série |
| Seule la clarté fluctue périodiquement, pas d'images répétées (interpolation) | Preuve faible : l'interpolation et la recompression peuvent le créer, à confirmer visuellement |
| Natif ≥48fps sans répétition, sans cycle d'interpolation | Principalement tournage réel par téléphone/appareil photo |
| Bruit du capteur et bruit temporel évidents, tremblement de la caméra à la main | Tournage réel |
| Fichier transcodé par la plateforme : l'ensemble du film est natif 30fps, les plans de type tournage réel n'ont pas d'images répétées | Tendance au tournage réel par téléphone (la preuve de bruit est invalidée après transcodage, la fréquence d'images est prioritaire) |
| Presque sans couleur, plan plat utilisant un nombre limité de couleurs | Animation d'interface/document (rendu par code), pas 3D |
| Sur fond presque noir, les zones lumineuses sont presque toutes de petits points ou de fines lignes, pas de surfaces lumineuses et sombres continues | Graphiques de particules/nuages de points/fil de fer (rendu par code), pas d'entités 3D, d'IA ou de tournage réel de nuit |
| L'image entière n'a presque pas de textures fines : dégradés de couleurs lisses, grandes zones de couleurs saturées pures, lueurs sur fond sombre, ou champ de couleurs arc-en-ciel | Dégradés/vecteurs/shaders dessinés par code, pas de rendu 3D (la 3D a des textures de matériaux comme le tissu, le bois) ; même si l'image entière est en mouvement |
| Musique omniprésente, voix chantée (beaucoup de hauteurs continues) | Clip musical → la chanson est probablement générée par IA |
| Voix off + musique de fond | Musique d'ambiance normale → tendance à la bibliothèque musicale existante (à confirmer, Suno est souvent utilisé dans les flux de travail IA) |
| Bruit de fond qui saute aux coupes | Le son suit les segments : vidéo IA avec son natif ou son synchrone de tournage réel |
| Fichier avec identifiant implicite GB 45438 AIGC Label=1 | Déclaré comme généré par IA (indique seulement que l'ensemble du film a été déclaré, les plans spécifiques doivent encore être jugés individuellement) |
| Panneau clair avec beaucoup de texte de petite taille | Capture d'écran d'interface intégrée → matériel réel |
| Pendant les pauses vocales, il y a toujours un son fort et mélodique | Musique de fond présente |
| Grande surface presque noire mais granuleuse, zones lumineuses non plates, présence de visages | Tournage réel de nuit/faible lumière (les blocs plats causés par la compression des zones sombres lors du transcodage ne sont pas une caractéristique de rendu) |
| Visage occupant ≥6% de l'image, présent tout au long du plan, parlant | Gros plan de personne en tournage réel ou avatar IA ; les blocs plats sur les murs/vêtements ne sont pas une preuve de rendu |

## Comparaison des confusions courantes (à vérifier point par point)

**Tournage réel vs vidéo générée par IA**
- Tournage réel : le grain du bruit varie d'une image à l'autre ; les mains, le texte, les personnes éloignées sont normaux ; la physique est correcte (tissu, liquide, collisions).
- IA : la peau et la lumière sont trop parfaites ; les personnes en arrière-plan ou le texte sont corrompus ; les bords des objets "bouillonnent" ; les mouvements sont lents et flottants ; l'image a tendance à se figer à la fin du plan.
- Fréquence d'images : source 24fps (IA/film) vs native 60fps (téléphone). Notez que l'interpolation d'images par IA à 60fps laissera des cycles de netteté, `sharp_period_ac>0.45`.
- La couche de certitude est la plus faible pour cette paire, **vous devez combiner le VLM et votre propre examen des images**.

**Vidéo IA de style dessin animé 3D vs vrai rendu 3D**
- Vrai 3D : la géométrie et les matériaux sont stables d'une image à l'autre, les cheveux et les tissus bougent selon la physique, peuvent être bouclés avec précision, beaucoup de blocs plats et peu de couleurs.
- IA : le même objet se déforme légèrement dans le plan, les textures scintillent, le bruit ressemble plus à une photo (plus de 100 couleurs).
- De nombreux comptes "dessin animé 3D" sur Douyin sont générés par IA, mais sans identification, on ne peut qu'indiquer une tendance.

**Graphiques de particules sur fond sombre vs rendu 3D vs vidéo IA / tournage réel de nuit**
- Graphiques de particules (rendu par code) : organes, corps humains, terre, molécules, etc., sont composés de milliers de points lumineux ou de lignes fines, sans surfaces continues claires et sombres ; souvent accompagnés de titres de chapitre en haut à gauche, de lignes de légende, de chiffres qui sautent. Three.js, AE Plexus / Trapcode peuvent tous le faire, la reproduction suit le projet de code.
- Rendu 3D : a des surfaces continues claires et sombres, des matériaux et des ombres.
- Tournage réel de nuit / IA : les zones lumineuses sont des objets et des taches lumineuses avec des transitions claires et sombres, avec du grain ou des déformations.
- Lors de la vérification, la `description` doit indiquer clairement la forme, la couleur et le mouvement de chaque plan de particules (flux de particules, déformation, zoom/orbite), et où se trouvent les légendes et les chiffres ; le tableau plan par plan de la section "Composition par code" du rapport l'utilisera. Si vous écrivez seulement "fond de particules", la reproduction sera une masse de taches lumineuses.

**Dégradé / lueur / champ de couleur rendu par code vs rendu 3D**
- Image par code : l'ensemble de l'image n'a presque pas de textures fines, seulement des dégradés lisses, des blocs de couleur pure, des lueurs et du texte ; fonds de taches lumineuses en dégradé courants, cartes en verre dépoli, texte néon, cartes 3D CSS qui se retournent, zoom fractal et shaders plasma. Même si l'image entière bouge (dérive de l'arrière-plan, respiration de la lueur), c'est un rendu par code.
- Rendu 3D : les objets ont des textures de matériaux (tissu, grain de bois, métal, particules de plastique), des ombres portées et des relations d'éclairage entre les objets.
- Affiche plate avec grain de film ajouté : une fois le grain retiré, ce sont des blocs de couleur pure, considérés comme un rendu par code ; si le grain est très lourd (l'outil mesure un bruit σ≥3), l'outil peut ne pas le détecter, il faut juger par l'image.
- Un dégradé lisse qui change lentement de couleur peut être confondu avec un fondu enchaîné ; l'outil l'exclut en fonction de la "stabilité de la vitesse de changement" ; lors de la vérification, si un effet d'arrière-plan continu est toujours coupé en plusieurs plans, traitez-le comme un seul plan.

**Rendu par code vs capture d'écran**
- Rendu par code : grande taille de police, couleurs de marque, vecteur clair, éléments avec animation d'entrée.
- Capture d'écran : fond clair, petits caractères denses, contrôles d'interface (boutons, icônes, navigation), souvent mis à l'échelle ou défilés dans leur ensemble.
- Capture d'écran intégrée dans un modèle : la couche inférieure est considérée comme un rendu par code, la capture d'écran est listée séparément dans les "vrais rushes".

**Comment écrire la description d'un plan rendu par code**
- La "chronologie des animations plan par plan" de la section "Composition par code" du rapport est mesurée par l'outil : position, temps d'apparition, direction, courbe de vitesse, valeur de couleur de chaque élément, les éléments apparaissant successivement sont fusionnés en un "intervalle de X secondes" ; la bande d'images clés est `shots/shot_XXX_strip.jpg`, les captures d'écran des éléments et le collage numéroté sont `shots/shot_XXX_elements.jpg`.
- En vous référant à ceux-ci, écrivez dans la `description` ce qu'est chaque élément par numéro ("1–12 : cartes d'icônes à coins arrondis, apparaissant successivement"), sans répéter les valeurs mesurées.

**Zoom/panoramique sur image statique vs zoom lent de vidéo IA**
- Zoom/panoramique : le logiciel de montage rend à la fréquence d'images de la timeline, chaque image est différente, il n'y a pas de motif de répétition 24→30.
- Zoom IA : avec un motif d'images répétées de source 24fps, le sujet a souvent de légers mouvements (respiration, clignement).

**Animation 2D vs animation par code vs vidéo de style animation IA**
- Animation 2D : a des personnages et des performances, des lignes stables, précises image par image, souvent en "une image sur deux" (ne change qu'une fois toutes les deux images).
- Animation par code : entrée et ralenti de texte, graphiques, UI, pas de performance de personnage.
- Style animation IA : les lignes se déplacent entre les images, les détails se déforment, traces de source 24fps.

**Animation image par image (stop motion) vs vidéo IA vs tournage réel**
- Stop motion : le même objet réel est déplacé image par image, l'éclairage est constant, il y a de légers scintillements et saccades entre les images, et des empreintes digitales, des bords effilochés sur les matériaux.
- IA imitant le stop motion : le matériau lui-même change entre les images (dérive de la texture de l'argile), pas de rythme saccadé réel.
- L'outil juge souvent le stop motion comme de l'IA (les motifs de fréquence d'images sont similaires), lors de l'examen des images, concentrez-vous sur la stabilité du matériau.

**Extrait de film/série vs mini-série IA vs tournage réel personnel**
- Extrait de film/série : acteurs ou séries reconnaissables ; éclairage professionnel (lumière principale, contre-jour, sources lumineuses pratiques dans le décor), profondeur de champ et plusieurs caméras en champ/contre-champ ; nombreux figurants, décors et accessoires complets, scènes d'action avec doublures et câbles ; texte à l'écran (enseignes, journaux, écrans) clair et lisible ; souvent avec logo de chaîne, filigrane de plateforme, génériques de début et de fin, ou format large encadré de barres noires.
- Mini-série IA : visages trop parfaits, différents personnages se ressemblent beaucoup ; erreurs de mains, de dents, de texte ; peu de personnages en arrière-plan et flous ; textures d'objets et de vêtements qui dérivent entre les images ; les plans sont souvent des gros plans individuels de 5 à 10 secondes. Les clauses de non-responsabilité telles que "effets cinématographiques", "nécessités scénaristiques" sont également courantes dans les explications de mini-séries IA et ne peuvent pas être considérées comme des preuves à elles seules.
- Tournage réel personnel : vlogs, unboxings où l'auteur ou le client apparaît, filmés avec un téléphone ou une petite équipe, sans l'échelle d'un plateau de tournage et de figurants.
- Dans les vidéos explicatives, si l'auteur insère son propre face caméra ou des images IA, étiquetez-les séparément par plan.
- L'outil, lorsqu'il n'active que les pixels, jugera les extraits de film/série comme "vidéo IA" ou "tournage réel" et les marquera "à confirmer", vous devrez corriger le jugement lors de la vérification.

**Jeu vidéo vs rendu 3D vs capture d'écran**
- Gameplay, commentaires de jeu, montages de jeu : la couche inférieure est `screen_capture` (enregistre le jeu rendu en temps réel à l'écran), pas `cg_3d`. Regardez la barre de vie, la mini-carte, le réticule, les icônes de compétences, les chiffres de dégâts, la boîte de discussion, ce type de HUD. La reproduction est l'enregistrement du jeu, la `description` indique le nom du jeu (si reconnaissable), la perspective et la position du HUD.
- Bande-annonce de cinématique de jeu, cinématique : pas de HUD, la mise en scène est cinématographique, classé comme `cg_3d`.
- L'outil et le VLM peuvent tous deux juger les écrans de jeu avec HUD comme de la 3D ou une interface de capture d'écran, lors de la vérification, le HUD prévaut.

**Bande dessinée animée / série animée vs animation 2D vs vidéo IA**
- Cases de bande dessinée statiques avec seulement des zooms/panoramiques → `still_motion` ; cases avec des animations locales superposées comme des clignements d'yeux, des cheveux qui flottent, des bouches qui bougent → `anim_2d` ; lignes qui se déplacent entre les images, détails qui se déforment → `ai_video`.
- Les séries animées sont souvent des images IA + effets locaux, `image_source` est rempli avec `ai_image` ou dessin à la main, en fonction des lignes et des détails comme les doigts.

**Image fixe : image IA vs photo réelle vs carte rendue**
- Carte rendue (couleur unie, peu de couleurs) → classée comme rendu par code.
- Les images IA et les photos réelles ne peuvent pas être distinguées au niveau de la couche de certitude, laissez le VLM faire ; si vous ne pouvez pas juger, écrivez "matériel image (réel/IA à confirmer)".

## Coupes

- Coupe franche : pic de distance d'histogramme et de différence de pixels, et la zone de changement dépasse 25%. L'apparition d'éléments n'est pas une coupe.
- Jump cut / coupe rapprochée : même position de caméra, même arrière-plan, la position du personnage ou la valeur de plan change brusquement en une seule image. La zone de changement n'est que de plus de 17%, mais plus de 2,5 fois supérieure au changement des quelques images précédentes et suivantes, les deux images précédentes et suivantes sont stables, et l'image ne revient pas à l'état d'avant la coupe.
- Flash, flash de bouche de canon, stroboscope : l'image devient plus lumineuse pendant une ou deux images puis revient à la normale, ce n'est pas une coupe ; une transition par flash blanc qui s'estompe pour révéler une nouvelle image est toujours une coupe.
- Plan court : un plan stable entre deux coupes franches nettes, le plus court est de 0,12 seconde (insertion de montage rapide, image de couverture de début) ; plusieurs limites plus proches appartiennent à la même transition, la plus forte est conservée.
- Fondu enchaîné : l'image du milieu est un mélange linéaire des images des deux extrémités (α entre 0,2 et 0,8, résidu <0,2), et le mouvement de zoom/panoramique est exclu par le flux optique.
- Fondu d'entrée/sortie : la luminosité diminue jusqu'à l'extrême obscurité ou l'extrême luminosité puis revient.
- Transition sans coupe franche : une section d'image stable, une section de transition au milieu, une section d'image stable à la fin, les deux extrémités sont des images différentes, et le milieu peut être interprété comme un fondu d'entrée/sortie / fondu enchaîné / balayage / glissement, alors seulement c'est une limite. Le même scénario qui ne fait que s'éclaircir ou s'assombrir, les zooms et panoramiques à l'intérieur du plan ne sont pas considérés.
- Les barres noires et les bannières fixes en haut et en bas sont recadrées avant la mesure, la transition d'image à l'intérieur des barres noires ne sera pas diluée par les barres noires.

**Types de transition** (`transition` de chaque plan : `type`, heures de début/fin `start` / `end`, `duration`, avec `direction` si directionnel)

| type | Ce qui apparaît à l'écran | Comment le reconnaître |
|---|---|---|
| `fade` | Via un écran noir / blanc (`via`) | Il y a une image plate purement noire ou blanche au milieu, l'image précédente et suivante s'assombrissent ou s'éclaircissent |
| `flash` | Flash blanc, fuite de lumière brûlant en blanc puis révélant une nouvelle image | Le milieu est lumineux, presque tout blanc mais pas une image plate ; ou la première image après la coupe est très lumineuse, puis diminue |
| `dissolve` | Fondu enchaîné | Chaque image intermédiaire est un mélange linéaire des deux extrémités |
| `wipe` | Balayage (bord droit, circulaire, stores, horloge) | Regardez bloc par bloc, chaque bloc est soit l'ancienne image, soit la nouvelle image, la zone de la nouvelle image augmente progressivement ; `direction` est la direction du mouvement du bord, `center_out` / `edges_in` est l'ouverture/fermeture circulaire |
| `slide` | Glissement (`mode` : `push` les deux bougent ensemble, `cover` la nouvelle image glisse, `reveal` l'ancienne image glisse) | L'image du milieu peut être composée des images des deux extrémités par un déplacement linéaire le long d'un bord droit |
| `whip` | Coup de fouet : panoramique rapide avec flou de mouvement, le point de coupe est caché dans le flou | Les images avant et après la coupe franche se déplacent considérablement dans une direction, les détails sont effacés |
| `zoom` / `spin` | Zoom / rotation vers le plan suivant | Le facteur de zoom ou l'angle de rotation estimé image par image avant et après la coupe franche est très grand |
| `blur` | Flou puis mise au point | Les détails des deux côtés de la coupe franche sont nettement inférieurs à ceux du plan habituel |
| `glitch` | Glitch : décalage, l'ancienne et la nouvelle image clignotent alternativement | Il y a plusieurs sauts brusques dans l'intervalle, et l'image est revenue à l'ancien plan |
| `shake` | Tremblement avant et après le point de coupe | Le déplacement image par image est important mais s'annule mutuellement |

Les coups de fouet, zooms, rotations, flous, tremblements ne sont reconnus qu'autour des coupes franches : les mouvements similaires sans coupe franche sont des mouvements de caméra à l'intérieur du plan.
- Battement MG : à l'intérieur d'un plan long, "image fixe → animation → image fixe", la différence de contenu entre les deux images fixes dépasse 12%, enregistré comme un battement à l'intérieur du plan, non considéré comme une coupe.
