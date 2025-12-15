# Projet HDFS - Fusion de Petits Fichiers

## 📋 Description du Projet

Implémentation de l'algorithme de fusion de petits fichiers basé sur l'article de recherche :

> **"Merging Small Files Based on Agglomerative Hierarchical Clustering on HDFS for Cloud Storage"**  
> *Khin Su Su Wai, Julia Myint, Tin Tin Yee - University of Information Technology, Yangon, Myanmar*

### Le Problème des Petits Fichiers (Small Files Problem)

Selon l'article (Section 1):
- *"The consumption of memory in NameNode is decided by the number of files stored in HDFS"*
- *"Each file requires 150 bytes of memory space to store metadata in NameNode"*
- *"When the large number of small files is stored, HDFS is inefficient because of high memory usage"*

### La Solution Proposée

Ce programme implémente l'**Algorithm 1: Small Files Merging Algorithm** de l'article :
- Clustering hiérarchique agglomératif avec **single-linkage**
- Distance **euclidienne** basée sur la taille des fichiers
- Contrainte de taille : clusters ≤ **128 MB** (taille de bloc HDFS)

---

## 🧮 Algorithm 1 - Small Files Merging Algorithm

### Implémentation de l'article (Section 4.1)

```
Input:  Small files S = {F₁, F₂, F₃, ..., Fₙ}
Output: Cluster hierarchies C = {C₁, C₂, ..., Cₘ}

Method:
(1-5)  Pour chaque paire (Fᵢ, Fⱼ): Calculer De(Fᵢ, Fⱼ) = |size_i - size_j|
(6)    Créer la matrice de distance (C, S, De)
(7)    C = {{F} | F ∈ S}  // Chaque fichier = 1 cluster
(8)    While sizeOfEachCluster |C| < 128MB Do
(9)        {C, C'} = min De(Fᵢ, Fⱼ)  // Single-linkage
(10)       If (|C| + |C'|) ≤ 128MB Then
(11)           C = ({C} ∪ {C'})  // Fusionner
(13)       Update distance matrix (C, S, De)
(14)   End while
(15)   Return (C)
```

### Distance Euclidienne (Section 3)

Selon l'article : *"The Euclidean distance measure is used to cluster the small files"*

```
De(Fᵢ, Fⱼ) = |size_i - size_j|
```

Exemple de l'article (Section 4.2):
- d(F₁, F₂) = |40 - 10| = 30 MB
- d(F₁, F₃) = |40 - 50| = 10 MB

### Méthode Single-Linkage (Section 3)

*"The single-linkage clustering is the minimum distance between elements of each cluster"*

```
distance(Cluster_A, Cluster_B) = min{ De(Fᵢ, Fⱼ) | Fᵢ ∈ A, Fⱼ ∈ B }
```

---

## ⚙️ Configuration HDFS (Selon Article)

| Paramètre | Valeur | Référence Article |
|-----------|--------|-------------------|
| **Taille de bloc HDFS** | 128 MB | Section 1: *"Each file is split into several blocks with the size of 128MB"* |
| **Seuil petits fichiers** | 75% (96 MB) | Section 4: *"The default threshold is set to (0.75) 75% of default block size"* |
| **Métadonnées/fichier** | 150 bytes | Section 1: *"Each file requires 150 bytes of memory space"* |
| **Taille max cluster** | 128 MB | Section 4: *"The size of cluster should less than or equal to default block size"* |
| **Linkage** | Single | Section 3: *"Single-linkage clustering is the minimum distance"* |

---

## 🏗️ Structure du Projet

```
projet_hdfs/
│
├── models/                          # Modèles de données
│   ├── __init__.py
│   ├── small_file.py               # Classe SmallFile - Représente Fᵢ ∈ S
│   └── cluster.py                  # Classe Cluster - Représente Cᵢ ∈ C
│
├── core/                            # Algorithmes (Algorithm 1)
│   ├── __init__.py
│   ├── clustering.py               # AgglomerativeClustering - Lignes 1-15
│   ├── distance_matrix.py          # DistanceMatrix - De(Fᵢ, Fⱼ)
│   ├── dendrogram.py               # Dendrogram - Arbre hiérarchique
│   ├── merger.py                   # FileMerger - Fusion physique
│   ├── namenode_memory.py          # NameNodeMemory - Simulation mémoire
│   └── file_index.py               # FileIndex - Index de récupération
│
├── data_io/                         # Entrées/Sorties
│   ├── __init__.py
│   ├── file_generator.py           # Génération de fichiers de test
│   └── metadata_writer.py          # Écriture des métadonnées JSON
│
├── output/                          # Résultats (créé automatiquement)
│   ├── cluster_*.bin               # Fichiers fusionnés
│   ├── cluster_*_metadata.json     # Métadonnées par cluster
│   ├── example*_clusters.json      # Résumé des clusters
│   └── example*_report.txt         # Rapports détaillés
│
├── main.py                          # Point d'entrée du programme
├── requirements.txt                 # Dépendances Python
└── README.md                        # Ce fichier
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
venv\Scripts\activate     # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Installer les dépendances (aucune externe)
pip install -r requirements.txt
```

---

## 🚀 Utilisation

### Exécution du Programme

```bash
python main.py
```

### Menu Principal

```
Choisissez un mode d'exécution:

  1. Exemple 1: Scénario réaliste (fichiers mixtes)
  2. Exemple 2: Liste personnalisée de fichiers
  3. Exemple 3: Problème des petits fichiers
  4. Mode interactif
  5. Exécuter tous les exemples
  0. Quitter
```

### Exemple de Sortie Console

```
============================================================
DÉMARRAGE DU CLUSTERING HIÉRARCHIQUE AGGLOMÉRATIF
============================================================
Configuration HDFS (selon article):
  - Taille de bloc: 128.0 MB
  - Seuil petits fichiers: 75% = 96.0 MB
  - Taille max cluster: 128.0 MB

[ALGORITHM 1 - Lignes 1-6] Calcul de la matrice de distance euclidienne...

[Ligne 9] Single-linkage: min distance = 0.00 MB
[Ligne 10] Contrainte: 5.00 + 5.00 = 10.00 MB <= 128.0 MB
[Ligne 11] Fusion: C = (C1 ∪ C2)
-> Nouveau cluster C15 créé (10.00 MB, 2 fichiers)
[Ligne 13] Mise à jour matrice de distance
```

---

## 📊 Classes Principales

### SmallFile (models/small_file.py)

Représente un fichier Fᵢ dans l'ensemble S = {F₁, F₂, ..., Fₙ}

```python
from models.small_file import SmallFile, HDFS_BLOCK_SIZE_MB, SMALL_FILE_THRESHOLD

file = SmallFile("document.txt", 25.0)  # 25 MB
print(file.size_mb)  # 25.0
```

**Constantes définies:**
- `HDFS_BLOCK_SIZE_MB = 128.0`
- `SMALL_FILE_THRESHOLD = 0.75`
- `SMALL_FILE_MAX_SIZE_MB = 96.0`

### Cluster (models/cluster.py)

Représente un cluster Cᵢ dans l'ensemble C = {C₁, C₂, ..., Cₘ}

```python
from models.cluster import Cluster

cluster = Cluster([file1, file2])
print(cluster.get_total_size())  # Taille totale en MB
print(cluster.can_merge_with(other_cluster, max_size_mb=128.0))
```

### AgglomerativeClustering (core/clustering.py)

Implémente l'Algorithm 1 de l'article (lignes 1-15)

```python
from core.clustering import AgglomerativeClustering

clustering = AgglomerativeClustering(max_cluster_size_mb=128.0)
clusters = clustering.fit(files)  # Exécute l'Algorithm 1
clustering.print_algorithm_steps()  # Affiche le journal d'exécution
```

### DistanceMatrix (core/distance_matrix.py)

Calcule et maintient la matrice De(Fᵢ, Fⱼ)

```python
from core.distance_matrix import DistanceMatrix

matrix = DistanceMatrix(clusters)
i, j, distance = matrix.find_closest_pair()  # Ligne 9: single-linkage
matrix.merge_clusters(i, j)  # Lignes 11 et 13
```

### Dendrogram (core/dendrogram.py)

Construit l'arbre hiérarchique des fusions

```python
clustering.dendrogram.print_tree()
clustering.dendrogram.print_merge_history()
```

### NameNodeMemory (core/namenode_memory.py)

Simule la consommation mémoire du NameNode (150 bytes/entrée)

```python
from core.namenode_memory import NameNodeMemory

namenode = NameNodeMemory()
report = namenode.get_detailed_report(files, clusters)
print(report)
```

**Exemple de sortie (selon article Section 5):**
```
ANALYSE MÉMOIRE NAMENODE
  Fichiers originaux: 15 → 2250 bytes
  Clusters fusionnés: 3 → 450 bytes
  Économie: 1800 bytes (80.00%)
```

### FileIndex (core/file_index.py)

Index pour récupérer les fichiers depuis les clusters fusionnés

```python
from core.file_index import FileIndex

index = FileIndex()
index.build_index(clusters)
location = index.get_file_location("document.txt")
# Retourne: (cluster_id, offset, size)
```

---

## 📤 Fichiers de Sortie

### Fichiers Fusionnés (*.bin)

Fichiers binaires contenant les données fusionnées de chaque cluster.

### Métadonnées JSON

**`example1_clusters.json`:**
```json
{
  "total_clusters": 3,
  "clusters": [
    {
      "cluster_id": 24,
      "files": ["file_0001.dat", "file_0003.dat", "file_0005.dat"],
      "file_count": 3,
      "size_total_mb": 96.5
    }
  ],
  "summary": {
    "total_files": 15,
    "total_size_mb": 294.8,
    "memory_reduction_percent": 80.0
  }
}
```

### Rapports Détaillés

**`example1_report.txt`:**
```
================================================================================
RAPPORT DE FUSION DE FICHIERS HDFS
================================================================================

Configuration (selon article):
  - Taille de bloc HDFS: 128 MB
  - Seuil petits fichiers: 75% = 96 MB
  - Métadonnées par entrée: 150 bytes

Résultats:
  - Fichiers originaux: 15
  - Clusters créés: 3
  - Réduction mémoire: 80.00%
```

---

## 📈 Évaluation (Section 5 de l'article)

### Comparaison Mémoire NameNode

| Scénario | Fichiers | Original HDFS | Proposed Approach | Réduction |
|----------|----------|---------------|-------------------|-----------|
| Exemple 1 | 6 fichiers | 900 bytes | 300 bytes (2 clusters) | 66.7% |
| Exemple 2 | 8 fichiers | 1200 bytes | 450 bytes (3 clusters) | 62.5% |
| Exemple 3 | 11 fichiers | 1650 bytes | 150 bytes (1 cluster) | 90.9% |

*Valeurs tirées de l'article - Figure 3: NameNode Memory Consumption*

-----

## 🧪 Tests

### Exécuter l'Exemple 1

```bash
python main.py
# Choisir: 1
```

### Vérifier les Résultats

```bash
# Fichiers créés dans output/
ls output/
# cluster_*.bin, cluster_*_metadata.json, example1_*.json, example1_*.txt
```

---

## 📚 Références

### Article de Recherche

> Khin Su Su Wai, Julia Myint, Tin Tin Yee. "Merging Small Files Based on Agglomerative Hierarchical Clustering on HDFS for Cloud Storage". University of Information Technology, Yangon, Myanmar.

### Concepts Clés

- **HDFS**: Hadoop Distributed File System
- **NameNode**: Gestionnaire de métadonnées HDFS
- **Small Files Problem**: Surcharge mémoire due aux nombreux petits fichiers
- **Agglomerative Clustering**: Clustering bottom-up
- **Single-Linkage**: Distance = minimum entre éléments

---

## 👨‍💻 Auteur

Projet académique - M1 Data Science  
Décembre 2025

---

**Bon clustering ! 🚀**
