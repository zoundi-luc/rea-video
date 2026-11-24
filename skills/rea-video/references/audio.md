# Décomposition audio

Sortie de l'outil : `audio` (mesures) et `audio_plan` (résultats fusionnés avec le VLM et plan de reproduction) dans `breakdown.json`, ainsi que la chronologie `audio.png`.

## Fiabilité

| Élément | Méthode | Fiabilité (échantillons capsule-cinema) |
|---|---|---|
| Présence de voix | Modulation syllabique dans la bande vocale (3–8 Hz), plus pauses entre les phrases | Élevée |
| Présence de BGM | Son fort et mélodique (rapport harmonique > 0,62) persistant dans les pauses vocales ; persistance harmonique en l'absence de voix ; ou rythme évident. Une seule hauteur de son sur toute la section (son de test, bip, bourdonnement électrique avec harmoniques, même avec un peu de bruit de fond) n'est pas considérée comme de la musique, mais comme `steady_tone`. | Élevée |
| BPM | Autocorrélation de l'enveloppe d'attaque des composants percussifs, avec des candidats à mi-vitesse/double vitesse ; les sons soutenus, les nappes longues sans composants percussifs sont signalés comme "pas de rythme évident", sans BPM ; les sons avec très peu de composants percussifs et un rythme très faible (nappes sans batterie) ne reçoivent pas non plus de BPM. | Élevée (œuf salé 110,0 vs valeur réelle 110,15) |
| Tonalité | Chromaticité + profil de tonalité de Krumhansl | Moyenne-élevée (les deux valeurs réelles sont correctes : Ré majeur) |
| Changement de section | Pics de nouveauté de la chromaticité et de la sonie | Moyenne |
| Effets sonores | Transitoires très prononcés en dehors des sections vocales, et non sur le rythme ; plus prononcés en présence de BGM ; les transitoires doivent avoir une énergie percussive réelle (le bruit de compression des sons soutenus ne compte pas), le son tronqué des 0,1 dernières secondes de la piste ne compte pas. | **Faible** : dans un mix voix + BGM, la précision mesurée au niveau du signal n'est que d'environ 0,2, les effets sonores légers sont pratiquement indétectables. La liste des effets sonores est basée sur le VLM. |
| TTS ou voix humaine | Laissé au VLM | — |
| Voix masculine / féminine | Médiane de la fréquence fondamentale (<150 Hz tend vers la voix masculine, >200 Hz tend vers la voix féminine) | Moyenne, à titre indicatif seulement |
| Montage rythmique | Proportion de coupes tombant sur le rythme vs probabilité aléatoire | Moyenne-élevée |

## Séparation des pistes audio

`decompose` sépare par défaut le son en trois pistes, placées sous `stems/` (`rea-video stems <vidéo>` peut faire uniquement cette étape) :

| Fichier | Contenu |
|---|---|
| `original.wav` | Son original (mixage complet de la vidéo) |
| `vocals.wav` | Voix isolées : narration, voix off, chant. Attention : les sons de clavier, les transitoires comme les "ding" peuvent aussi se retrouver ici. |
| `music.wav` | Musique d'accompagnement (les endroits où les effets sonores se produisent sont soustraits) |
| `voice_S1.wav`, `voice_S2.wav`… | S'il y a plus de deux locuteurs, une piste par personne : seule la section parlée par cette personne est conservée dans les voix isolées, la longueur est la même que celle de la vidéo originale. |

Le modèle est UVR MDX-Net Inst HQ 3 (ONNX, CPU suffisant, premier lancement télécharge environ 67 Mo depuis GitHub, mis en cache dans `~/.cache/rea-video/models`, peut être modifié avec `REA_VIDEO_MODELS`). La séparation du mixage TTS + Suno BGM a une SDR mesurée d'environ 19,7 dB ; la fuite de BGM pure dans la piste vocale est de −42 dB. Environ 0,6 fois le temps réel (4 cœurs).

Lors de la vérification, **écoutez directement vocals.wav et music.wav**, c'est plus facile à juger que d'écouter le mixage : si la voix chante ou parle, si c'est du TTS, si la musique d'accompagnement contient des voix, si la fin est coupée.

### Locuteurs

Lorsque `rea-video[asr]` est installé, `decompose` identifie qui parle et quand dans les voix isolées, les résultats se trouvent dans `speakers` de `breakdown.json` :

- `speakers` : secondes, pourcentage, fréquence fondamentale et indication homme/femme pour chaque voix (`S1`, `S2`…, par ordre d'apparition) ; celles qui n'apparaissent que quelques secondes sont marquées `minor`.
- `turns` : heures de début et de fin et locuteur de chaque segment ; `overlaps` : périodes où deux personnes parlent simultanément.
- Les lignes de dialogue `speech.lines` incluent `speaker` ; lorsque le VLM est activé, les noms des personnages sont associés aux voix par le temps (`name`).

Deux personnes avec des timbres très similaires peuvent être fusionnées en une seule, et la même personne changeant de ton peut être divisée en deux : si le nombre de personnes est important, écoutez les pistes de chaque personne pour confirmer. `--no-speakers` permet de sauter cette étape.

## Détection de la source : généré par IA ou existant ?

**La conclusion en une phrase** se trouve dans `sound_sources.summary_zh`, au format "Type de vidéo → Source de la voix / musique / effets sonores" :

| Type de vidéo | Voix | Musique | Effets sonores |
|---|---|---|---|
| MV musical / Chanson | Chant intégré à la chanson | Principalement **généré par IA** (Suno, etc.) | Bibliothèque d'effets sonores |
| Vidéo IA avec son natif | Généré par le modèle vidéo | Musique d'accompagnement ajoutée en post-production | Généré par le modèle vidéo |
| Tournage réel | Son direct / Voix off humaine | Musique d'accompagnement existante | Son direct |
| Narration/Voix off + Musique d'accompagnement | TTS ou voix off humaine | Principalement **bibliothèque de musique existante** (les workflows IA utilisent aussi souvent Suno pour les nappes) | Bibliothèque d'effets sonores |
| Musique d'accompagnement pure | — | Bibliothèque de musique existante | Bibliothèque d'effets sonores |

Sortie de l'outil : `sound_sources` dans `breakdown.json` (pour la musique / voix / effets sonores, `source`, `leaning`, `probs`, `evidence`, `how_to_confirm` respectifs).

### Première étape : Examiner le format vidéo (détermine l'a priori)

| Format | Comment identifier | A priori de la source musicale |
|---|---|---|
| **MV musical IA** (le film entier est une chanson avec voix) | Le VLM indique format=MV ; ou couche de certitude : la musique couvre tout le film (>85 %) **et la voix chante** (`voice.style` = singing / rap_or_rhythmic, mesuré sur les voix isolées) | Généré par IA 60 % (réduit à 45 % si le VLM n'est pas activé) |
| **Musique d'accompagnement vidéo normale** (narration/voix off + BGM de fond, ou musique d'accompagnement pure sans voix) | La voix parle (`voice.style` = speech), ou pas de voix | Bibliothèque de musique existante 60 % |

Le "chant" et la "parole" sont jugés sur les **voix isolées**, avec deux signaux :

- Hauteur de son soutenue (`sustained_note_ratio`) : le chant reste sur une hauteur de son ≥160 ms, >0,3 est considéré comme du chant. Mesuré : narration TTS 0,14–0,15, rap 0,24 (le rap ne prolonge pas les notes).
- Répétition de refrain (`chorus_repeat_share`) : un fragment mélodique vocal de 4 secondes réapparaît après 6 secondes. >0,1 est considéré comme une chanson (y compris le rap). Mesuré : MV de rap IA 0,26, narration TTS 0,00. Ce signal est inefficace si la courte vidéo n'est qu'un extrait sans refrain répété.

### Deuxième étape : Corriger avec des preuves

| Preuve | Indique | Poids |
|---|---|---|
| Les paroles chantent le personnage/produit/intrigue du film (VLM `lyrics_match_content`) | Généré par IA (chanson personnalisée) | Fort |
| Le VLM reconnaît le titre de la chanson (`song_guess`) | Chanson connue | Fort |
| Le tag musical de la plateforme est un titre de chanson spécifique (`--meta`) | Morceau existant | Fort |
| Le tag de la plateforme est "@son original créé par l'auteur" | Pas une bibliothèque de plateforme ; les MV sont souvent des chansons IA | Moyen |
| La musique de fin est coupée brutalement à plein volume | Morceau existant extrait | Faible |
| La musique et la vidéo se terminent ensemble | Personnalisé/édité selon la durée du film (les deux sont possibles) | Très faible |
| Le fichier contient un identifiant implicite AIGC | Le film entier déclare contenir du contenu IA | Très faible |

Si la probabilité la plus élevée est <45 %, la sortie est "à confirmer", avec une tendance (`leaning`).

### Pièges connus (à toujours rappeler dans la réponse)

**Les vidéos normales produites par des workflows IA ont souvent des BGM générées par Suno** (les propres monkey_wine, œufs salés, nids d'oiseaux de capsule-cinema en sont des exemples). L'a priori "musique d'accompagnement normale = bibliothèque" sera faux pour ces vidéos, et les caractéristiques purement auditives/signal ne peuvent pas distinguer l'instrumental Suno de l'instrumental de bibliothèque. Par conséquent, la conclusion pour la musique d'accompagnement normale doit être formulée comme "tendance bibliothèque, à confirmer", et des méthodes de confirmation doivent être fournies :

1. Les tags musicaux de la page originale de Douyin/Xiaohongshu (il est préférable de les transmettre via `--meta`).
2. "Shazam" de Qishui Music / QQ Music ou ACRCloud : si identifié, c'est une chanson existante ; si non identifié, cela ne signifie pas que c'est de l'IA (les morceaux de bibliothèque peu connus sont souvent non identifiables).
3. Sensation auditive : les chansons IA ont une diction floue, des hautes fréquences faibles avec une sensation métallique, et des paroles étroitement liées à l'image ; l'instrumental IA a souvent une structure inchangée, une fin abrupte ou des boucles.

### Source des voix et des effets sonores

- **Voix** : TTS / voix intégrée à la vidéo IA / enregistrement humain. Les sauts de bruit de fond aux changements de plan (`per_clip_audio.resets_at_cuts`) indiquent que chaque segment audio suit le fragment vidéo, ce qui est le son natif du modèle vidéo IA (comme Veo, Seedance avec audio) ou le son direct du tournage réel.
- **Effets sonores** : la plupart proviennent de bibliothèques d'effets sonores existantes (mixkit, aigive, etc.) ; lorsque le modèle vidéo IA produit un son natif, les effets sonores suivent également le fragment. La couche de certitude ne peut donner qu'une tendance, la liste est basée sur le VLM.

## Méthode de vérification

1. Regardez `audio.png` : les barres vocales, les barres musicales et les lignes de coupe correspondent-elles à votre intuition.
2. En cas de doute sur les effets sonores, extrayez cette section de l'image pour voir s'il y a des événements correspondants (texte pop-up, transition, action) : `rea-video tiles`.
3. Si le VLM donne `source_guess=popular_song`, ou si le tag de la plateforme est un titre de chanson spécifique, indiquez dans le plan de reproduction "nécessite une autorisation ou un remplacement".
4. Écrivez la source musicale selon la section "Détection de la source" ci-dessus, ne dites pas "bibliothèque" de manière définitive pour la musique d'accompagnement normale.

## Reproduction

- **Voix** : DoubaoTTSTool / UniversalTTSTool de capsule-cinema ou clone MiniMax ; utilisez un TTS à durée contrôlable si vous devez respecter la fenêtre temporelle d'origine.
- **BGM** : Utilisez Suno (UniversalMusicGenerationTool) ou une bibliothèque de musique en fonction du BPM, de la tonalité et de l'ambiance ; alignez les points de changement de section avec les plans.
- **Effets sonores** : Placez-les aux points temporels ; alignez les effets sonores avec une hauteur de son sur la tonalité de la BGM (les recettes sfx.py / cues.py de capsule-cinema font cela).
