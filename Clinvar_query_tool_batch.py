# -*- coding: utf-8 -*-
"""
ClinVar Single & Batch Variant Query Tool
-----------------------------------------
Author: Natalia Quintana Prieto
Created: September 18, 2024
Last Updated: October 2025

Description:
    This script queries the ClinVar database for one or more variants based on gene name
    and variant notation (e.g., protein change, nucleotide change, or residue format).
    It retrieves each variant's ClinVar ID, accession, canonical SPDI, ACMG classification,
    and molecular consequence using NCBI's E-utilities API.

    The tool can be used in two modes:
        1. **Single Mode:** Enter a single gene and variant manually.
        2. **Batch Mode:** Provide an Excel file containing multiple genes and variants.
           The script will query all entries and output the results to a new Excel file.

Dependencies:
    - requests
    - urllib.parse
    - pandas
    - openpyxl (for Excel input/output)

Example:
    $ python clinvar_query.py
    Type 'batch' for Excel input or 'single' for manual entry: single
    Enter the gene name (e.g., ASXL1): CHD8
    Enter your variant (Residue & Allele changes admitted): p.Arg1580Trp

Batch Mode Example:
    $ python clinvar_query.py
    Type 'batch' for Excel input or 'single' for manual entry: batch
    Enter the path to your Excel file (e.g., variants.xlsx): variant_input.xlsx
    Enter the output Excel filename (e.g., clinvar_results.xlsx): variant_output.xlsx

Expected Input Excel Format:
    | Gene | Variant       |
    |------|---------------|
    | CHD8 | p.Arg1580Trp  |
    | ASXL1 | p.Gly646TrpfsTer12 |


"""
import requests
from urllib.parse import quote
import pandas as pd
from time import sleep

def query_clinvar_for_specific_variant(gene_name, variant):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_term = f"{gene_name}[gene] AND {variant}[Variation Name]"
    encoded_term = quote(search_term)
    
    # eSearch to find the specific variant
    esearch_url = f"{base_url}esearch.fcgi?db=clinvar&term={encoded_term}&retmode=json"
    
    
    try:
        response = requests.get(esearch_url)
        response.raise_for_status()
        data = response.json()
        id_list = data['esearchresult'].get('idlist', [])
    except requests.exceptions.RequestException as e:
        return {"Gene": gene_name, "Variant": variant, "Error": f"Unable to search ClinVar: {str(e)}"}
    
    if not id_list:
        return {"Gene": gene_name, "Variant": variant, "Error": f"No variants found for gene: {gene_name}"}

    for var_id in id_list:
        esummary_url = f"{base_url}esummary.fcgi?db=clinvar&id={var_id}&retmode=json"
        try:
           response = requests.get(esummary_url)
           response.raise_for_status()
           summary_data = response.json()
        except requests.exceptions.RequestException:
            continue
    
        var_data = summary_data['result'].get(var_id, {})
        if not var_data:
           continue
    
    # Extract gene symbols
        gene_symbols = []
        for gene in var_data.get('genes', []):
            if isinstance(gene, dict):
               gene_symbols.append(gene.get('symbol', ''))
            elif isinstance(gene, str):
                 gene_symbols.append(gene)
            
        if gene_name.upper() not in [g.upper() for g in gene_symbols]:
           continue
       
        title = var_data.get("title", "")
        if "del" in title.lower() or "dup" in title.lower():
           continue
    
    # Get canonical_spdi        
        variation_set = var_data.get('variation_set', [])
        canonical_spdi = 'N/A'
        if variation_set and isinstance(variation_set[0], dict):
           canonical_spdi = variation_set[0].get('canonical_spdi', 'N/A')
    
        return {
           "Gene": gene_name,
           "Variant": variant,
           "Variation ID": var_id,
           "Accession": var_data.get('accession', 'N/A'),
           "Title": var_data.get('title', 'N/A'),
           "Canonical spdi": canonical_spdi,
           "Gene Symbol": ', '.join(gene_symbols),
           "Chromosome": var_data.get('chr_sort', 'N/A'),
           "ACMG score": var_data.get('germline_classification', {}).get('description', 'N/A'),
           "Molecular Consequence": ', '.join(var_data.get('molecular_consequence_list', ['N/A']))
           }
    return {"Gene": gene_name, "Variant": variant, "Error": "No matching ClinVar record for gene"}

def batch_query_from_excel(input_path, output_path):
    print(f"Opening file: {input_path}")
    df = pd.read_excel(input_path)
    print("Columns detected:", list(df.columns))
    print("Preview:\n", df.head())
    results = []

    for _, row in df.iterrows():
        gene = str(row.get("Gene", "")).strip()
        variant = str(row.get("Variant", "")).strip()
        if not gene or not variant:
            continue

        print(f"Querying {gene} - {variant}...")
        result = query_clinvar_for_specific_variant(gene, variant)
        results.append(result)
        sleep(1)  # small pause to avoid hitting API rate limits

    results_df = pd.DataFrame(results)
    results_df.to_excel(output_path, index=False)
    print(f"\nResults saved to: {output_path}")
    
if __name__ == "__main__":
    mode = input("Type 'batch' for Excel input or 'single' for manual entry: ").strip().lower()

    if mode == "batch":
        input_path = input("Enter the path to your Excel file (e.g., variants.xlsx): ")
        output_path = input("Enter the output Excel filename (e.g., clinvar_results.xlsx): ")
        batch_query_from_excel(input_path, output_path)

    else:
        gene_name = input("Enter the gene name: ")
        variant = input("Enter your variant: ")
        result = query_clinvar_for_specific_variant(gene_name, variant)
        print(result)