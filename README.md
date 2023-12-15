# Gender Attribution Model Process

This repository contains Python scripts for both training and scoring a gender attribution model. The model is trained using Multinomial Naive Bayes, and gender predictions are scored for records with missing gender values in a BigQuery table. The process utilizes Google Cloud Storage for model storage and retrieval.

## Prerequisites

1. **Google Cloud Storage Setup:**
   - Ensure you have a Google Cloud Storage bucket configured.
   - Set up the necessary folders in the bucket for storing the trained model and vectorizer.

2. **BigQuery Setup:**
   - Create a BigQuery dataset and table for storing the attributed gender predictions.

## Instructions

### 1. Model Training (gender_model_training.py)

#### 1.1. BigQuery Data Retrieval
   - Execute the SQL query to retrieve demographic information from the specified BigQuery table (`abi-martech-global.maz_col_cdp_inbound.L2_attributes`).

#### 1.2. Model Training
   - Train a Multinomial Naive Bayes model on the retrieved data, encoding gender categories.

#### 1.3. Text Processing
   - Apply text processing to clean and normalize first names.

#### 1.4. Data Filtering
   - Filter the dataset to include only valid gender categories and non-null names.

#### 1.5. Text Transformation
   - Transform text data.

#### 1.6. Save Model to Google Cloud Storage
   - Save the trained model (`modelo_entrenado.joblib`) and vectorizer (`vectorizador.joblib`) to the specified Google Cloud Storage bucket.

### 2. Gender Attribution Model Scoring (score_model.py)

#### 2.1. Model Loading
   - Load the pre-trained gender attribution model (`modelo_entrenado.joblib`) from the Google Cloud Storage bucket.
   - Load the vectorizer (`vectorizador.joblib`) from the same bucket.

#### 2.2. BigQuery Table Check
   - Check if the target BigQuery table (`maz_col_sandbox.atribucion_genero`) exists.
   - If not, create the table with the required schema.

#### 2.3. Data Retrieval
   - Execute a SQL query to retrieve records from the source table (`abi-martech-global.maz_col_cdp_inbound.L2_attributes`) with missing gender values.
   - Apply pre-processing rules to clean and normalize the data.

#### 2.4. Data Filtering
   - Filter out records with null or empty first name values.

#### 2.5. Gender Prediction
   - Use the loaded model and vectorizer to predict gender for the filtered records.
   - Assign predicted genders (Male/Female) based on model outcomes.

#### 2.6. Export to BigQuery
   - Export the attributed gender predictions to the target BigQuery table (`maz_col_sandbox.atribucion_genero`).

#### 2.7. Running the Process
   - Execute the Python script (`score_model.py`) to perform the gender attribution scoring.
   - Monitor the console for any messages or errors.

#### Note
   - Adjust the Google Cloud Storage bucket name and file paths in the scripts to match your specific setup.
