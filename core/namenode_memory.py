"""
Simulation de la consommation mémoire du NameNode HDFS.

Selon l'article (Section 1 - Introduction):
- "The consumption of memory in NameNode is decided by the number of files stored in HDFS"
- "Each file requires 150 bytes of memory space to store metadata in NameNode"

Selon l'article (Section 4.1 - File Merging Operation):
- "NameNode only maintains the metadata of merged files and does not save the original small files"
- "File merging reduces the length of the metadata of many small files"

Selon l'article (Section 5 - Evaluation):
- Comparaison mémoire: Original HDFS vs Proposed Approach
- Exemple: 6 fichiers = 900 bytes, 2 clusters = 300 bytes (réduction 66.7%)
"""

from typing import List
from models.cluster import Cluster
from models.small_file import SmallFile


# Constante selon l'article de recherche
METADATA_BYTES_PER_FILE = 150


class NameNodeMemory:
    """
    Simule et compare la consommation mémoire du NameNode HDFS.
    
    Selon l'article (Section 5 - Evaluation, Figure 3):
    - Original HDFS: n fichiers × 150 bytes
    - Proposed Approach: m clusters × 150 bytes (m << n)
    
    Exemples de l'article:
    - 6 fichiers: Original = 900 bytes, Proposé = 300 bytes (2 clusters)
    - 8 fichiers: Original = 1200 bytes, Proposé = 450 bytes (3 clusters)
    - 11 fichiers: Original = 1650 bytes, Proposé = 150 bytes (1 cluster)
    
    Attributes:
        metadata_size_bytes (int): Taille métadonnées/entrée (150 bytes)
    """
    
    def __init__(self, metadata_size_bytes: int = METADATA_BYTES_PER_FILE):
        """
        Initialise le simulateur de mémoire NameNode.
        
        Args:
            metadata_size_bytes (int): Taille des métadonnées en bytes (défaut: 150)
        """
        self.metadata_size_bytes = metadata_size_bytes
    
    def calculate_original_memory(self, files: List[SmallFile]) -> int:
        """
        Calcule la mémoire requise AVANT fusion (système HDFS original).
        
        Args:
            files (List[SmallFile]): Liste des fichiers originaux
            
        Returns:
            int: Mémoire totale en bytes
        """
        return len(files) * self.metadata_size_bytes
    
    def calculate_merged_memory(self, clusters: List[Cluster]) -> int:
        """
        Calcule la mémoire requise APRÈS fusion (système proposé).
        
        Selon l'article: "NameNode only maintains the metadata of merged files 
        and does not save the original small files"
        
        Args:
            clusters (List[Cluster]): Liste des clusters fusionnés
            
        Returns:
            int: Mémoire totale en bytes
        """
        return len(clusters) * self.metadata_size_bytes
    
    def calculate_memory_reduction(self, original_files_count: int, 
                                   clusters_count: int) -> dict:
        """
        Calcule la réduction de mémoire entre système original et proposé.
        
        Args:
            original_files_count (int): Nombre de fichiers originaux
            clusters_count (int): Nombre de clusters après fusion
            
        Returns:
            dict: Statistiques de réduction mémoire
        """
        original_memory = original_files_count * self.metadata_size_bytes
        merged_memory = clusters_count * self.metadata_size_bytes
        memory_saved = original_memory - merged_memory
        reduction_percentage = (memory_saved / original_memory * 100) if original_memory > 0 else 0
        
        return {
            "original_files": original_files_count,
            "merged_clusters": clusters_count,
            "original_memory_bytes": original_memory,
            "merged_memory_bytes": merged_memory,
            "memory_saved_bytes": memory_saved,
            "reduction_percentage": round(reduction_percentage, 2),
            "metadata_size_per_entry": self.metadata_size_bytes
        }
    
    def get_detailed_report(self, files: List[SmallFile], 
                           clusters: List[Cluster]) -> str:
        """
        Génère un rapport détaillé de la consommation mémoire.
        
        Args:
            files (List[SmallFile]): Liste des fichiers originaux
            clusters (List[Cluster]): Liste des clusters fusionnés
            
        Returns:
            str: Rapport formaté
        """
        stats = self.calculate_memory_reduction(len(files), len(clusters))
        
        report = f"""
{'='*70}
NAMENODE MEMORY CONSUMPTION ANALYSIS (selon article de recherche)
{'='*70}

Configuration:
  Métadonnées par entrée: {self.metadata_size_bytes} bytes

Système HDFS Original:
  Nombre de fichiers: {stats['original_files']}
  Mémoire requise: {stats['original_memory_bytes']} bytes
  Formule: {stats['original_files']} fichiers × {self.metadata_size_bytes} bytes

Système Proposé (Après Fusion):
  Nombre de clusters: {stats['merged_clusters']}
  Mémoire requise: {stats['merged_memory_bytes']} bytes
  Formule: {stats['merged_clusters']} clusters × {self.metadata_size_bytes} bytes

Réduction:
  Mémoire économisée: {stats['memory_saved_bytes']} bytes
  Pourcentage de réduction: {stats['reduction_percentage']}%
  
{'='*70}
"""
        return report
    
    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """
        Formate les bytes en unités lisibles.
        
        Args:
            bytes_value (int): Valeur en bytes
            
        Returns:
            str: Valeur formatée (bytes, KB, MB)
        """
        if bytes_value < 1024:
            return f"{bytes_value} bytes"
        elif bytes_value < 1024 * 1024:
            return f"{bytes_value / 1024:.2f} KB"
        else:
            return f"{bytes_value / (1024 * 1024):.2f} MB"
