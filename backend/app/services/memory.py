import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import openai

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEMORY_DIR = BASE_DIR / "app" / "db" / "memory"
VECTORS_PATH = MEMORY_DIR / "vectors.npz"
METADATA_PATH = MEMORY_DIR / "metadata.json"

class ChronicleService:
    """
    Temporal Memory Layer (The Chronicle).
    Provides semantic search and persistence for strategic outputs and audits.
    """
    def __init__(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self.embeddings = [] # List of np.arrays
        self.metadata = []   # List of dicts
        self._load()

    def _load(self):
        if VECTORS_PATH.exists() and METADATA_PATH.exists():
            try:
                data = np.load(VECTORS_PATH)
                self.embeddings = [data[f] for f in data.files]
                with open(METADATA_PATH, "r") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"[Chronicle] Load failed: {e}")
                self.embeddings = []
                self.metadata = []

    def _save(self):
        if not self.embeddings:
            return
        try:
            # Save vectors as named files in the npz
            vec_dict = {f"v_{i}": v for i, v in enumerate(self.embeddings)}
            np.savez(VECTORS_PATH, **vec_dict)
            with open(METADATA_PATH, "w") as f:
                json.dump(self.metadata, f)
        except Exception as e:
            print(f"[Chronicle] Save failed: {e}")

    async def add_entry(self, text: str, meta: Dict[str, Any], api_key: Optional[str] = None):
        """Generates embedding and adds an entry to the chronicle."""
        if not api_key:
            return # Cannot generate embedding without key
            
        try:
            client = openai.AsyncOpenAI(api_key=api_key)
            response = await client.embeddings.create(
                input=[text.replace("\n", " ")],
                model="text-embedding-3-small"
            )
            embedding = np.array(response.data[0].embedding)
            
            self.embeddings.append(embedding)
            self.metadata.append({
                **meta,
                "text_snippet": text[:500], # Store a snippet for quick preview
                "timestamp": str(os.path.getmtime(METADATA_PATH)) if METADATA_PATH.exists() else str(0)
            })
            self._save()
        except Exception as e:
            print(f"[Chronicle] Failed to add entry: {e}")

    def search(self, query_embedding: np.ndarray, limit: int = 5) -> List[Dict[str, Any]]:
        """Finds most similar entries using cosine similarity."""
        if not self.embeddings:
            return []
            
        similarities = []
        for i, emb in enumerate(self.embeddings):
            # Cosine similarity
            dot = np.dot(query_embedding, emb)
            norm = np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            score = dot / norm if norm > 0 else 0
            similarities.append((score, i))
            
        # Sort by score descending
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, idx in similarities[:limit]:
            results.append({
                "score": float(score),
                "metadata": self.metadata[idx]
            })
        return results

# Singleton instance
chronicle = ChronicleService()
