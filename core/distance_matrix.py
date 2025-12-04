"""
Classe pour calculer et gérer la matrice de distance euclidienne entre fichiers.
"""

from typing import List
from models.cluster import Cluster


class DistanceMatrix:
    """
    Calcule et maintient la matrice de distance entre clusters.
    
    La distance entre deux clusters est calculée uniquement sur la base
    de la taille des fichiers qu'ils contiennent.
    
    Attributes:
        clusters (List[Cluster]): Liste des clusters actifs
        matrix (List[List[float]]): Matrice de distance symétrique
    """
    
    def __init__(self, clusters: List[Cluster]):
        """
        Initialise la matrice de distance.
        
        Args:
            clusters (List[Cluster]): Liste initiale de clusters
        """
        self.clusters = clusters
        self.matrix = []
        self._compute_matrix()
    
    def _compute_matrix(self) -> None:
        """
        Calcule la matrice de distance complète.
        
        Pour chaque paire de clusters, calcule la distance euclidienne
        basée sur la taille totale de chaque cluster.
        """
        n = len(self.clusters)
        self.matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                # Distance euclidienne basée sur la taille
                size_i = self.clusters[i].get_total_size()
                size_j = self.clusters[j].get_total_size()
                distance = abs(size_i - size_j)
                
                # Matrice symétrique
                self.matrix[i][j] = distance
                self.matrix[j][i] = distance
    
    def find_closest_pair(self) -> tuple:
        """
        Trouve la paire de clusters la plus proche.
        
        Returns:
            tuple: (index_i, index_j, distance) où i < j
                   Retourne (None, None, float('inf')) si moins de 2 clusters
        """
        if len(self.clusters) < 2:
            return None, None, float('inf')
        
        min_distance = float('inf')
        min_i, min_j = 0, 1
        
        n = len(self.clusters)
        for i in range(n):
            for j in range(i + 1, n):
                if self.matrix[i][j] < min_distance:
                    min_distance = self.matrix[i][j]
                    min_i, min_j = i, j
        
        return min_i, min_j, min_distance
    
    def get_all_pairs_sorted(self) -> list:
        """
        Retourne toutes les paires de clusters triées par distance.
        
        Returns:
            list: Liste de tuples (index_i, index_j, distance) triée par distance
        """
        pairs = []
        n = len(self.clusters)
        
        for i in range(n):
            for j in range(i + 1, n):
                pairs.append((i, j, self.matrix[i][j]))
        
        # Trier par distance croissante
        pairs.sort(key=lambda x: x[2])
        
        return pairs
    
    def merge_clusters(self, i: int, j: int) -> None:
        """
        Fusionne deux clusters et met à jour la matrice.
        
        Utilise la méthode single-linkage: la distance entre le nouveau
        cluster fusionné et les autres est le minimum des distances.
        
        Args:
            i (int): Index du premier cluster (doit être < j)
            j (int): Index du second cluster
        """
        # S'assurer que i < j pour simplifier la suppression
        if i > j:
            i, j = j, i
        
        # Créer le nouveau cluster fusionné
        merged_cluster = self.clusters[i].merge_with(self.clusters[j])
        
        # Calculer les nouvelles distances (single-linkage)
        new_distances = []
        n = len(self.clusters)
        
        for k in range(n):
            if k == i or k == j:
                new_distances.append(0.0)
            else:
                # Single-linkage: minimum des distances
                dist = min(self.matrix[i][k], self.matrix[j][k])
                new_distances.append(dist)
        
        # Supprimer les anciens clusters (supprimer j d'abord car j > i)
        del self.clusters[j]
        del self.clusters[i]
        
        # Ajouter le nouveau cluster
        self.clusters.append(merged_cluster)
        
        # Reconstruire la matrice
        self._rebuild_matrix_after_merge(i, j, new_distances)
    
    def _rebuild_matrix_after_merge(self, i: int, j: int, new_distances: List[float]) -> None:
        """
        Reconstruit la matrice après une fusion.
        
        Args:
            i (int): Index du premier cluster fusionné
            j (int): Index du second cluster fusionné
            new_distances (List[float]): Distances du nouveau cluster aux autres
        """
        n_old = len(new_distances)
        n_new = n_old - 2 + 1  # On enlève 2 clusters, on en ajoute 1
        
        # Créer une nouvelle matrice
        new_matrix = [[0.0 for _ in range(n_new)] for _ in range(n_new)]
        
        # Copier les anciennes distances (en excluant i et j)
        old_to_new = []
        for k in range(n_old):
            if k != i and k != j:
                old_to_new.append(k)
        
        for row_idx, old_row in enumerate(old_to_new):
            for col_idx, old_col in enumerate(old_to_new):
                new_matrix[row_idx][col_idx] = self.matrix[old_row][old_col]
        
        # Ajouter les distances pour le nouveau cluster (dernière ligne/colonne)
        new_cluster_idx = n_new - 1
        for idx, k in enumerate(old_to_new):
            dist = new_distances[k]
            new_matrix[new_cluster_idx][idx] = dist
            new_matrix[idx][new_cluster_idx] = dist
        
        self.matrix = new_matrix
    
    def get_distance(self, i: int, j: int) -> float:
        """
        Retourne la distance entre deux clusters.
        
        Args:
            i (int): Index du premier cluster
            j (int): Index du second cluster
            
        Returns:
            float: Distance entre les clusters
        """
        return self.matrix[i][j]
    
    def __len__(self) -> int:
        """
        Retourne le nombre de clusters actifs.
        
        Returns:
            int: Nombre de clusters
        """
        return len(self.clusters)
    
    def __repr__(self) -> str:
        """
        Représentation textuelle de la matrice.
        
        Returns:
            str: Description de la matrice
        """
        return f"DistanceMatrix(clusters={len(self.clusters)})"
