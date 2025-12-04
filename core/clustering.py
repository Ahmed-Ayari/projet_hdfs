"""
Implémentation de l'algorithme de clustering hiérarchique agglomératif
avec single-linkage.
"""

from typing import List
from models.small_file import SmallFile
from models.cluster import Cluster
from .distance_matrix import DistanceMatrix


class AgglomerativeClustering:
    """
    Algorithme de clustering hiérarchique agglomératif.
    
    Utilise la méthode single-linkage et respecte une contrainte de taille
    maximale pour les clusters (par défaut 128 MB).
    
    Attributes:
        max_cluster_size_mb (float): Taille maximale d'un cluster en MB
        clusters (List[Cluster]): Liste finale des clusters
        distance_matrix (DistanceMatrix): Matrice de distance entre clusters
    """
    
    def __init__(self, max_cluster_size_mb: float = 128.0):
        """
        Initialise l'algorithme de clustering.
        
        Args:
            max_cluster_size_mb (float): Taille maximale autorisée pour un cluster
        """
        self.max_cluster_size_mb = max_cluster_size_mb
        self.clusters = []
        self.distance_matrix = None
        self._iteration_count = 0
    
    def fit(self, files: List[SmallFile]) -> List[Cluster]:
        """
        Exécute l'algorithme de clustering sur la liste de fichiers.
        
        Processus:
        1. Initialisation: chaque fichier = un cluster
        2. Tant qu'il existe des paires fusionnables:
            a. Trouver les deux clusters les plus proches
            b. Vérifier la contrainte de taille
            c. Si OK, fusionner et mettre à jour la matrice
            d. Sinon, marquer comme non fusionnable et continuer
        3. Retourner la liste finale de clusters
        
        Args:
            files (List[SmallFile]): Liste des fichiers à regrouper
            
        Returns:
            List[Cluster]: Liste des clusters finaux
        """
        print(f"\n{'='*60}")
        print(f"DÉMARRAGE DU CLUSTERING HIÉRARCHIQUE AGGLOMÉRATIF")
        print(f"{'='*60}")
        print(f"Nombre de fichiers: {len(files)}")
        print(f"Taille maximale par cluster: {self.max_cluster_size_mb} MB")
        print(f"Méthode de linkage: SINGLE-LINKAGE")
        
        # Étape 1: Initialisation - chaque fichier devient un cluster
        self._initialize_clusters(files)
        
        # Étape 2: Créer la matrice de distance initiale
        self.distance_matrix = DistanceMatrix(self.clusters)
        
        print(f"\nInitialisation terminée: {len(self.clusters)} clusters créés")
        
        # Étape 3: Fusionner itérativement
        self._agglomerate()
        
        print(f"\n{'='*60}")
        print(f"CLUSTERING TERMINÉ")
        print(f"{'='*60}")
        print(f"Nombre de clusters finaux: {len(self.clusters)}")
        print(f"Nombre d'itérations: {self._iteration_count}")
        
        return self.clusters
    
    def _initialize_clusters(self, files: List[SmallFile]) -> None:
        """
        Initialise les clusters: un fichier par cluster.
        
        Args:
            files (List[SmallFile]): Liste des fichiers
        """
        # Réinitialiser le compteur d'IDs pour avoir des IDs cohérents
        Cluster.reset_counter()
        
        self.clusters = []
        for file in files:
            cluster = Cluster([file])
            self.clusters.append(cluster)
    
    def _agglomerate(self) -> None:
        """
        Processus principal d'agglomération.
        
        Continue à fusionner les clusters les plus proches tant que
        la contrainte de taille est respectée.
        """
        while len(self.distance_matrix) > 1:
            # Obtenir toutes les paires triées par distance
            all_pairs = self.distance_matrix.get_all_pairs_sorted()
            
            if not all_pairs:
                break
            
            # Chercher la première paire fusionnable
            merged_something = False
            
            for i, j, distance in all_pairs:
                cluster_i = self.distance_matrix.clusters[i]
                cluster_j = self.distance_matrix.clusters[j]
                
                # Vérifier la contrainte de taille
                if cluster_i.can_merge_with(cluster_j, self.max_cluster_size_mb):
                    self._iteration_count += 1
                    
                    print(f"\n--- Itération {self._iteration_count} ---")
                    print(f"Fusion: Cluster {cluster_i.cluster_id} ({cluster_i.get_total_size():.2f} MB) "
                          f"+ Cluster {cluster_j.cluster_id} ({cluster_j.get_total_size():.2f} MB)")
                    print(f"Distance: {distance:.2f} MB")
                    
                    # Fusionner les clusters
                    self.distance_matrix.merge_clusters(i, j)
                    
                    merged = self.distance_matrix.clusters[-1]
                    print(f"→ Nouveau cluster {merged.cluster_id} créé ({merged.get_total_size():.2f} MB, "
                          f"{len(merged.files)} fichiers)")
                    print(f"Clusters restants: {len(self.distance_matrix)}")
                    
                    merged_something = True
                    break  # Sortir de la boucle for et recalculer les paires
            
            # Si aucune fusion n'a été effectuée, arrêter
            if not merged_something:
                print("\nAucune fusion supplémentaire possible avec la contrainte de taille.")
                break
        
        # Les clusters finaux sont ceux restants dans la matrice
        self.clusters = self.distance_matrix.clusters
    
    def _all_pairs_checked(self, unfusable_pairs: set) -> bool:
        """
        Vérifie si toutes les paires possibles ont été testées.
        
        Args:
            unfusable_pairs (set): Ensemble des paires non fusionnables
            
        Returns:
            bool: True si toutes les paires ont été vérifiées
        """
        n = len(self.distance_matrix)
        total_pairs = n * (n - 1) // 2
        return len(unfusable_pairs) >= total_pairs
    
    def get_clusters(self) -> List[Cluster]:
        """
        Retourne la liste des clusters finaux.
        
        Returns:
            List[Cluster]: Liste des clusters
        """
        return self.clusters
    
    def get_statistics(self) -> dict:
        """
        Retourne des statistiques sur le clustering.
        
        Returns:
            dict: Statistiques (nombre de clusters, taille moyenne, etc.)
        """
        if not self.clusters:
            return {}
        
        sizes = [c.get_total_size() for c in self.clusters]
        file_counts = [len(c) for c in self.clusters]
        
        return {
            "num_clusters": len(self.clusters),
            "total_files": sum(file_counts),
            "avg_cluster_size_mb": sum(sizes) / len(sizes),
            "min_cluster_size_mb": min(sizes),
            "max_cluster_size_mb": max(sizes),
            "avg_files_per_cluster": sum(file_counts) / len(file_counts),
            "iterations": self._iteration_count
        }
