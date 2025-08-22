"""
Vector Loading and Unloading Operations

This module provides functions to load and unload vectors from various sources
including files, memory, and different data formats.
"""

import numpy as np
import pickle
import json
from typing import List, Union, Optional, Any
import os


class VectorManager:
    """A class to manage vector loading and unloading operations."""
    
    def __init__(self):
        self.loaded_vectors = {}
        self.vector_counter = 0
    
    def load_vector_from_list(self, data: List[float], name: Optional[str] = None) -> str:
        """
        Load a vector from a Python list.
        
        Args:
            data: List of numerical values
            name: Optional name for the vector
            
        Returns:
            str: Unique identifier for the loaded vector
        """
        if name is None:
            name = f"vector_{self.vector_counter}"
            self.vector_counter += 1
        
        vector = np.array(data, dtype=np.float64)
        self.loaded_vectors[name] = vector
        print(f"Loaded vector '{name}' with shape {vector.shape}")
        return name
    
    def load_vector_from_file(self, filepath: str, format_type: str = "npy", name: Optional[str] = None) -> str:
        """
        Load a vector from a file.
        
        Args:
            filepath: Path to the vector file
            format_type: File format ('npy', 'txt', 'csv', 'json', 'pickle')
            name: Optional name for the vector
            
        Returns:
            str: Unique identifier for the loaded vector
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if name is None:
            name = os.path.splitext(os.path.basename(filepath))[0]
        
        try:
            if format_type.lower() == "npy":
                vector = np.load(filepath)
            elif format_type.lower() in ["txt", "csv"]:
                vector = np.loadtxt(filepath)
            elif format_type.lower() == "json":
                with open(filepath, 'r') as f:
                    data = json.load(f)
                vector = np.array(data, dtype=np.float64)
            elif format_type.lower() == "pickle":
                with open(filepath, 'rb') as f:
                    vector = pickle.load(f)
                if not isinstance(vector, np.ndarray):
                    vector = np.array(vector, dtype=np.float64)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            self.loaded_vectors[name] = vector
            print(f"Loaded vector '{name}' from {filepath} with shape {vector.shape}")
            return name
            
        except Exception as e:
            raise RuntimeError(f"Failed to load vector from {filepath}: {str(e)}")
    
    def load_vector_from_numpy(self, array: np.ndarray, name: Optional[str] = None) -> str:
        """
        Load a vector from a numpy array.
        
        Args:
            array: NumPy array
            name: Optional name for the vector
            
        Returns:
            str: Unique identifier for the loaded vector
        """
        if name is None:
            name = f"numpy_vector_{self.vector_counter}"
            self.vector_counter += 1
        
        vector = array.copy()
        self.loaded_vectors[name] = vector
        print(f"Loaded vector '{name}' with shape {vector.shape}")
        return name
    
    def unload_vector(self, name: str) -> bool:
        """
        Unload a vector from memory.
        
        Args:
            name: Name of the vector to unload
            
        Returns:
            bool: True if successfully unloaded, False otherwise
        """
        if name in self.loaded_vectors:
            del self.loaded_vectors[name]
            print(f"Unloaded vector '{name}'")
            return True
        else:
            print(f"Vector '{name}' not found in loaded vectors")
            return False
    
    def unload_all_vectors(self) -> int:
        """
        Unload all vectors from memory.
        
        Returns:
            int: Number of vectors unloaded
        """
        count = len(self.loaded_vectors)
        self.loaded_vectors.clear()
        print(f"Unloaded {count} vectors")
        return count
    
    def save_vector_to_file(self, name: str, filepath: str, format_type: str = "npy") -> bool:
        """
        Save a loaded vector to a file (unload to file).
        
        Args:
            name: Name of the vector to save
            filepath: Output file path
            format_type: File format ('npy', 'txt', 'csv', 'json', 'pickle')
            
        Returns:
            bool: True if successfully saved, False otherwise
        """
        if name not in self.loaded_vectors:
            print(f"Vector '{name}' not found in loaded vectors")
            return False
        
        vector = self.loaded_vectors[name]
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            if format_type.lower() == "npy":
                np.save(filepath, vector)
            elif format_type.lower() in ["txt", "csv"]:
                np.savetxt(filepath, vector)
            elif format_type.lower() == "json":
                with open(filepath, 'w') as f:
                    json.dump(vector.tolist(), f)
            elif format_type.lower() == "pickle":
                with open(filepath, 'wb') as f:
                    pickle.dump(vector, f)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            print(f"Saved vector '{name}' to {filepath}")
            return True
            
        except Exception as e:
            print(f"Failed to save vector '{name}' to {filepath}: {str(e)}")
            return False
    
    def get_vector(self, name: str) -> Optional[np.ndarray]:
        """
        Get a loaded vector by name.
        
        Args:
            name: Name of the vector
            
        Returns:
            numpy.ndarray or None: The vector if found, None otherwise
        """
        return self.loaded_vectors.get(name)
    
    def list_loaded_vectors(self) -> List[str]:
        """
        Get a list of all loaded vector names.
        
        Returns:
            List[str]: List of vector names
        """
        return list(self.loaded_vectors.keys())
    
    def get_vector_info(self, name: str) -> Optional[dict]:
        """
        Get information about a loaded vector.
        
        Args:
            name: Name of the vector
            
        Returns:
            dict or None: Vector information if found, None otherwise
        """
        if name in self.loaded_vectors:
            vector = self.loaded_vectors[name]
            return {
                "name": name,
                "shape": vector.shape,
                "dtype": str(vector.dtype),
                "size": vector.size,
                "memory_usage_bytes": vector.nbytes
            }
        return None
    
    def get_memory_usage(self) -> dict:
        """
        Get total memory usage of all loaded vectors.
        
        Returns:
            dict: Memory usage information
        """
        total_bytes = sum(v.nbytes for v in self.loaded_vectors.values())
        return {
            "total_vectors": len(self.loaded_vectors),
            "total_memory_bytes": total_bytes,
            "total_memory_mb": total_bytes / (1024 * 1024)
        }


# Example usage and demonstration
def demo_vector_operations():
    """Demonstrate the vector loading and unloading capabilities."""
    print("=== Vector Operations Demo ===\n")
    
    # Create a vector manager
    vm = VectorManager()
    
    # Load vectors from different sources
    print("1. Loading vectors from various sources:")
    
    # Load from list
    sample_data = [1.0, 2.0, 3.0, 4.0, 5.0]
    vec1_id = vm.load_vector_from_list(sample_data, "sample_vector")
    
    # Load from numpy array
    random_array = np.random.rand(10)
    vec2_id = vm.load_vector_from_numpy(random_array, "random_vector")
    
    # Create and save a vector to file, then load it back
    test_vector = np.array([10, 20, 30, 40, 50])
    np.save("temp_vector.npy", test_vector)
    vec3_id = vm.load_vector_from_file("temp_vector.npy", "npy", "file_vector")
    
    print(f"\n2. Loaded vectors: {vm.list_loaded_vectors()}")
    
    # Get vector information
    print("\n3. Vector information:")
    for vec_name in vm.list_loaded_vectors():
        info = vm.get_vector_info(vec_name)
        print(f"   {vec_name}: {info}")
    
    # Show memory usage
    print(f"\n4. Memory usage: {vm.get_memory_usage()}")
    
    # Save a vector to file (unload to file)
    print("\n5. Saving vector to file:")
    vm.save_vector_to_file("sample_vector", "output_vector.npy", "npy")
    vm.save_vector_to_file("random_vector", "random_vector.json", "json")
    
    # Unload specific vectors
    print("\n6. Unloading vectors:")
    vm.unload_vector("sample_vector")
    print(f"   Remaining vectors: {vm.list_loaded_vectors()}")
    
    # Unload all vectors
    print("\n7. Unloading all vectors:")
    vm.unload_all_vectors()
    print(f"   Remaining vectors: {vm.list_loaded_vectors()}")
    
    # Clean up temporary files
    try:
        os.remove("temp_vector.npy")
        os.remove("output_vector.npy")
        os.remove("random_vector.json")
        print("\n8. Cleaned up temporary files")
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    demo_vector_operations()
