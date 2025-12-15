"""
Module core - Contient les algorithmes de clustering et de fusion.
"""

from .distance_matrix import DistanceMatrix
from .clustering import AgglomerativeClustering
from .merger import FileMerger
from .namenode_memory import NameNodeMemory, METADATA_BYTES_PER_FILE
from .file_index import FileIndex
from .dendrogram import Dendrogram, MergeNode

__all__ = [
    'DistanceMatrix', 
    'AgglomerativeClustering', 
    'FileMerger',
    'NameNodeMemory',
    'METADATA_BYTES_PER_FILE',
    'FileIndex',
    'Dendrogram',
    'MergeNode'
]
