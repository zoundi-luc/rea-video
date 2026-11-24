# Matériel réel de l'utilisateur

**Définition** : Pixels qui ne sont pas générés ou rendus par le producteur, mais introduits à partir de la réalité, y compris les vidéos filmées, les photos réelles, les captures d'écran de pages web/applications, les enregistrements d'écran, les extraits vidéo lus dans une mise en page, les logos/images de produits collés. Lors de la reproduction, ces éléments doivent être fournis par l'utilisateur sous forme de fichiers originaux et **ne peuvent pas être décrits comme "générés par IA"**.

**Distinction avec le "matériel de référence"** : Les produits, logos, personnages apparaissant dans les vidéos IA, les humains numériques, les images 3D, dont les pixels sont créés par le modèle ou le moteur de rendu, ne sont pas considérés comme du matériel réel ; ils sont enregistrés dans `material.references` et sont désignés dans le rapport comme "matériel de référence à préparer pour la reproduction", et sont utilisés comme images de référence (`@imageN`) pour le modèle lors de la reproduction. Les produits dans les images filmées sont des accessoires et sont également enregistrés comme références.

## Comment l'outil les étiquette

- **Image entière** :
  - Tournage réel → Matériel vidéo filmé
  - Enregistrement d'écran/capture d'écran → Matériel d'enregistrement d'écran ou capture d'écran d'interface (les images fixes sont considérées comme des captures d'écran)
  - Image fixe/panoramique/zoom dont la source est une photo ou une capture d'écran → Photo réelle ou capture d'écran
  - Source d'image fixe inconnue (VLM non activé) → "Matériel image (réel/IA à confirmer)", non compté comme matériel réel
- **Intégré** (détecté uniquement dans les images rendues, c'est-à-dire rendu par code, enregistrement d'écran, image fixe, carte rendue) :
  - Zone de texture photo : entropie de gris élevée, pas de couleur unie, et pas dans la bande de sous-titres → Matériel photo/image, **étiqueté "réel ou IA à confirmer"** (les images collées dans le modèle peuvent aussi être des images IA). Soit le VLM le confirme, soit vous jugez vous-même l'image.
  - Panneau clair + une seule image ≥ 6 petits caractères → Capture d'écran d'interface (directement considérée comme matériel réel)
  - Mouvement dans la zone tandis que l'environnement est statique → Extrait vidéo intégré ou enregistrement d'écran
- **VLM** : Éléments dans `embedded_assets` où `is_real_material=true`. Si le fond est une mise en page rendue (code, enregistrement d'écran, image fixe), il est considéré comme du matériel intégré ; le `real_footage` mentionné par le VLM est enregistré comme "extrait vidéo intégré" (il peut s'agir d'une vidéo IA elle-même) ; si le fond est une vidéo IA / humain numérique / tournage réel, ou des produits, logos, personnages en 3D, il est enregistré comme matériel de référence.

## Détections manquées connues

- Photos sombres, semi-transparentes, utilisées comme arrière-plan d'ambiance (par exemple, l'image de fond de la NASA de mediank) : le contraste de texture est trop faible, la détection de certitude ne peut pas les identifier. Lorsque vous voyez un modèle sombre, vous devez vérifier l'arrière-plan vous-même.
- Captures d'écran de pages web à thème sombre : ce ne sont pas des panneaux clairs, elles ne sont pas détectées, vous devez vérifier s'il y a un navigateur ou un cadre d'interface dans l'image.
- Petits logos, images de produits superposés sur des images filmées ou IA : la couche de certitude ne fait pas de détection d'intégration sur l'image de fond (facile aux fausses alertes), elle dépend du VLM.

## Plans de coupe de la bibliothèque de matériel

Les plans de coupe filmés sans rapport avec le sujet principal de la vidéo, tels que les vues aériennes de villes, les time-lapses, les paysages, les personnages d'affaires, les gros plans de mains, sont souvent achetés sur des sites de matériel et ne sont pas filmés par l'auteur lui-même. L'outil les étiquettera comme "matériel vidéo filmé". Lors de l'examen des images, indiquez "plan de coupe de bibliothèque de matériel suspecté" dans la `description`, et listez-les séparément du matériel filmé par l'auteur lors de la livraison : pour la reproduction, il suffit de trouver des éléments similaires sur un site de matériel, il n'est pas nécessaire de demander les rushes originaux à l'utilisateur.

Il en va de même pour les extraits de films/séries (`film_footage`) : le matériel provient de la société de production, indiquez "nécessite de trouver l'extrait original correspondant, l'utilisation commerciale nécessite une autorisation" lors de la livraison, ne l'écrivez pas comme le matériel de l'utilisateur.

## Format de livraison

Listez chaque élément : numéro de plan, heure, type de matériel, position à l'écran, description du contenu, et "pour la reproduction, vous devrez fournir : ...".
