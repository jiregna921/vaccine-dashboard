import pandas as pd
import streamlit as st
from fuzzywuzzy import fuzz
from typing import Tuple, Dict, List

@st.cache_data(show_spinner=False)
def load_data(file_uploader, dataset_type: str) -> pd.DataFrame:
    """
    Load and validate CSV data from a file uploader.
    """
    try:
        df = pd.read_csv(file_uploader)
        
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        df.columns = [col.strip().replace(' ', '_').replace('.', '').replace('-', '_') for col in df.columns]

        required_cols = ["Woreda", "Period"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"Error: {dataset_type} dataset is missing one of the required columns: {required_cols}")
            return pd.DataFrame()

        for col in ["Region", "Zone", "Woreda"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        st.success(f"{dataset_type} dataset loaded with {len(df)} records.")
        return df
    
    except Exception as e:
        st.error(f"Error loading {dataset_type} dataset: {str(e)}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def perform_fuzzy_matching(
    admin_df: pd.DataFrame, 
    dist_df: pd.DataFrame, 
    threshold: int = 85
) -> Tuple[Dict, List, List]:
    """
    Perform fuzzy matching on Woreda names between two dataframes.
    """
    admin_woredas = admin_df["Woreda"].dropna().unique()
    dist_woredas = dist_df["Woreda"].dropna().unique()
    
    match_map = {}
    unmatched_admin = []
    unmatched_dist = list(dist_woredas)

    for admin_woreda in admin_woredas:
        best_match = None
        highest_score = 0
        
        for dist_woreda in unmatched_dist:
            score = fuzz.ratio(admin_woreda, dist_woreda)
            if score > highest_score:
                highest_score = score
                best_match = dist_woreda
                
        if highest_score >= threshold:
            match_map[admin_woreda] = best_match
            unmatched_dist.remove(best_match)
        else:
            unmatched_admin.append(admin_woreda)
            
    return match_map, unmatched_admin, unmatched_dist

@st.cache_data(show_spinner=False)
def merge_datasets_with_fuzzy_matching(
    admin_df: pd.DataFrame, 
    dist_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Performs fuzzy matching and merges the administered and distributed datasets.
    """
    match_map, unmatched_admin, unmatched_dist = perform_fuzzy_matching(admin_df, dist_df)

    # Apply mapping to administered DataFrame
    admin_df['Woreda_Matched'] = admin_df['Woreda'].map(match_map)

    # Rename vaccine columns in distributed data to avoid merge conflicts
    dist_cols_to_keep = ['Region', 'Zone', 'Woreda', 'Period']
    dist_vaccine_cols = [col for col in dist_df.columns if col not in dist_cols_to_keep]

    # Rename columns to distinguish them from administered data
    dist_df = dist_df.rename(columns={col: f"{col}_Dist" for col in dist_vaccine_cols})
    
    # Merge on the fuzzy-matched Woreda name
    merged_df = pd.merge(
        admin_df, 
        dist_df, 
        left_on=['Woreda_Matched', 'Period'], 
        right_on=['Woreda', 'Period'], 
        how='inner',
        suffixes=('_Admin', '_Dist_Ignored') # Use suffixes to manage duplicate columns
    )

    # Get dataframes for unmatched records
    unmatched_admin_df = admin_df[admin_df['Woreda'].isin(unmatched_admin)].copy()
    unmatched_dist_df = dist_df[dist_df['Woreda'].isin(unmatched_dist)].copy()
    
    st.info(f"Fuzzy matching results:\n- Matched records: {len(merged_df)}\n- Unmatched Administered records: {len(unmatched_admin_df)}\n- Unmatched Distributed records: {len(unmatched_dist_df)}")

    return merged_df, unmatched_admin_df, unmatched_dist_df