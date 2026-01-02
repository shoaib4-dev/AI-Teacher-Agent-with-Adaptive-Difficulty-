# Allowed AI Topics for Quiz Generation

The quiz generation feature is **restricted to AI-related topics only**. The system validates topics using a comprehensive list of AI keywords and patterns.

## Quick Reference - Suggested Topics

These are the most common AI topics you can use:

1. **Machine Learning**
2. **Deep Learning**
3. **Neural Networks**
4. **Natural Language Processing** (or **NLP**)
5. **Computer Vision**
6. **Reinforcement Learning**
7. **Convolutional Neural Networks** (or **CNN**)
8. **Transformers**
9. **Generative AI**
10. **Supervised Learning**
11. **Unsupervised Learning**
12. **Image Recognition**
13. **Text Classification**
14. **Sentiment Analysis**
15. **Object Detection**

## Complete List of Allowed Topics

The system recognizes **100+ AI-related topics** including:

### Core AI Concepts
- Artificial Intelligence, AI
- Machine Learning, ML
- Deep Learning, DL
- Neural Networks, Neural Network, ANN
- Supervised Learning
- Unsupervised Learning
- Reinforcement Learning
- Transfer Learning
- Semi-supervised Learning
- Active Learning

### AI Subfields
- Natural Language Processing, NLP
- Computer Vision, CV
- Speech Recognition
- Robotics
- Expert Systems
- Knowledge Representation
- Reasoning
- Planning
- Search Algorithms
- Optimization
- Genetic Algorithms

### Deep Learning
- Convolutional Neural Network, CNN
- Recurrent Neural Network, RNN
- Long Short-Term Memory, LSTM
- Gated Recurrent Unit, GRU
- Transformer
- Attention Mechanism
- BERT
- GPT
- Generative AI
- Generative Adversarial Network, GAN
- Variational Autoencoder, VAE
- Autoencoder
- Encoder-Decoder
- Seq2Seq

### Machine Learning Algorithms
- Linear Regression
- Logistic Regression
- Decision Tree
- Random Forest
- Support Vector Machine, SVM
- K-Means
- K-Nearest Neighbors, KNN
- Naive Bayes
- Gradient Boosting
- XGBoost
- AdaBoost
- Clustering
- Classification
- Regression
- Dimensionality Reduction
- Principal Component Analysis, PCA
- T-SNE

### AI Applications
- Image Recognition
- Object Detection
- Face Recognition
- Image Classification
- Text Classification
- Sentiment Analysis
- Named Entity Recognition, NER
- Machine Translation
- Text Generation
- Chatbot
- Virtual Assistant
- Recommendation System
- Anomaly Detection
- Predictive Analytics
- Time Series Forecasting

### AI Tools and Frameworks
- TensorFlow
- PyTorch
- Keras
- Scikit-learn, sklearn
- OpenCV
- NLTK
- spaCy
- Hugging Face
- Transformers

### AI Ethics and Concepts
- AI Ethics
- Bias in AI
- Fairness
- Explainable AI, XAI
- Model Interpretability
- Adversarial Attacks
- Federated Learning
- Edge AI
- Quantization
- Model Compression

### Advanced Topics
- Q-Learning
- Policy Gradient
- Actor-Critic
- Meta-Learning
- Few-Shot Learning
- Zero-Shot Learning
- Continual Learning
- Multi-Task Learning
- Domain Adaptation
- Self-Supervised Learning
- Contrastive Learning
- Representation Learning
- Feature Learning

### AI Architectures
- ResNet
- VGG
- Inception
- MobileNet
- YOLO
- R-CNN
- U-Net
- Diffusion Models
- Stable Diffusion

### NLP Specific
- Word Embeddings
- Word2Vec
- GloVe
- FastText
- ELMO
- Transformer Architecture
- Self-Attention
- Multi-Head Attention
- Positional Encoding
- Tokenization
- Lemmatization
- Stemming
- Part-of-Speech Tagging
- Dependency Parsing
- Semantic Analysis

### Computer Vision Specific
- Image Segmentation
- Semantic Segmentation
- Instance Segmentation
- Object Tracking
- Optical Flow
- Feature Extraction
- Edge Detection
- Image Enhancement
- Super-Resolution
- Style Transfer

### Data Science for AI
- Data Preprocessing
- Feature Engineering
- Feature Selection
- Cross-Validation
- Hyperparameter Tuning
- Model Evaluation
- Confusion Matrix
- ROC Curve
- Precision
- Recall
- F1 Score

## How Topic Validation Works

1. **Direct Match**: If your topic exactly matches any AI keyword (case-insensitive)
2. **Keyword Match**: If your topic contains any AI keyword
3. **Pattern Match**: If your topic contains common AI patterns like:
   - "artificial intelligence"
   - "machine learning"
   - "deep learning"
   - "neural network"
   - "ai "
   - " ml "
   - " nlp "
   - "computer vision"
   - "natural language"

## Examples

### ✅ Allowed Topics
- "Machine Learning"
- "Deep Learning Basics"
- "Introduction to Neural Networks"
- "NLP for Beginners"
- "Computer Vision Applications"
- "Reinforcement Learning Algorithms"
- "CNN Architecture"
- "Transformers in NLP"
- "Generative AI Models"
- "Supervised vs Unsupervised Learning"

### ❌ Not Allowed Topics
- "Python Basics"
- "Mathematics"
- "History"
- "Data Structures"
- "Algorithms" (general algorithms, not AI-specific)
- "Web Development"
- "Database Management"

## Frontend Dropdown Options

The quiz interface dropdown includes these pre-selected AI topics:
1. Machine Learning
2. Deep Learning
3. Neural Networks
4. Natural Language Processing
5. Computer Vision
6. Reinforcement Learning
7. Convolutional Neural Networks
8. Transformers
9. Generative AI
10. Supervised Learning
11. Unsupervised Learning

## Testing a Topic

You can test if a topic is allowed by running:
```bash
python test_ai_topics.py
```

Or in Python:
```python
from src.utils.ai_topics import is_ai_topic

print(is_ai_topic("Machine Learning"))  # True
print(is_ai_topic("Python Basics"))     # False
```

## Error Message

If you try to generate a quiz with a non-AI topic, you'll see:
```
Quiz generation is only available for AI-related topics. '[Your Topic]' is not recognized as an AI topic. Please enter an AI-related topic such as Machine Learning, Deep Learning, Neural Networks, Natural Language Processing, etc.
```

