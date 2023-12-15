def if_tbl_exists(client, table_ref):
    """
    Checks if a BigQuery table exists.

    Parameters:
    - client: BigQuery Client instance.
    - table_ref: Table reference in the format `project.dataset.table`.

    Returns:
    - True if the table exists, False otherwise.
    """
    from google.cloud.exceptions import NotFound
    try:
        client.get_table(table_ref)
        return True
    except NotFound:
        return False

def score_model():
    """
    Scores gender predictions for records with missing gender values in a BigQuery table.

    This function loads a pre-trained machine learning model and a vectorizer from Google Cloud Storage,
    retrieves data from a BigQuery table, applies pre-processing rules, and exports predictions back to BigQuery.

    Note: Ensure that the necessary Google Cloud Storage and BigQuery configurations are set up.

    """
    import joblib
    import pandas as pd
    import numpy as np
    import warnings
    from google.cloud import bigquery
    from google.cloud import storage

    # Suppress warnings
    warnings.filterwarnings("ignore")

    # Set up Google Cloud Storage and BigQuery clients
    client_storage = storage.Client()
    client_bq = bigquery.Client()

    # Load the model from Google Cloud Storage
    bucket_name = 'abi-martech-maz-col-local'
    model_file_path = 'gender_model/modelo_entrenado.joblib'
    bucket = client_storage.get_bucket(bucket_name)
    blob = bucket.blob(model_file_path)
    
    # Load the model directly from the blob object
    with blob.open("rb") as file:
        modelo_cargado = joblib.load(file)

    # Load the vectorizer
    model_file_path = 'gender_model/vectorizador.joblib'
    blob = bucket.blob(model_file_path)
    
    # Load the vectorizer directly from the blob object
    with blob.open("rb") as file:
        vectorizador = joblib.load(file)
    
    # Set up BigQuery table and schema
    table_id = 'abi-martech-maz-col.maz_col_sandbox.atribucion_genero'
    if not if_tbl_exists(client_bq, table_id):
        schema = [
            bigquery.SchemaField('td_id', 'STRING'),
            bigquery.SchemaField('abi_gender_pred', 'STRING')
        ]
        table = bigquery.Table(table_id, schema=schema)
        client_bq.create_table(table)

    # SQL query to retrieve data
    query = """
    SELECT
      td_id,
      abi_firstname,
      LOWER(TRIM(REGEXP_REPLACE(NORMALIZE(abi_gender, nfd), r"\pM", ''))) AS abi_gender
    FROM
      `abi-martech-global.maz_col_cdp_inbound.L2_attributes` a
    WHERE
      classification_category IN ('gold', 'diamond')
      AND abi_gender IS NULL
      AND abi_firstname IS NOT NULL
      AND NOT EXISTS (
        SELECT td_id
        FROM `abi-martech-maz-col.maz_col_sandbox.atribucion_genero` b
        WHERE a.td_id = b.td_id
      )
    """

    # Execute query and get DataFrame
    connombre_singenero = client_bq.query(query).to_dataframe()

    # Apply pre-processing rules
    connombre_singenero['abi_firstname'] = connombre_singenero['abi_firstname'].str.replace('\d+', '')
    # ... (additional pre-processing steps)

    # Filter non-null and non-empty values
    connombre_singenero1 = connombre_singenero[connombre_singenero.abi_firstname.notnull()]
    connombre_singenero1 = connombre_singenero1[connombre_singenero1.abi_firstname != '']
    connombre_singenero1 = connombre_singenero1[connombre_singenero1.abi_firstname != ' ']

    # Get sample names
    sample_name = list(connombre_singenero1['abi_firstname'].values)

    if len(sample_name) > 0:
        # Get gender predictions
        calificaciones = modelo_cargado.predict(vectorizador.transform(sample_name))
        # Assign gender predictions
        calificaciones_genero = ['Male' if i == 1 else 'Female' for i in calificaciones]
        # Assign predictions to DataFrame
        connombre_singenero1['abi_gender_pred'] = calificaciones_genero
        # Export results to BigQuery - Sandbox
        connombre_singenero1[['td_id', 'abi_gender_pred']].to_gbq('maz_col_sandbox.atribucion_genero', 'abi-martech-maz-col', if_exists='append')
    else:
        print("No new records for score")
