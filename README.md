# Projet HDFS - Fusion de Petits Fichiers

## 📋 Description du Projet

Ce projet implémente une solution orientée objets pour résoudre le **problème des petits fichiers** dans les systèmes distribués de type HDFS (Hadoop Distributed File System).

### Le Problème des Petits Fichiers

Dans HDFS, chaque fichier génère des métadonnées stockées en mémoire par le NameNode. Un grand nombre de petits fichiers entraîne:
- **Surcharge mémoire** du NameNode
- **Performances dégradées** lors des opérations de lecture/écriture
- **Coût élevé** de gestion des métadonnées

### La Solution

Ce programme regroupe les petits fichiers en **clusters** en utilisant un algorithme de **clustering hiérarchique agglomératif** avec la méthode **single-linkage**, permettant de:
- Réduire le nombre de fichiers de métadonnées
- Minimiser la surcharge du NameNode
- Optimiser l'utilisation du stockage

---

## 🧮 Méthode de Clustering Utilisée

### Algorithme: Clustering Hiérarchique Agglomératif

**Principe:**
1. **Initialisation**: Chaque fichier commence comme un cluster individuel
2. **Itération**: À chaque étape:
   - Trouver les deux clusters les plus proches
   - Vérifier la contrainte de taille: `taille_totale ≤ 128 MB`
   - Si OK → fusionner les clusters
   - Sinon → marquer comme non fusionnable
3. **Terminaison**: Quand aucune fusion n'est plus possible

### Distance Entre Fichiers

La distance est calculée **uniquement sur la taille**:

```
distance(fichier_i, fichier_j) = |taille_i - taille_j|
```

### Méthode de Linkage: Single-Linkage

La distance entre deux clusters A et B est le **minimum** des distances entre leurs éléments:

```
distance(A, B) = min(distance(fichier_i, fichier_j))
                 pour tout fichier_i ∈ A, fichier_j ∈ B
```

---

## 🏗️ Structure du Projet

```
projet_hdfs/
│
├── models/                      # Classes de données
│   ├── __init__.py
│   ├── small_file.py           # Classe SmallFile (nom, taille)
│   └── cluster.py              # Classe Cluster (groupe de fichiers)
│
├── core/                        # Algorithmes principaux
│   ├── __init__.py
│   ├── distance_matrix.py      # Calcul de la matrice de distance
│   ├── clustering.py           # Clustering hiérarchique agglomératif
│   └── merger.py               # Fusion physique des fichiers
│
├── data_io/                     # Entrées/Sorties
│   ├── __init__.py
│   ├── file_generator.py       # Génération de fichiers de test
│   └── metadata_writer.py      # Écriture des métadonnées JSON
│
├── output/                      # Dossier de sortie (créé automatiquement)
│   ├── cluster_*.bin           # Fichiers fusionnés
│   ├── cluster_*_metadata.json # Métadonnées individuelles
│   ├── clusters_summary.json   # Résumé de tous les clusters
│   └── detailed_report.txt     # Rapport détaillé
│
├── main.py                      # Point d'entrée du programme
├── README.md                    # Ce fichier
└── requirements.txt             # Dépendances Python
```

---

## 📦 Installation

### Prérequis

- Python 3.7 ou supérieur
- Aucune bibliothèque externe requise (bibliothèque standard uniquement)

### Installation

```bash
# Cloner ou télécharger le projet
cd projet_hdfs

# Optionnel: créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances (aucune pour ce projet)
pip install -r requirements.txt
```

---

## 🚀 Utilisation

### Exécution du Programme

```bash
python main.py
```

### Modes d'Exécution

Le programme propose plusieurs modes:

1. **Exemple 1**: Scénario réaliste avec fichiers mixtes
2. **Exemple 2**: Liste personnalisée de fichiers
3. **Exemple 3**: Problème des petits fichiers
4. **Mode interactif**: Configuration personnalisée
5. **Tous les exemples**: Exécution séquentielle

---

## 📊 Exemple d'Entrée

### Génération Automatique

```python
from io.file_generator import FileGenerator

generator = FileGenerator()
files = generator.generate_realistic_scenario("mixed")
```

Génère un ensemble de fichiers comme:
```
file_0001.dat (5.00 MB)
file_0002.dat (10.00 MB)
file_0003.dat (20.00 MB)
...
```

### Création Manuelle

```python
from models.small_file import SmallFile

files = [
    SmallFile("doc1.txt", 10.0),
    SmallFile("img1.jpg", 25.0),
    SmallFile("video.mp4", 45.0),
]
```

---

## 📤 Exemple de Sortie

### Fichiers Fusionnés

```
output/
├── cluster_1.bin        # Cluster 1 (96.5 MB, 8 fichiers)
├── cluster_2.bin        # Cluster 2 (120.0 MB, 5 fichiers)
└── cluster_3.bin        # Cluster 3 (78.3 MB, 6 fichiers)
```

### Métadonnées JSON

**`clusters_summary.json`:**
```json
{
  "total_clusters": 3,
  "clusters": [
    {
      "cluster_id": 1,
      "files": ["file_0001.dat", "file_0003.dat", "file_0005.dat"],
      "file_count": 3,
      "size_total_mb": 96.5
    },
    {
      "cluster_id": 2,
      "files": ["file_0002.dat", "file_0004.dat"],
      "file_count": 2,
      "size_total_mb": 120.0
    }
  ],
  "summary": {
    "total_files": 19,
    "total_size_mb": 294.8,
    "file_reduction_rate_percent": 84.21
  }
}
```

### Rapport Détaillé

**`detailed_report.txt`:**
```
================================================================================
RAPPORT DE FUSION DE FICHIERS HDFS
================================================================================

Nombre de fichiers originaux: 19
Nombre de clusters créés: 3
Taux de réduction: 84.21%

--------------------------------------------------------------------------------
DÉTAILS DES CLUSTERS
--------------------------------------------------------------------------------

Cluster ID: 1
  Nombre de fichiers: 8
  Taille totale: 96.50 MB
  Fichiers:
    - file_0001.dat (5.00 MB)
    - file_0003.dat (10.00 MB)
    ...
```

---

## 🎯 Contraintes Techniques

### Implémentation

✅ **Programmation orientée objets** stricte  
✅ **Aucune bibliothèque externe** de clustering (pas scipy, pas scikit-learn)  
✅ **Algorithme manuel** complètement implémenté  
✅ **Méthode single-linkage** respectée  
✅ **Contrainte de taille** de 128 MB par cluster  
✅ **Distance euclidienne** basée uniquement sur la taille  

### Classes Principales

- `SmallFile`: Représente un fichier (nom, taille)
- `Cluster`: Groupe de fichiers
- `DistanceMatrix`: Matrice de distance entre clusters
- `AgglomerativeClustering`: Algorithme de clustering
- `FileMerger`: Fusion physique des fichiers
- `MetadataWriter`: Écriture des métadonnées

---

## 📈 Performances

### Complexité

- **Temps**: O(n³) dans le pire cas
  - n² paires à considérer
  - n itérations maximum
  
- **Espace**: O(n²) pour la matrice de distance

### Optimisations Possibles

- Utiliser une structure de données plus efficace (heap)
- Implémenter un cache pour les distances
- Paralléliser le calcul de la matrice

---

## 🔧 Configuration

### Modifier la Taille Maximale

Dans `main.py`:
```python
clustering = AgglomerativeClustering(max_cluster_size_mb=256.0)  # 256 MB
```

### Changer le Répertoire de Sortie

```python
merger = FileMerger(output_dir="mes_resultats")
metadata_writer = MetadataWriter(output_dir="mes_resultats")
```

---

## 📝 Exemples d'Utilisation Avancée

### Utiliser l'API Programmatique

```python
from models.small_file import SmallFile
from core.clustering import AgglomerativeClustering
from core.merger import FileMerger
from data_io.metadata_writer import MetadataWriter

# 1. Créer des fichiers
files = [
    SmallFile("data1.csv", 15.0),
    SmallFile("data2.csv", 18.0),
    SmallFile("img.jpg", 30.0),
]

# 2. Clustering
clustering = AgglomerativeClustering(max_cluster_size_mb=128.0)
clusters = clustering.fit(files)

# 3. Fusion
merger = FileMerger(output_dir="output")
merger.merge_all_clusters(clusters)

# 4. Métadonnées
writer = MetadataWriter(output_dir="output")
writer.write_all_metadata(clusters)
```

### Générer un Scénario Personnalisé

```python
from data_io.file_generator import FileGenerator

generator = FileGenerator()

# Distribution personnalisée
distribution = {
    5: 20,   # 20 fichiers de 5 MB
    15: 10,  # 10 fichiers de 15 MB
    30: 5,   # 5 fichiers de 30 MB
}

files = generator.generate_with_distribution(distribution)
```

---

## 🧪 Tests

### Vérifier le Fonctionnement

Exécutez le programme avec l'exemple 1:
```bash
python main.py
# Choisir: 1
```

Vérifiez les fichiers dans le dossier `output/`:
- Fichiers `.bin` (fichiers fusionnés)
- Fichiers `.json` (métadonnées)
- Fichiers `.txt` (rapports)

---

## 🤝 Contribution

### Architecture du Code

Le code est organisé en modules indépendants:
- **models**: Structures de données
- **core**: Algorithmes
- **data_io**: Génération et écriture

### Ajouter une Fonctionnalité

1. Identifier le module approprié
2. Créer une nouvelle classe ou méthode
3. Documenter avec des docstrings
4. Mettre à jour le `README.md`

---

## 📚 Références

### HDFS Small Files Problem

- [Apache Hadoop Documentation](https://hadoop.apache.org/)
- [The Small Files Problem in HDFS](https://blog.cloudera.com/the-small-files-problem/)

### Clustering Hiérarchique

- Algorithme: Agglomerative Hierarchical Clustering
- Linkage: Single-linkage (nearest neighbor)
- Distance: Euclidienne (taille des fichiers)

---

## 📄 Licence

Ce projet est fourni à des fins éducatives.

---

## 👨‍💻 Auteur

Projet académique - M1 Data Science  
Date: Novembre 2025

---

## 🎓 Notes Pédagogiques

### Concepts Illustrés

1. **Programmation orientée objets**
   - Encapsulation
   - Héritage conceptuel
   - Polymorphisme

2. **Algorithmes de clustering**
   - Clustering hiérarchique
   - Matrice de distance
   - Méthodes de linkage

3. **Systèmes distribués**
   - Problème des petits fichiers
   - Optimisation du stockage
   - Gestion des métadonnées

### Points Clés

- ✅ Aucune bibliothèque externe de ML
- ✅ Implémentation complète de l'algorithme
- ✅ Code commenté et documenté
- ✅ Architecture modulaire
- ✅ Gestion propre des fichiers

---

**Bon clustering ! 🚀**
