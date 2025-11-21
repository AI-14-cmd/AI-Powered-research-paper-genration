import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from io import BytesIO
import base64
import os
import hashlib
from typing import Dict, List

class ImageGenerator:
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def _get_seed(self, topic: str) -> int:
        """Generate consistent seed from topic for reproducible data"""
        return int(hashlib.md5(topic.encode()).hexdigest()[:8], 16) % 1000
    
    def generate_research_charts(self, topic: str, paper_content: Dict) -> List[Dict]:
        """Generate relevant charts and graphs for research paper"""
        charts = []
        
        # Generate different types of charts based on topic
        if 'fmri' in topic.lower() or 'brain' in topic.lower():
            charts.extend(self._generate_neuroscience_charts(topic))
        elif 'ai' in topic.lower() or 'machine learning' in topic.lower():
            charts.extend(self._generate_ai_charts(topic))
        else:
            charts.extend(self._generate_generic_charts(topic))
        
        return charts
    
    def _generate_neuroscience_charts(self, topic: str) -> List[Dict]:
        """Generate neuroscience-specific charts"""
        charts = []
        
        # Brain activation heatmap
        fig, ax = plt.subplots(figsize=(10, 6))
        np.random.seed(self._get_seed(topic))
        # Generate realistic brain activation patterns
        base_activation = np.array([85, 78, 72, 65, 45, 38, 82, 75])  # Typical activation levels
        data = np.outer(base_activation, np.linspace(0.8, 1.2, 10)) + np.random.normal(0, 5, (8, 10))
        data = np.clip(data, 0, 100)
        regions = ['Frontal', 'Parietal', 'Temporal', 'Occipital', 'Cerebellum', 'Brainstem', 'Limbic', 'Motor']
        
        sns.heatmap(data, yticklabels=regions, cmap='viridis', annot=True, fmt='.1f', ax=ax)
        ax.set_title(f'Brain Activation Patterns in {topic}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time Points (seconds)')
        
        charts.append({
            'title': 'Brain Activation Heatmap',
            'image': self._fig_to_base64(fig),
            'caption': f'Heatmap showing brain activation patterns across different regions during {topic.lower()} tasks.'
        })
        plt.close(fig)
        
        # Accuracy comparison chart
        fig, ax = plt.subplots(figsize=(10, 6))
        methods = ['Traditional\nMethods', 'Machine\nLearning', 'Deep\nLearning', 'Proposed\nMethod']
        accuracy = [72.3, 84.7, 89.2, 92.8]
        colors = ['#ff7f0e', '#2ca02c', '#d62728', '#1f77b4']
        
        bars = ax.bar(methods, accuracy, color=colors, alpha=0.8)
        ax.set_ylabel('Accuracy (%)')
        ax.set_title(f'Classification Accuracy Comparison for {topic}', fontsize=14, fontweight='bold')
        ax.set_ylim(60, 100)
        
        for bar, acc in zip(bars, accuracy):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                   f'{acc}%', ha='center', va='bottom', fontweight='bold')
        
        charts.append({
            'title': 'Method Comparison',
            'image': self._fig_to_base64(fig),
            'caption': f'Comparison of different methodological approaches for {topic.lower()} showing accuracy improvements.'
        })
        plt.close(fig)
        
        return charts
    
    def _generate_ai_charts(self, topic: str) -> List[Dict]:
        """Generate AI/ML specific charts"""
        charts = []
        
        # Training progress chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        np.random.seed(self._get_seed(topic))
        epochs = np.arange(1, 51)
        # Realistic training curves
        train_loss = 2.5 * np.exp(-epochs/15) + 0.1 + np.random.normal(0, 0.02, 50)
        val_loss = 2.8 * np.exp(-epochs/18) + 0.15 + np.random.normal(0, 0.03, 50)
        # Ensure validation loss is higher than training loss
        val_loss = np.maximum(val_loss, train_loss + 0.05)
        
        ax1.plot(epochs, train_loss, label='Training Loss', color='#1f77b4', linewidth=2)
        ax1.plot(epochs, val_loss, label='Validation Loss', color='#ff7f0e', linewidth=2)
        ax1.set_xlabel('Epochs')
        ax1.set_ylabel('Loss')
        ax1.set_title('Model Training Progress')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Accuracy over epochs
        train_acc = 100 * (1 - np.exp(-epochs/12)) * 0.95 + np.random.normal(0, 0.5, 50)
        val_acc = 100 * (1 - np.exp(-epochs/15)) * 0.92 + np.random.normal(0, 0.8, 50)
        # Ensure realistic accuracy bounds
        train_acc = np.clip(train_acc, 0, 100)
        val_acc = np.clip(val_acc, 0, 100)
        
        ax2.plot(epochs, train_acc, label='Training Accuracy', color='#2ca02c', linewidth=2)
        ax2.plot(epochs, val_acc, label='Validation Accuracy', color='#d62728', linewidth=2)
        ax2.set_xlabel('Epochs')
        ax2.set_ylabel('Accuracy (%)')
        ax2.set_title('Model Accuracy Progress')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        charts.append({
            'title': 'Training Progress',
            'image': self._fig_to_base64(fig),
            'caption': f'Training and validation metrics showing model performance improvement for {topic.lower()}.'
        })
        plt.close(fig)
        
        return charts
    
    def _generate_generic_charts(self, topic: str) -> List[Dict]:
        """Generate generic research charts"""
        charts = []
        
        # Performance comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        categories = ['Baseline', 'Method A', 'Method B', 'Proposed']
        # Generate topic-based performance values
        seed = self._get_seed(topic)
        np.random.seed(seed)
        base_values = [65, 75, 80, 85]
        noise = np.random.normal(0, 2, 4)
        values = [round(base + n, 1) for base, n in zip(base_values, noise)]
        colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))
        
        bars = ax.bar(categories, values, color=colors, alpha=0.8)
        ax.set_ylabel('Performance Score (%)')
        ax.set_title(f'Performance Comparison for {topic}', fontsize=14, fontweight='bold')
        
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                   f'{val}%', ha='center', va='bottom', fontweight='bold')
        
        charts.append({
            'title': 'Performance Analysis',
            'image': self._fig_to_base64(fig),
            'caption': f'Comparative analysis of different approaches for {topic.lower()} research.'
        })
        plt.close(fig)
        
        # Trend analysis
        fig, ax = plt.subplots(figsize=(10, 6))
        years = np.arange(2018, 2025)
        # Generate topic-based publication trends
        seed = self._get_seed(topic)
        np.random.seed(seed)
        base_growth = [45, 65, 95, 140, 200, 280, 380]
        noise = np.random.normal(0, 10, 7)
        publications = [max(int(base + n), 1) for base, n in zip(base_growth, noise)]
        
        ax.plot(years, publications, marker='o', linewidth=3, markersize=8, color='#1f77b4')
        ax.fill_between(years, publications, alpha=0.3, color='#1f77b4')
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of Publications')
        ax.set_title(f'Research Trend in {topic} (2018-2024)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        charts.append({
            'title': 'Research Trends',
            'image': self._fig_to_base64(fig),
            'caption': f'Publication trends showing growing interest in {topic.lower()} research over recent years.'
        })
        plt.close(fig)
        
        return charts
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        return f"data:image/png;base64,{image_base64}"