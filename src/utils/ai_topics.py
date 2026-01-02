"""
AI Topics Validator - List of AI-related topics allowed for quiz generation
"""

# Comprehensive list of AI-related topics and keywords
AI_TOPICS = {
    # Core AI Concepts
    "artificial intelligence", "ai", "machine learning", "ml", "deep learning", "dl",
    "neural networks", "neural network", "artificial neural network", "ann",
    "supervised learning", "unsupervised learning", "reinforcement learning",
    "transfer learning", "semi-supervised learning", "active learning",
    
    # AI Subfields
    "natural language processing", "nlp", "computer vision", "cv", "speech recognition",
    "robotics", "expert systems", "knowledge representation", "reasoning",
    "planning", "search algorithms", "optimization", "genetic algorithms",
    
    # Deep Learning
    "convolutional neural network", "cnn", "recurrent neural network", "rnn",
    "long short-term memory", "lstm", "gated recurrent unit", "gru",
    "transformer", "attention mechanism", "bert", "gpt", "generative ai",
    "generative adversarial network", "gan", "variational autoencoder", "vae",
    "autoencoder", "encoder-decoder", "seq2seq",
    
    # Machine Learning Algorithms
    "linear regression", "logistic regression", "decision tree", "random forest",
    "support vector machine", "svm", "k-means", "k-nearest neighbors", "knn",
    "naive bayes", "gradient boosting", "xgboost", "adaboost",
    "clustering", "classification", "regression", "dimensionality reduction",
    "principal component analysis", "pca", "t-sne",
    
    # AI Applications
    "image recognition", "object detection", "face recognition", "image classification",
    "text classification", "sentiment analysis", "named entity recognition", "ner",
    "machine translation", "text generation", "chatbot", "virtual assistant",
    "recommendation system", "recommender system", "anomaly detection",
    "predictive analytics", "time series forecasting",
    
    # AI Tools and Frameworks
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "opencv", "nltk", "spacy", "hugging face", "transformers",
    
    # AI Ethics and Concepts
    "ai ethics", "bias in ai", "fairness", "explainable ai", "xai",
    "model interpretability", "adversarial attacks", "federated learning",
    "edge ai", "quantization", "model compression",
    
    # Advanced Topics
    "reinforcement learning", "q-learning", "policy gradient", "actor-critic",
    "meta-learning", "few-shot learning", "zero-shot learning", "continual learning",
    "multi-task learning", "domain adaptation", "self-supervised learning",
    "contrastive learning", "representation learning", "feature learning",
    
    # AI Architectures
    "resnet", "vgg", "inception", "mobilenet", "yolo", "r-cnn",
    "u-net", "gan", "vae", "diffusion models", "stable diffusion",
    
    # NLP Specific
    "word embeddings", "word2vec", "glove", "fasttext", "elmo",
    "transformer architecture", "self-attention", "multi-head attention",
    "positional encoding", "tokenization", "lemmatization", "stemming",
    "part-of-speech tagging", "dependency parsing", "semantic analysis",
    
    # Computer Vision Specific
    "image segmentation", "semantic segmentation", "instance segmentation",
    "object tracking", "optical flow", "feature extraction", "edge detection",
    "image enhancement", "super-resolution", "style transfer",
    
    # Data Science for AI
    "data preprocessing", "feature engineering", "feature selection",
    "cross-validation", "hyperparameter tuning", "model evaluation",
    "confusion matrix", "roc curve", "precision", "recall", "f1 score",
}

def is_ai_topic(topic: str) -> bool:
    """
    Check if a topic is AI-related
    
    Args:
        topic: The topic name to check
        
    Returns:
        True if the topic is AI-related, False otherwise
    """
    if not topic:
        return False
    
    topic_lower = topic.lower().strip()
    
    # Direct match
    if topic_lower in AI_TOPICS:
        return True
    
    # Check if topic contains any AI keywords
    for ai_keyword in AI_TOPICS:
        if ai_keyword in topic_lower:
            return True
    
    # Check for common AI patterns
    ai_patterns = [
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "neural network",
        "ai ",
        " ml ",
        " nlp ",
        "computer vision",
        "natural language",
    ]
    
    for pattern in ai_patterns:
        if pattern in topic_lower:
            return True
    
    return False

def get_ai_topic_suggestions() -> list:
    """Get a list of suggested AI topics"""
    return [
        "Machine Learning",
        "Deep Learning",
        "Neural Networks",
        "Natural Language Processing",
        "Computer Vision",
        "Reinforcement Learning",
        "Convolutional Neural Networks",
        "Transformers",
        "Generative AI",
        "Supervised Learning",
        "Unsupervised Learning",
        "Image Recognition",
        "Text Classification",
        "Sentiment Analysis",
        "Object Detection",
    ]

