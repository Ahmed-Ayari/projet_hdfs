"""
Modèle représentant un cluster de fichiers fusionnés.

Selon l'article (Section 4 - Algorithm 1):
- Output: "Cluster hierarchies C = {C1, C2, ..., Cm}"
- "Each cluster consists of set of small files"
- "The size of cluster should less than or equal to default block size" (128 MB)

Le clustering permet de réduire la consommation mémoire du NameNode:
- Avant: n fichiers = n * 150 bytes de métadonnées
- Après: m clusters = m * 150 bytes (où m << n)
"""

from typing import List
from .small_file import SmallFile


class Cluster:
    """
    Représente un cluster Ci dans l'ensemble C = {C1, C2, ..., Cm}.
    
    Selon l'article (Section 4.1):
    - "The small files are merged into a large file"
    - "NameNode only maintains the metadata of merged files"
    - Contrainte: |Ci| ≤ 128 MB (taille de bloc HDFS)
    
    Le dendrogramme (Section 3):
    "The small files are nested in larger cluster of files. These larger 
    clusters are joined until its size is less than the default block size."
    
    Attributes:
        cluster_id (int): Identifiant unique du cluster (C1, C2, ...)
        files (List[SmallFile]): Ensemble des fichiers {F1, F2, ...} dans le cluster
    """
    
    # Compteur statique pour générer des IDs uniques
    _id_counter = 0
    
    def __init__(self, files: List[SmallFile] = None):
        """
        Initialise un cluster.
        
        Args:
            files (List[SmallFile], optional): Liste initiale de fichiers.
                                                Par défaut, liste vide.
        """
        Cluster._id_counter += 1
        self.cluster_id = Cluster._id_counter
        self.files = files if files is not None else []
    
    def add_file(self, file: SmallFile) -> None:
        """
        Ajoute un fichier au cluster.
        
        Args:
            file (SmallFile): Le fichier à ajouter
        """
        self.files.append(file)
    
    def get_total_size(self) -> float:
        """
        Calcule la taille totale du cluster.
        
        Returns:
            float: La somme des tailles de tous les fichiers en MB
        """
        return sum(f.size_mb for f in self.files)
    
    def merge_with(self, other: 'Cluster') -> 'Cluster':
        """
        [ALGORITHM 1 - Ligne 11] Fusionne ce cluster avec un autre.
        
        Selon l'article: "C = ({C} ∪ {C'})" - Union des deux clusters.
        
        Args:
            other (Cluster): L'autre cluster C' à fusionner
            
        Returns:
            Cluster: Nouveau cluster C'' = C ∪ C'
        """
        new_cluster = Cluster()
        new_cluster.files = self.files + other.files
        return new_cluster
    
    def can_merge_with(self, other: 'Cluster', max_size_mb: float = 128.0) -> bool:
        """
        [ALGORITHM 1 - Ligne 10] Vérifie la contrainte de fusion.
        
        Selon l'article: "If (sizeOfCluster |C| + sizeOfCluster |C'|) <= 128MB Then"
        
        Args:
            other (Cluster): L'autre cluster C'
            max_size_mb (float): Taille de bloc HDFS (128 MB par défaut)
            
        Returns:
            bool: True si |C| + |C'| ≤ 128 MB, False sinon
        """
        total_size = self.get_total_size() + other.get_total_size()
        return total_size <= max_size_mb
    
    def __len__(self) -> int:
        """
        Retourne le nombre de fichiers dans le cluster.
        
        Returns:
            int: Nombre de fichiers
        """
        return len(self.files)
    
    def __repr__(self) -> str:
        """
        Représentation textuelle du cluster.
        
        Returns:
            str: Description du cluster
        """
        return f"Cluster(id={self.cluster_id}, files={len(self.files)}, size={self.get_total_size():.2f} MB)"
    
    def to_dict(self) -> dict:
        """
        Convertit le cluster en dictionnaire pour export JSON.
        
        Returns:
            dict: Dictionnaire contenant les métadonnées du cluster
        """
        return {
            "cluster_id": self.cluster_id,
            "files": [f.name for f in self.files],
            "file_count": len(self.files),
            "size_total_mb": round(self.get_total_size(), 2)
        }
    
    @staticmethod
    def reset_counter():
        """
        Réinitialise le compteur d'IDs (utile pour les tests).
        """
        Cluster._id_counter = 0
