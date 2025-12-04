"""
Module core - Contient les algorithmes de clustering et de fusion.
"""

from .distance_matrix import DistanceMatrix
from .clustering import AgglomerativeClustering
from .merger import FileMerger

__all__ = ['DistanceMatrix', 'AgglomerativeClustering', 'FileMerger']
