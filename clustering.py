import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm.auto import tqdm
from pathlib import Path
import pickle
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from matplotlib.colors import LinearSegmentedColormap
import umap
from typing import List, Dict, Tuple, Set

# LangChain imports
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document

# Set up constants
DOCUMENT_DIR = "path/to/your/documents"  # Update this to your documents directory
EMBEDDING_CACHE_PATH = "document_embeddings.pkl"
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200
SIMILARITY_THRESHOLD = 0.85  # Minimum similarity to consider documents as similar
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # BERT-based model

class DuplicateDetector:
    def __init__(self, document_dir: str, embedding_model: str = EMBEDDING_MODEL):
        """Initialize the duplicate detector."""
        self.document_dir = document_dir
        self.embedding_model_name = embedding_model
        self.embedding_model = None
        self.documents = []
        self.chunks = []
        self.document_embeddings = {}
        self.similarity_matrix = None
        self.document_clusters = None
        self.faiss_index = None
        
    def load_documents(self) -> List[Document]:
        """Load documents from directory."""
        print("Loading documents...")
        
        # You may need to adjust this based on your document formats
        loader = DirectoryLoader(
            self.document_dir, 
            glob="**/*.txt",  # Update pattern based on your file types
            loader_cls=TextLoader,
            recursive=True
        )
        
        # Fallback if the directory loader fails or for custom document types
        if not os.path.exists(self.document_dir):
            raise FileNotFoundError(f"Document directory {self.document_dir} not found")
            
        self.documents = loader.load()
        print(f"Loaded {len(self.documents)} documents")
        return self.documents
    
    def chunk_documents(self) -> List[Document]:
        """Split documents into smaller chunks."""
        print("Chunking documents...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        self.chunks = []
        for doc in tqdm(self.documents):
            # Store the original document name/path in the metadata
            doc_chunks = text_splitter.split_documents([doc])
            for chunk in doc_chunks:
                # Ensure we track the document source for each chunk
                if 'source' not in chunk.metadata:
                    chunk.metadata['source'] = doc.metadata.get('source', 'unknown')
            self.chunks.extend(doc_chunks)
            
        print(f"Created {len(self.chunks)} chunks from {len(self.documents)} documents")
        return self.chunks
        
    def initialize_embeddings(self):
        """Initialize the embedding model."""
        print(f"Initializing embedding model: {self.embedding_model_name}")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={'device': 'cuda' if os.environ.get('CUDA_VISIBLE_DEVICES') else 'cpu'}
        )
        
    def embed_documents(self, use_cached: bool = True) -> Dict[str, np.ndarray]:
        """Generate embeddings for all document chunks."""
        # Try to load cached embeddings if allowed
        if use_cached and os.path.exists(EMBEDDING_CACHE_PATH):
            print(f"Loading cached embeddings from {EMBEDDING_CACHE_PATH}")
            with open(EMBEDDING_CACHE_PATH, 'rb') as f:
                self.document_embeddings = pickle.load(f)
            return self.document_embeddings
        
        print("Generating document embeddings...")
        if not self.embedding_model:
            self.initialize_embeddings()
            
        # Create FAISS index for efficient similarity search
        self.faiss_index = FAISS.from_documents(self.chunks, self.embedding_model)
        
        # Extract embeddings for each document
        self.document_embeddings = {}
        for i, doc in enumerate(tqdm(self.documents)):
            # Get source path to use as unique identifier
            doc_id = doc.metadata.get('source', f"doc_{i}")
            
            # Find chunks belonging to this document
            doc_chunks = [c for c in self.chunks if c.metadata.get('source') == doc_id]
            
            if not doc_chunks:
                print(f"Warning: No chunks found for document {doc_id}")
                continue
                
            # Get embeddings for all chunks
            chunk_texts = [chunk.page_content for chunk in doc_chunks]
            chunk_embeddings = self.embedding_model.embed_documents(chunk_texts)
            
            # Average the chunk embeddings to get a document-level embedding
            doc_embedding = np.mean(chunk_embeddings, axis=0)
            self.document_embeddings[doc_id] = doc_embedding
            
        # Cache the embeddings
        with open(EMBEDDING_CACHE_PATH, 'wb') as f:
            pickle.dump(self.document_embeddings, f)
            
        print(f"Generated embeddings for {len(self.document_embeddings)} documents")
        return self.document_embeddings
    
    def compute_similarity_matrix(self) -> np.ndarray:
        """Compute pairwise similarity matrix between documents."""
        print("Computing similarity matrix...")
        doc_ids = list(self.document_embeddings.keys())
        embeddings = np.array(list(self.document_embeddings.values()))
        
        # Compute cosine similarity
        self.similarity_matrix = cosine_similarity(embeddings)
        
        # Set diagonal to 0 to ignore self-similarity
        np.fill_diagonal(self.similarity_matrix, 0)
        
        print(f"Computed {self.similarity_matrix.shape[0]}x{self.similarity_matrix.shape[1]} similarity matrix")
        return self.similarity_matrix
    
    def perform_hierarchical_clustering(self, method: str = 'ward', 
                                       distance_threshold: float = 0.5) -> Dict[str, int]:
        """
        Perform hierarchical clustering on document embeddings.
        Returns a dictionary mapping document IDs to cluster labels.
        """
        print(f"Performing hierarchical clustering using {method} linkage...")
        doc_ids = list(self.document_embeddings.keys())
        embeddings = np.array(list(self.document_embeddings.values()))
        
        # Compute the linkage matrix
        Z = linkage(embeddings, method=method)
        
        # Form flat clusters from the hierarchical clustering
        labels = fcluster(Z, t=distance_threshold, criterion='distance')
        
        # Map document IDs to their cluster labels
        self.document_clusters = {doc_id: label for doc_id, label in zip(doc_ids, labels)}
        
        # Count documents per cluster
        cluster_counts = {}
        for label in labels:
            if label not in cluster_counts:
                cluster_counts[label] = 0
            cluster_counts[label] += 1
            
        print(f"Found {len(set(labels))} clusters")
        print(f"Largest cluster has {max(cluster_counts.values())} documents")
        print(f"Smallest cluster has {min(cluster_counts.values())} documents")
        
        return self.document_clusters
    
    def find_duplicate_groups(self, similarity_threshold: float = SIMILARITY_THRESHOLD) -> List[Set[str]]:
        """Find groups of similar/duplicate documents."""
        if self.similarity_matrix is None:
            self.compute_similarity_matrix()
            
        doc_ids = list(self.document_embeddings.keys())
        duplicate_groups = []
        
        # Track which documents have been processed
        processed_docs = set()
        
        for i in range(len(doc_ids)):
            if doc_ids[i] in processed_docs:
                continue
                
            # Find all documents similar to the current one
            similar_indices = np.where(self.similarity_matrix[i] >= similarity_threshold)[0]
            
            if len(similar_indices) > 0:
                similar_docs = {doc_ids[i]}  # Include the source document
                for idx in similar_indices:
                    similar_docs.add(doc_ids[idx])
                
                # Only consider as duplicates if there's more than one document
                if len(similar_docs) > 1:
                    duplicate_groups.append(similar_docs)
                    processed_docs.update(similar_docs)
                
        print(f"Found {len(duplicate_groups)} groups of potential duplicates")
        return duplicate_groups
    
    def visualize_similarity_heatmap(self, max_docs: int = 100, 
                                   output_file: str = "similarity_heatmap.png"):
        """
        Visualize the similarity matrix as a heatmap.
        Limits to max_docs to avoid creating huge visualizations.
        """
        if self.similarity_matrix is None:
            self.compute_similarity_matrix()
            
        doc_ids = list(self.document_embeddings.keys())
        
        # Limit to a reasonable number of documents for visualization
        if len(doc_ids) > max_docs:
            print(f"Limiting heatmap to first {max_docs} documents")
            doc_ids = doc_ids[:max_docs]
            similarity_subset = self.similarity_matrix[:max_docs, :max_docs]
        else:
            similarity_subset = self.similarity_matrix
        
        # Create short labels for documents
        short_labels = [os.path.basename(doc_id) if isinstance(doc_id, str) else f"Doc {doc_id}" 
                      for doc_id in doc_ids]
        
        # Create custom colormap - from white to blue
        colors = [(1, 1, 1), (0, 0, 1)]  # White to blue
        cmap = LinearSegmentedColormap.from_list('custom_cmap', colors, N=100)
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(similarity_subset, xticklabels=short_labels, yticklabels=short_labels, 
                   cmap=cmap, vmin=0, vmax=1)
        plt.title('Document Similarity Heatmap')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300)
        plt.close()
        print(f"Saved similarity heatmap to {output_file}")
        
    def visualize_document_clusters(self, output_file: str = "document_clusters.png"):
        """Visualize document clusters using UMAP for dimensionality reduction."""
        if not self.document_clusters:
            self.perform_hierarchical_clustering()
            
        doc_ids = list(self.document_embeddings.keys())
        embeddings = np.array(list(self.document_embeddings.values()))
        
        # Use UMAP for dimensionality reduction to 2D
        reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
        embedding_2d = reducer.fit_transform(embeddings)
        
        # Get cluster labels
        labels = [self.document_clusters[doc_id] for doc_id in doc_ids]
        
        # Create plot
        plt.figure(figsize=(12, 10))
        scatter = plt.scatter(embedding_2d[:, 0], embedding_2d[:, 1], 
                             c=labels, cmap='tab20', alpha=0.6, s=50)
        
        # Add legend for clusters with more than 3 documents
        cluster_counts = {}
        for label in labels:
            if label not in cluster_counts:
                cluster_counts[label] = 0
            cluster_counts[label] += 1
            
        # Only show major clusters in legend to avoid overcrowding
        major_clusters = [c for c, count in cluster_counts.items() if count > 3]
        if major_clusters:
            handles, _ = scatter.legend_elements()
            legend_labels = [f"Cluster {i}" for i in major_clusters]
            plt.legend(handles=handles[:len(major_clusters)], labels=legend_labels, 
                      title="Major Clusters", bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.title('Document Clusters Visualization')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300)
        plt.close()
        print(f"Saved cluster visualization to {output_file}")
        
    def visualize_duplicate_network(self, similarity_threshold: float = SIMILARITY_THRESHOLD, 
                                  output_file: str = "duplicate_network.png"):
        """Visualize duplicate documents as a network graph."""
        if self.similarity_matrix is None:
            self.compute_similarity_matrix()
            
        doc_ids = list(self.document_embeddings.keys())
        
        # Create a graph
        G = nx.Graph()
        
        # Add nodes
        for doc_id in doc_ids:
            short_name = os.path.basename(doc_id) if isinstance(doc_id, str) else f"Doc {doc_id}"
            G.add_node(doc_id, label=short_name)
        
        # Add edges for similar documents
        for i in range(len(doc_ids)):
            for j in range(i+1, len(doc_ids)):
                similarity = self.similarity_matrix[i, j]
                if similarity >= similarity_threshold:
                    G.add_edge(doc_ids[i], doc_ids[j], weight=similarity)
        
        # Remove isolated nodes (no connections)
        G.remove_nodes_from(list(nx.isolates(G)))
        
        if len(G.nodes) == 0:
            print("No connections found above threshold. Try lowering the similarity threshold.")
            return
            
        print(f"Network has {len(G.nodes)} nodes and {len(G.edges)} edges")
        
        # Set up visualization parameters
        plt.figure(figsize=(15, 15))
        
        # Use force-directed layout
        pos = nx.spring_layout(G, k=0.2, iterations=50, seed=42)
        
        # Get edge weights for width and color
        edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
        
        # Draw the network
        nx.draw_networkx_nodes(G, pos, node_size=100, alpha=0.7)
        nx.draw_networkx_edges(G, pos, width=[w*3 for w in edge_weights], 
                              edge_color=edge_weights, edge_cmap=plt.cm.Blues, alpha=0.6)
        
        # Add minimal labels to avoid overcrowding
        if len(G.nodes) <= 50:  # Only label if not too many nodes
            labels = {node: G.nodes[node]['label'] for node in G.nodes}
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
        
        plt.title('Document Similarity Network (Potential Duplicates)')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300)
        plt.close()
        print(f"Saved network visualization to {output_file}")
        
    def save_results_to_excel(self, output_file: str = "duplicate_analysis.xlsx"):
        """Save the analysis results to an Excel file."""
        # Prepare data for document clusters
        if self.document_clusters:
            cluster_data = []
            for doc_id, cluster in self.document_clusters.items():
                short_name = os.path.basename(doc_id) if isinstance(doc_id, str) else f"Doc {doc_id}"
                cluster_data.append({
                    'Document ID': doc_id,
                    'Document Name': short_name,
                    'Cluster': cluster
                })
            cluster_df = pd.DataFrame(cluster_data)
            
            # Identify duplicate groups
            duplicate_groups = self.find_duplicate_groups()
            duplicate_data = []
            
            for i, group in enumerate(duplicate_groups):
                for doc_id in group:
                    short_name = os.path.basename(doc_id) if isinstance(doc_id, str) else f"Doc {doc_id}"
                    duplicate_data.append({
                        'Document ID': doc_id,
                        'Document Name': short_name,
                        'Duplicate Group': i+1,
                        'Group Size': len(group)
                    })
            duplicate_df = pd.DataFrame(duplicate_data)
            
            # Save to Excel
            with pd.ExcelWriter(output_file) as writer:
                cluster_df.to_excel(writer, sheet_name='Document Clusters', index=False)
                duplicate_df.to_excel(writer, sheet_name='Duplicate Groups', index=False)
                
                # Add a summary sheet
                summary_data = {
                    'Metric': [
                        'Total Documents',
                        'Documents with Duplicates',
                        'Duplicate Groups',
                        'Total Clusters',
                        'Largest Cluster Size',
                        'Similarity Threshold'
                    ],
                    'Value': [
                        len(self.documents),
                        len(set(duplicate_df['Document ID'])) if not duplicate_df.empty else 0,
                        duplicate_df['Duplicate Group'].nunique() if not duplicate_df.empty else 0,
                        cluster_df['Cluster'].nunique() if not cluster_df.empty else 0,
                        cluster_df.groupby('Cluster').size().max() if not cluster_df.empty else 0,
                        SIMILARITY_THRESHOLD
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
            print(f"Saved analysis results to {output_file}")
        else:
            print("No clustering results available. Run perform_hierarchical_clustering() first.")

    def analyze_duplicate_content(self):
        """Analyze what content is being duplicated across documents."""
        duplicate_groups = self.find_duplicate_groups()
        
        if not duplicate_groups:
            print("No duplicate groups found.")
            return
            
        # For each duplicate group, analyze the shared content
        for i, group in enumerate(duplicate_groups[:5]):  # Limit to first 5 groups
            print(f"\nAnalyzing duplicate group {i+1} with {len(group)} documents")
            
            # Get document paths
            doc_paths = list(group)
            doc_names = [os.path.basename(path) if isinstance(path, str) else f"Doc {path}" 
                       for path in doc_paths]
            
            print(f"Documents in this group: {', '.join(doc_names)}")
            
            # Load the content of these documents
            doc_contents = []
            for doc_id in doc_paths:
                # Find the original document
                matching_docs = [doc for doc in self.documents 
                               if doc.metadata.get('source') == doc_id]
                
                if matching_docs:
                    doc_contents.append(matching_docs[0].page_content)
                else:
                    print(f"Warning: Content not found for document {doc_id}")
            
            if len(doc_contents) < 2:
                continue
                
            # Simple analysis of common text
            # In a real implementation, you might want more sophisticated text analysis
            print("Common content analysis would go here")
            # This would require more sophisticated analysis like extracting key phrases,
            # finding common procedural steps, etc.

def main():
    detector = DuplicateDetector(DOCUMENT_DIR)
    
    # Process the documents
    detector.load_documents()
    detector.chunk_documents()
    detector.embed_documents()
    detector.compute_similarity_matrix()
    detector.perform_hierarchical_clustering()
    
    # Generate visualizations
    detector.visualize_similarity_heatmap()
    detector.visualize_document_clusters()
    detector.visualize_duplicate_network()
    
    # Save results
    detector.save_results_to_excel()
    
    # Optional: Analyze what content is being duplicated
    detector.analyze_duplicate_content()
    
if __name__ == "__main__":
    main()
