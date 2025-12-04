"""
Classe représentant un cluster de fichiers.
"""

from typing import List
from .small_file import SmallFile


class Cluster:
    """
    Représente un cluster contenant un ou plusieurs fichiers.
    
    Un cluster est créé lors du processus de fusion et contient
    l'ensemble des fichiers regroupés ensemble.
    
    Attributes:
        cluster_id (int): Identifiant unique du cluster
        files (List[SmallFile]): Liste des fichiers dans le cluster
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
        Fusionne ce cluster avec un autre cluster.
        
        Args:
            other (Cluster): L'autre cluster à fusionner
            
        Returns:
            Cluster: Un nouveau cluster contenant tous les fichiers
        """
        new_cluster = Cluster()
        new_cluster.files = self.files + other.files
        return new_cluster
    
    def can_merge_with(self, other: 'Cluster', max_size_mb: float = 128.0) -> bool:
        """
        Vérifie si ce cluster peut fusionner avec un autre sans dépasser la limite.
        
        Args:
            other (Cluster): L'autre cluster
            max_size_mb (float): Taille maximale autorisée en MB (par défaut 128 MB)
            
        Returns:
            bool: True si la fusion est possible, False sinon
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
