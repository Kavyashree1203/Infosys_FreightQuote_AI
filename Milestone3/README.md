# 🚚 FreightQuote AI

### AI-Powered Multi-Agent Freight Quotation & Logistics Decision Support System

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge\&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-red?style=for-the-badge\&logo=streamlit)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange?style=for-the-badge)
![RAG](https://img.shields.io/badge/RAG-FAISS-green?style=for-the-badge)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?style=for-the-badge)
![GitHub](https://img.shields.io/badge/GitHub-Version_Control-black?style=for-the-badge\&logo=github)

</p>

---

# 📖 Project Overview

**FreightQuote AI** is an intelligent logistics platform that combines **Machine Learning**, **Generative AI**, and **Retrieval-Augmented Generation (RAG)** to automate freight quotation, logistics analysis, and compliance assistance.

The application provides an interactive Streamlit interface where users can obtain freight price predictions, ask logistics-related questions through an AI Copilot, and utilize multiple AI agents for shipment analysis and decision support. A RAG knowledge base built from customs regulations, logistics documents, and government resources enables the system to deliver context-aware responses for freight and compliance queries.

---

# 🎯 Project Objectives

* Develop an AI-driven freight quotation platform.
* Predict freight pricing using Machine Learning.
* Build a multi-agent decision support system.
* Implement a Retrieval-Augmented Generation (RAG) knowledge base.
* Improve logistics planning and customs compliance.
* Provide secure user authentication and administration.
* Deliver an intuitive web-based application using Streamlit.

---

# ✨ Key Features

## 🤖 AI Copilot

* Natural language logistics assistant
* Context-aware responses using RAG
* Freight and customs guidance

## 🧠 Multi-Agent AI System

The project incorporates three Machine Learning agents:

### Agent 1 – Dynamic Pricing (Regression)

Predicts freight quotation costs based on shipment characteristics and logistics parameters.

### Agent 2 – Route Delay (Classification)

Predicts whether a shipment is likely to experience delays using operational and route-related information.

### Agent 3 – Carrier Audit (Classification)

Evaluates carrier performance and supports operational decision-making using classification models.

## 📊 Machine Learning

* Freight price prediction
* Classification models
* Model evaluation
* Performance comparison

## 📚 Retrieval-Augmented Generation (RAG)

* FAISS Vector Database
* HuggingFace Embeddings
* Government customs knowledge
* PDF knowledge extraction
* Context-aware document retrieval

## 🌐 Knowledge Collection

* Government website scraping
* Logistics document processing
* Automated PDF extraction
* Structured knowledge base generation

## 🔐 Authentication & Security

* User Registration
* Secure Login
* Password Reset
* OTP Verification
* Role-Based Access Control

## 👨‍💼 Admin Dashboard

* User management
* System monitoring
* Machine Learning metrics
* Administrative controls

---

# 🛠️ Technology Stack

| Category             | Technologies                      |
| -------------------- | --------------------------------- |
| Programming Language | Python                            |
| Frontend             | Streamlit                         |
| Machine Learning     | Scikit-Learn                      |
| AI                   | Generative AI                     |
| RAG Framework        | LangChain                         |
| Vector Database      | FAISS                             |
| Embedding Model      | HuggingFace Sentence Transformers |
| Database             | SQLite                            |
| Data Processing      | Pandas, NumPy                     |
| Web Scraping         | Requests, BeautifulSoup           |
| PDF Processing       | PyMuPDF (fitz)                    |
| Authentication       | JWT, bcrypt                       |
| Version Control      | Git & GitHub                      |

---

# 🌟 Project Highlights

* 🤖 AI-Powered Logistics Copilot
* 🧠 Multi-Agent Machine Learning System
* 📊 Freight Price Prediction
* 🚚 Route Delay Prediction
* 📋 Carrier Audit Classification
* 📚 Retrieval-Augmented Generation (RAG)
* 🌐 Government Customs Knowledge Integration
* 📄 Automated PDF Knowledge Extraction
* 🔐 Secure Authentication & Authorization
* 📈 Interactive Streamlit Dashboard

---
# 🏗️ System Architecture

FreightQuote AI follows a modular architecture that integrates Machine Learning, Generative AI, and Retrieval-Augmented Generation (RAG) into a single intelligent logistics platform.

```text
                           User
                             │
                             ▼
                    Streamlit Web Application
                             │
      ┌──────────────────────┼──────────────────────┐
      ▼                      ▼                      ▼
 AI Copilot           ML Prediction Engine     Admin Dashboard
      │                      │
      │              ┌───────┼───────────────┐
      │              ▼       ▼               ▼
      │          Agent 1  Agent 2        Agent 3
      │          Dynamic  Route Delay    Carrier Audit
      │          Pricing  Classification Classification
      │
      ▼
Retrieval-Augmented Generation (RAG)
      │
      ▼
FAISS Vector Database
      │
      ▼
Knowledge Base
      │
      ▼
Government Websites + PDF Documents + Offline Corpus
```

---

# 🤖 Multi-Agent Workflow

The FreightQuote AI platform combines three Machine Learning agents with an AI Copilot to support logistics decision-making.

### 🔹 Agent 1 – Dynamic Pricing (Regression)

* Predicts freight quotation cost.
* Uses shipment attributes to estimate pricing.
* Supports quick and consistent quotation generation.

### 🔹 Agent 2 – Route Delay (Classification)

* Predicts the likelihood of shipment delays.
* Considers route-related and operational features.
* Assists logistics planning and scheduling.

### 🔹 Agent 3 – Carrier Audit (Classification)

* Evaluates carrier performance.
* Supports operational audits and carrier assessment.
* Helps improve logistics reliability.

---

# 📁 Project Structure

```text
FreightQuote_AI/
│
├── FreightQuote_AI_Comprehensive.ipynb
├── FreightQuote_RAG_Builder.ipynb
├── app.py
├── README.md
├── requirements.txt
├── freight_database.db
├── freight_vectorstore/
│
├── knowledge_base/
│   ├── kb_freight.json
│   ├── us_customs_electronics.txt
│   ├── isf_10_2_rules.txt
│   ├── incoterms_guide.txt
│   ├── imo_2020_sulphur.txt
│   ├── bill_of_lading_fields.txt
│   ├── freight_pricing_margin.txt
│   ├── weather_rerouting_rules.txt
│   ├── cbam_regulations.txt
│   ├── dangerous_goods_iata.txt
│   └── port_congestion_causes.txt
│
└── assets/
```

---

## 🚀 How to Run FreightQuote AI in Google Colab
This guide covers the execution of the primary FreightQuote_AI_Comprehensive notebook and the accompanying FreightQuote_RAG_Builder notebook. Google Colab provides the necessary GPU resources and environment to run this Multi-Agent LLM platform seamlessly.  

### 🛑 Prerequisites: Configuring Colab Secrets
Before running any cells, you must securely inject your API keys and environment variables using Google Colab's Secrets feature (the key icon 🔑 on the left sidebar).

Add the following keys and their corresponding values:  HF_TOKEN: Your HuggingFace access token (required to download the Qwen-2.5-3B model).

KAGGLE_USERNAME & KAGGLE_KEY (or KAGGLE_API_TOKEN): Your Kaggle API credentials to download the ML training datasets. 

NGROK_AUTHTOKEN: Your Ngrok tunnel authentication token to expose the web app.  

EMAIL_ADDRESS & EMAIL_PASSWORD: Your Gmail address and App Password for sending OTP emails. 

ADMIN_EMAIL & ADMIN_PASSWORD: Your desired login credentials for the admin dashboard.

JWT_SECRET_KEY: A secure string used for generating session tokens. 

## 🛠️ Phase 1: Build the RAG Knowledge Base
If this is your first time setting up the project, you must build the vector database so the AI Copilot can reference global trade laws.  Open the RAG Builder: 

Open the FreightQuote_RAG_Builder.ipynb notebook in Google Colab.  

Run Dependencies: Execute the first cell to install langchain, faiss-cpu, pymupdf, and other required libraries. 

Mount Google Drive: Run the subsequent cell to mount your Google Drive. This ensures the output folder (/content/drive/MyDrive/FreightQuote_AI/rag_documents) is created permanently on your cloud storage.  

Execute the Pipeline: Run the remaining cells in order to scrape the embedded HTML and PDF sources, chunk the text, and generate the freight_vectorstore FAISS database.  
## ⚡ Phase 2: Run the Main Application

Once the knowledge base is built, open the main FreightQuote_AI_Comprehensive (8).ipynb notebook in Google Colab. Ensure your Runtime is set to use a T4 GPU (Runtime > Change runtime type > T4 GPU).  Execute the notebook sequentially:

Step 1 — Install Dependencies: Run the first cell to install all required libraries, including streamlit, pyngrok, scikit-learn, transformers, and bitsandbytes.  

Step 2 — Configure Secrets & Mount Drive: Execute this cell to mount your Google Drive and automatically generate the ~/.kaggle/kaggle.json file using the secrets you configured in the prerequisites.  

Step 3 — Write Application Modules: Run the %%writefile cells. Colab will physically write out the modular Python scripts (config.py, ui_theme.py, auth.py, llm_engine_freight.py, etc.) into your temporary Colab workspace.  

Step 4 — Initialize Database & Seed Data: Run the cell containing db.init_db() and seed_data.seed_all() to build the SQLite database (freightquote.db) and inject the sample global carriers, quotes, and shipments. 

Step 5 — Train ML Agents: Execute the training cell to pull the Kaggle datasets and train the Pricing, Route/Weather, and Carrier Audit machine learning models. The resulting .joblib models will be saved to your Google Drive for persistent caching.  

Step 6 — Launch Streamlit Application via Ngrok Tunnel: Run the deployment cell. This script will bind your Colab Secrets to the process environment variables, start Streamlit headlessly on port 8501, and open an Ngrok tunnel. Click the generated Ngrok URL in the console output to access your live application. 

Step 7 & 8 — Diagnostics and Shutdown:If the Ngrok link fails to load, execute Step 7 (!cat streamlit.log) to view the application logs for errors.  When you are finished using the application, run Step 8 (process.terminate() and ngrok.kill()) to safely shut down the background Streamlit server and close the tunnel.  

# 📚 RAG Builder Workflow

The **FreightQuote_RAG_Builder.ipynb** notebook prepares the knowledge base used by the AI Copilot.

### Workflow

* Scrape logistics and customs websites.
* Detect and extract text from PDF documents.
* Create the logistics knowledge corpus.
* Generate embeddings.
* Build the FAISS vector database.
* Save the vector store for retrieval.

The main application loads this vector store to provide context-aware AI responses.

---

# 🤖 AI Copilot

The AI Copilot is the central intelligence module of **FreightQuote AI**. It enables users to interact with the system using natural language and receive context-aware logistics assistance.

### Key Capabilities

* Freight quotation assistance
* Customs and compliance guidance
* Logistics knowledge retrieval
* AI-powered decision support
* Context-aware responses using the RAG knowledge base

---

# 🧠 Multi-Agent AI System

FreightQuote AI incorporates three specialized Machine Learning agents, each designed to solve a specific logistics problem.

| Agent                         | Model Type     | Primary Function                                                                 |
| ----------------------------- | -------------- | -------------------------------------------------------------------------------- |
| **Agent 1 – Dynamic Pricing** | Regression     | Predicts freight quotation cost based on shipment details.                       |
| **Agent 2 – Route Delay**     | Classification | Predicts the likelihood of shipment delays using operational and route features. |
| **Agent 3 – Carrier Audit**   | Classification | Evaluates carrier performance and supports operational decision-making.          |

---

## 🔹 Agent 1 – Dynamic Pricing (Regression)

### Objective

Estimate freight quotation costs using shipment-related features.

### Input

* Shipment information
* Transport parameters
* Logistics attributes

### Output

* Predicted freight quotation cost

### Business Benefit

* Faster quotation generation
* Reduced manual calculations
* Consistent pricing decisions

---

## 🔹 Agent 2 – Route Delay (Classification)

### Objective

Predict whether a shipment is likely to be delayed.

### Input

* Route information
* Shipment characteristics
* Operational factors

### Output

* Delay prediction (Delayed / On Time)

### Business Benefit

* Better shipment planning
* Early risk identification
* Improved customer communication

---

## 🔹 Agent 3 – Carrier Audit (Classification)

### Objective

Assess carrier performance using historical logistics information.

### Input

* Carrier operational data
* Shipment performance indicators

### Output

* Carrier performance classification

### Business Benefit

* Supports carrier evaluation
* Improves logistics reliability
* Assists operational decision-making

---

# 📚 Retrieval-Augmented Generation (RAG)

The application integrates a Retrieval-Augmented Generation (RAG) pipeline to enhance AI responses with verified logistics knowledge.

### RAG Workflow

```text
User Question
      │
      ▼
AI Copilot
      │
      ▼
FAISS Vector Search
      │
      ▼
Relevant Logistics Documents
      │
      ▼
Generative AI Model
      │
      ▼
Context-Aware Response
```

### Knowledge Sources

The knowledge base includes:

* Government customs websites
* Logistics compliance documents
* Customs regulations
* Freight pricing rules
* Incoterms guidance
* Dangerous goods regulations
* Weather rerouting information
* PDF documents extracted automatically
* Structured JSON knowledge files

---

# 🌐 Web Scraping & Knowledge Collection

The RAG Builder automatically collects information from trusted logistics resources by:

* Scraping government customs websites
* Detecting downloadable PDF documents
* Extracting PDF text using PyMuPDF
* Creating structured knowledge files
* Building the FAISS vector database

This ensures that the AI Copilot responds using relevant logistics information instead of relying only on the language model.

---

# 📊 Machine Learning Model Performance

FreightQuote AI trains and evaluates multiple machine learning algorithms for each AI agent. The best-performing model is automatically selected based on evaluation metrics and deployed within the application.

## 🧠 Agent 1 – Dynamic Pricing (Regression)

This agent predicts freight quotation costs using multiple regression algorithms.

| Algorithm                      |  R² Score  |    RMSE |
| ------------------------------ | :--------: | ------: |
| Random Forest Regressor        |   0.9813   |   1,427 |
| Gradient Boosting Regressor    |   0.9902   |   1,033 |
| Extra Trees Regressor          |   0.9889   |   1,100 |
| Ridge Regression               |   0.9843   |   1,308 |
| Linear Regression              |   0.9843   |   1,307 |
| Decision Tree Regressor        |   0.9379   |   2,600 |
| AdaBoost Regressor             |   0.9255   |   2,848 |
| K-Nearest Neighbors Regressor  |   0.9387   |   2,583 |
| HistGradientBoosting Regressor | **0.9909** | **997** |
| ElasticNet                     |   0.9809   |   1,442 |

🏆 **Best Model:** **HistGradientBoostingRegressor**

* **R² Score:** **0.9909**
* **RMSE:** **997**
* **Status:** ✅ Target (R² ≥ 0.90) Achieved

---

## 🚛 Agent 2 – Route Delay Prediction (Classification)

This agent predicts the likelihood of shipment delays using classification algorithms.

| Algorithm                       |   ROC-AUC  |  Accuracy |
| ------------------------------- | :--------: | :-------: |
| Random Forest Classifier        |   0.9890   |   94.0%   |
| Gradient Boosting Classifier    |   0.9910   |   93.8%   |
| Logistic Regression             | **1.0000** | **99.8%** |
| Support Vector Machine (RBF)    |   0.9960   |   96.8%   |
| Extra Trees Classifier          |   0.9923   |   95.5%   |
| AdaBoost Classifier             |   0.9957   |   95.8%   |
| K-Nearest Neighbors             |   0.9815   |   93.0%   |
| HistGradientBoosting Classifier |   0.9930   |   95.5%   |
| SGD Classifier                  |   0.9996   |   99.0%   |

🏆 **Best Model:** **LogisticRegression**

* **ROC-AUC:** **1.0000**
* **Accuracy:** **99.8%**

---

## 📋 Agent 3 – Carrier Audit & Compliance (Classification)

This agent evaluates carrier performance and supports logistics compliance.

| Algorithm                       |   ROC-AUC  |  Accuracy  |
| ------------------------------- | :--------: | :--------: |
| Gradient Boosting Classifier    |   0.9999   |    99.8%   |
| Random Forest Classifier        | **1.0000** | **100.0%** |
| Extra Trees Classifier          | **1.0000** | **100.0%** |
| Logistic Regression             | **1.0000** |    99.8%   |
| Decision Tree Classifier        | **1.0000** |    98.8%   |
| AdaBoost Classifier             |   0.9999   |    99.8%   |
| MLP Classifier                  | **1.0000** | **100.0%** |
| HistGradientBoosting Classifier | **1.0000** |    99.8%   |

🏆 **Selected Model:** **RandomForestClassifier**

* **ROC-AUC:** **1.0000**
* **Accuracy:** **100.0%**

---

# 🏆 Training Summary

After evaluating multiple machine learning algorithms, FreightQuote AI automatically selected the best-performing model for each AI agent.

| AI Agent                                 | Selected Model                | Performance                             |
| ---------------------------------------- | ----------------------------- | --------------------------------------- |
| **Agent 1 – Dynamic Pricing**            | HistGradientBoostingRegressor | **R² = 0.9909**                         |
| **Agent 2 – Route Delay Prediction**     | LogisticRegression            | **ROC-AUC = 1.0000, Accuracy = 99.8%**  |
| **Agent 3 – Carrier Audit & Compliance** | RandomForestClassifier        | **ROC-AUC = 1.0000, Accuracy = 100.0%** |

The trained models are saved after the training pipeline completes and are used by the FreightQuote AI application to generate real-time predictions for pricing, delay risk, and carrier compliance.


# 🔐 Authentication & Admin Dashboard

### Authentication Features

* User Registration
* Secure Login
* Password Reset
* OTP Verification
* Role-Based Access Control

### Admin Dashboard

The Admin Panel enables administrators to:

* Monitor users
* Manage accounts
* View Machine Learning metrics
* Monitor AI usage
* Access system analytics

---
## 📸 Screenshots

### 1. Home Page
<img width="1841" height="844" alt="image" src="https://github.com/user-attachments/assets/6660b9cc-06b5-42e9-a22f-5b226f1422dc" />


### 2. AI Copilot
<img width="1838" height="828" alt="image" src="https://github.com/user-attachments/assets/ecd48fee-f5b8-40e0-8324-9aba291e7698" />

### 3. Login page
<img width="1082" height="467" alt="image" src="https://github.com/user-attachments/assets/bd06dcfe-8df0-4b0e-88b5-debaf5a888c8" />

### 4. Register Account
<img width="1078" height="810" alt="image" src="https://github.com/user-attachments/assets/c541489d-38db-428e-b41c-f9ecf1847f8e" />

### 5. Reset Password
<img width="1148" height="601" alt="image" src="https://github.com/user-attachments/assets/68513d4e-b629-4834-aa61-c596b5e0d8d6" />

### 6. Agent 1
<img width="1521" height="772" alt="image" src="https://github.com/user-attachments/assets/b94406ff-b09e-43c9-92c7-c175cc1e9a57" />

### 7. Agent 2
<img width="1920" height="849" alt="image" src="https://github.com/user-attachments/assets/3af25193-1d1c-4a73-b3cf-73889ccbed6a" />

### 8. Agent 3
<img width="1871" height="863" alt="image" src="https://github.com/user-attachments/assets/34d08285-40e0-412c-a745-2a854820fd1e" />

### 9. Analytics & Retrain
<img width="1855" height="868" alt="image" src="https://github.com/user-attachments/assets/b8dc1028-c4e8-4826-9bba-0ccdfca4f78f" />

### 10. Password Strength
<img width="970" height="556" alt="image" src="https://github.com/user-attachments/assets/d581d36c-0ab5-4f79-a5d8-87067764d0fb" />

### 11. Account Lockout After Multiple Failed Login Attempts
<img width="1017" height="516" alt="image" src="https://github.com/user-attachments/assets/d04d1c34-8fcd-4c13-9367-30d87155157b" />

## 👥 Team Contributions

| Team Member | Responsibilities |
|-------------|------------------|
| Alexa Salvi | Integrated the authentication module with the application and ensured smooth functionality without introducing new issues. |
| Vishnu Vardhan Reddy | Identified and resolved application issues, improved backend functionality, and enhanced overall system performance. |
| Kavya Shree | Redesigned and improved the UI/UX theme to provide a better user experience and a more attractive interface. |
| Samatha Sri | Conducted final testing, resolved minor issues, validated all application features, and prepared the README.md documentation. |
