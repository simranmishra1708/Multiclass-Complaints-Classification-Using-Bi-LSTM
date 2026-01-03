# Multiclass-Complaints-Classification-Using-Bi-LSTM

🧠 User Complaint Understanding & Classification System (End-to-End NLP + MLOps)
📌 Project Overview

Customer complaints are long, unstructured, and often contain multiple issues in a single narrative.
This project builds an end-to-end NLP system to automatically classify consumer complaints into predefined product categories and evaluates multiple modeling approaches before selecting a production-ready model.

The project follows a rigorous experimentation → model selection → production mindset, comparing:

Classical machine learning models

Deep learning (Bi-LSTM)

Transformer-based models (DistilBERT)

and is designed to be fully deployable using MLOps best practices.

🎯 Problem Statement

Given a user’s complaint text, predict the financial product category (e.g., credit card, loan, mortgage) accurately and robustly, even in the presence of:

Noisy text

Long narratives

Severe class imbalance

🗂 Dataset Description

Source: Consumer Financial Complaint Dataset

Data Type: Real-world, user-generated complaint narratives

Target: product (multiclass classification)

Key Characteristics

Long, unstructured text

Class imbalance across product categories

Missing and noisy entries

Multiple issues mentioned in a single complaint

This dataset closely mirrors real enterprise customer support and regulatory workflows.

🧪 Modeling Approach

We follow a layered experimentation strategy:

1️⃣ Classical Machine Learning (Baselines)

TF-IDF Vectorization

Logistic Regression

Linear Support Vector Machine (SVM)

Multinomial Naive Bayes

Purpose:
Establish strong, fast, and interpretable baselines.

2️⃣ Deep Learning

Bi-LSTM with Word Embeddings

Captures sequential patterns in text

Purpose:
Evaluate whether sequence modeling provides gains over linear baselines.

3️⃣ Transformer-Based NLP

DistilBERT (PyTorch, Hugging Face)

Contextual language understanding

Fine-tuned on complaint data

Purpose:
Achieve state-of-the-art performance on imbalanced, long-text data.

⚙️ Text Preprocessing Strategy
For Classical ML & LSTM

Lowercasing

Removal of non-alphabet characters

Stopword removal

Whitespace normalization

For Transformers

Minimal preprocessing

No stopword removal

Tokenization handled by DistilBERT tokenizer

This highlights model-aware preprocessing, a key production insight.

📊 Evaluation Metrics

To handle class imbalance, we use:

Accuracy

Macro F1-Score (critical metric)

Weighted F1-Score

Confusion Matrix analysis

📈 Experiment Results Summary
Model	Accuracy	Macro F1	Key Insight
Naive Bayes	Low	Low	Weak baseline
Logistic Regression	High	Medium	Strong, fast baseline
Linear SVM	Very High	High	Best classical model
Bi-LSTM	Comparable	Improved minority recall	Sequential modeling helps
DistilBERT	Best	Best	Superior contextual understanding

📌 Final Choice: DistilBERT achieved the best macro-F1, especially on minority classes, making it the preferred production model.

🏆 Final Model Selection Rationale

Why DistilBERT?

Handles long, noisy complaint text effectively

Improves minority-class performance

Robust to vocabulary variation

Easily extendable to:

Explainability

RAG-based systems

Production APIs

Fallback Model:
Logistic Regression (TF-IDF) for low-latency or cost-sensitive use cases.

🏗 Project Structure (MLOps-Ready)
├── src/
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   ├── data_transformation.py
│   │   ├── model_trainer_baseline.py
│   │   ├── model_trainer_lstm.py
│   │   ├── model_trainer_transformer.py
│   │   ├── model_evaluation.py
│   │   └── model_pusher.py
│   │
│   ├── pipelines/
│   │   ├── training_pipeline.py
│   │   └── prediction_pipeline.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   ├── exception.py
│   │   └── common.py
│
├── notebooks/
│   └── experiments.ipynb
│
├── artifacts/
│   ├── data/
│   ├── models/
│   └── metrics/
│
├── app.py
├── Dockerfile
├── requirements.txt
├── README.md

🚀 Deployment Plan

Model Serving: FastAPI

Containerization: Docker

Cloud: AWS EC2

CI/CD: GitHub Actions

Inference: REST API endpoint for real-time prediction

🔍 Explainability (Planned / Extendable)

SHAP for classical models

Token-level attention / attribution for DistilBERT

Sentence-level root cause highlighting

🧠 Key Learnings

Classical ML models remain strong baselines for NLP

Deep learning should be justified through measurable gains

Transformers excel on long, imbalanced, real-world text

Model choice must balance accuracy, cost, and latency

Production NLP requires robust preprocessing and reproducibility


🔮 Future Enhancements

Hierarchical classification (product → issue → sub-issue)

Explainable AI dashboard

RAG-based complaint resolution assistant

Drift detection & monitoring

Human-in-the-loop feedback integration

🛠 Tech Stack

Python

Scikit-learn

TensorFlow (Bi-LSTM)

PyTorch

Hugging Face Transformers

FastAPI

Docker

AWS EC2
