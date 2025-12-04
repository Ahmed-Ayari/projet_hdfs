"""
Classe pour générer une liste de petits fichiers de test.
"""

import random
from typing import List
from models.small_file import SmallFile


class FileGenerator:
    """
    Génère une liste de fichiers de test avec des tailles aléatoires.
    
    Permet de simuler un ensemble de petits fichiers typiques d'un
    système HDFS nécessitant une fusion.
    
    Attributes:
        min_size_mb (float): Taille minimale d'un fichier en MB
        max_size_mb (float): Taille maximale d'un fichier en MB
        seed (int): Graine pour la génération aléatoire (reproductibilité)
    """
    
    def __init__(self, min_size_mb: float = 0.5, max_size_mb: float = 50.0, seed: int = None):
        """
        Initialise le générateur de fichiers.
        
        Args:
            min_size_mb (float): Taille minimale en MB
            max_size_mb (float): Taille maximale en MB
            seed (int): Graine aléatoire (None = aléatoire)
        """
        self.min_size_mb = min_size_mb
        self.max_size_mb = max_size_mb
        self.seed = seed
        
        if seed is not None:
            random.seed(seed)
    
    def generate(self, num_files: int, prefix: str = "file") -> List[SmallFile]:
        """
        Génère une liste de fichiers avec des tailles aléatoires.
        
        Args:
            num_files (int): Nombre de fichiers à générer
            prefix (str): Préfixe pour les noms de fichiers
            
        Returns:
            List[SmallFile]: Liste de fichiers générés
        """
        files = []
        
        for i in range(1, num_files + 1):
            # Générer une taille aléatoire
            size = random.uniform(self.min_size_mb, self.max_size_mb)
            size = round(size, 2)
            
            # Créer le nom du fichier
            name = f"{prefix}_{i:04d}.dat"
            
            # Créer le fichier
            file = SmallFile(name, size)
            files.append(file)
        
        print(f"\n{'='*60}")
        print(f"GÉNÉRATION DE FICHIERS DE TEST")
        print(f"{'='*60}")
        print(f"Nombre de fichiers générés: {num_files}")
        print(f"Taille minimale: {self.min_size_mb} MB")
        print(f"Taille maximale: {self.max_size_mb} MB")
        print(f"Taille totale: {sum(f.size_mb for f in files):.2f} MB")
        
        return files
    
    def generate_with_distribution(self, distribution: dict) -> List[SmallFile]:
        """
        Génère des fichiers selon une distribution spécifique.
        
        Args:
            distribution (dict): Dictionnaire {taille_mb: nombre_de_fichiers}
                                 Exemple: {5: 10, 15: 5, 25: 3}
                                 
        Returns:
            List[SmallFile]: Liste de fichiers générés
        """
        files = []
        file_counter = 1
        
        for size_mb, count in distribution.items():
            for _ in range(count):
                name = f"file_{file_counter:04d}.dat"
                file = SmallFile(name, size_mb)
                files.append(file)
                file_counter += 1
        
        print(f"\n{'='*60}")
        print(f"GÉNÉRATION DE FICHIERS AVEC DISTRIBUTION")
        print(f"{'='*60}")
        print(f"Distribution:")
        for size, count in distribution.items():
            print(f"  {size} MB: {count} fichiers")
        print(f"Total: {len(files)} fichiers, {sum(f.size_mb for f in files):.2f} MB")
        
        return files
    
    def generate_realistic_scenario(self, scenario: str = "mixed") -> List[SmallFile]:
        """
        Génère un scénario réaliste de fichiers.
        
        Args:
            scenario (str): Type de scénario ("mixed", "small", "medium", "large")
                           - "mixed": mélange de toutes tailles
                           - "small": surtout des petits fichiers
                           - "medium": surtout des fichiers moyens
                           - "large": surtout des gros fichiers
                           
        Returns:
            List[SmallFile]: Liste de fichiers générés
        """
        scenarios = {
            "mixed": {
                # Mélange équilibré
                5: 15,    # 15 fichiers de 5 MB
                10: 12,   # 12 fichiers de 10 MB
                20: 8,    # 8 fichiers de 20 MB
                35: 5,    # 5 fichiers de 35 MB
                45: 3     # 3 fichiers de 45 MB
            },
            "small": {
                # Beaucoup de petits fichiers
                2: 20,
                5: 15,
                8: 10,
                12: 5
            },
            "medium": {
                # Fichiers de taille moyenne
                15: 10,
                20: 10,
                25: 8,
                30: 6
            },
            "large": {
                # Fichiers plus gros
                30: 8,
                40: 6,
                50: 4
            }
        }
        
        if scenario not in scenarios:
            scenario = "mixed"
        
        return self.generate_with_distribution(scenarios[scenario])
    
    @staticmethod
    def display_files(files: List[SmallFile], max_display: int = 10) -> None:
        """
        Affiche un échantillon de fichiers.
        
        Args:
            files (List[SmallFile]): Liste de fichiers
            max_display (int): Nombre maximum de fichiers à afficher
        """
        print(f"\nÉchantillon de fichiers (affichant {min(max_display, len(files))} sur {len(files)}):")
        
        for i, file in enumerate(files[:max_display], 1):
            print(f"  {i}. {file}")
        
        if len(files) > max_display:
            print(f"  ... et {len(files) - max_display} autres fichiers")
