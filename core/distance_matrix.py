"""
Matrice de distance euclidienne pour le clustering hiérarchique.

Selon l'article (Section 3 - Background Theory):
- "The Euclidean distance measure is used to cluster the small files"
- "Only the half of the matrix is needed because the distance between objects is symmetric"
- Formule: d(i,j) = |x_ip - x_jp| où x est la taille du fichier
"""

from typing import List
from models.cluster import Cluster


class DistanceMatrix:
    """
    Calcule et maintient la matrice de distance De(Fi, Fj) entre clusters.
    
    Selon l'article (Section 4 - Algorithm 1, Lignes 1-6):
    - [Lignes 1-5] "Calculate Euclidean distance matrix between small files De(Fi, Fj)"
    - [Ligne 6] "Create distance matrix (C, S, De)"
    
    La distance est basée sur la différence de taille entre clusters:
    De(Ci, Cj) = |size(Ci) - size(Cj)|
    
    Attributes:
        clusters (List[Cluster]): Liste des clusters actifs C = {C1, C2, ..., Cm}
        matrix (List[List[float]]): Matrice de distance symétrique De
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
        [ALGORITHM 1 - Lignes 1-5] Calcule la matrice de distance euclidienne.
        
        Selon l'article (Section 3):
        "The Euclidean distance measure is: d(i,j) = sqrt(sum((x_ip - x_jp)^2))"
        
        Pour le cas unidimensionnel (taille uniquement):
        De(Ci, Cj) = |size(Ci) - size(Cj)|
        
        Exemple de l'article (Section 4.2):
        - d(1,2) = |40 - 10| = 30
        - d(1,3) = |40 - 50| = 10
        """
        n = len(self.clusters)
        self.matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                # Distance euclidienne: De(Ci, Cj) = |size(Ci) - size(Cj)|
                size_i = self.clusters[i].get_total_size()
                size_j = self.clusters[j].get_total_size()
                distance = abs(size_i - size_j)
                
                # Matrice symétrique: d(i,j) = d(j,i)
                self.matrix[i][j] = distance
                self.matrix[j][i] = distance
    
    def find_closest_pair(self) -> tuple:
        """
        [ALGORITHM 1 - Ligne 9] Trouve la paire de clusters la plus proche.
        
        Selon l'article: "{C, C'} = min De(Fi, Fj) {Ci, Cj} ∈ C: Ci ≠ Cj"
        Sélection par single-linkage: "minimum distance between elements".
        
        Returns:
            tuple: (index_i, index_j, distance) où i < j
                   Retourne (None, None, inf) si moins de 2 clusters
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
        [ALGORITHM 1 - Lignes 11 et 13] Fusionne deux clusters et met à jour la matrice.
        
        Selon l'article:
        - [Ligne 11] "C = ({C} ∪ {C'})" - Fusion des clusters
        - [Ligne 13] "Update distance matrix (C, S, De)" - Mise à jour
        
        Méthode Single-Linkage (Section 3):
        "The single-linkage clustering is the minimum distance between elements"
        La nouvelle distance = min(De(Ci, Ck), De(Cj, Ck)) pour tout k.
        
        Args:
            i (int): Index du premier cluster Ci
            j (int): Index du second cluster Cj
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
    
    def print_matrix(self) -> None:
        """
        Affiche la matrice de distance selon le format de l'article.
        
        Selon l'article: "Only the half of the matrix is needed because 
        the distance between objects is symmetric"
        """
        n = len(self.clusters)
        
        if n == 0:
            print("Matrice vide")
            return
        
        # En-tête
        print("\n" + " " * 12, end="")
        for j in range(n):
            print(f"C{self.clusters[j].cluster_id:5d}", end="")
        print()
        
        # Lignes de la matrice (demi-matrice supérieure)
        for i in range(n):
            print(f"Cluster {self.clusters[i].cluster_id:3d} |", end="")
            for j in range(n):
                if i == j:
                    print("    - ", end="")
                elif j < i:
                    print("      ", end="")  # Partie inférieure (symétrique)
                else:
                    print(f"{self.matrix[i][j]:5.1f} ", end="")
            
            # Afficher la taille du cluster
            size = self.clusters[i].get_total_size()
            print(f"| ({size:.1f} MB)")
        
        print()
