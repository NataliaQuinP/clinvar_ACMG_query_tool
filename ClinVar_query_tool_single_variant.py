# -*- coding: utf-8 -*-
"""

ClinVar Single Variant Query Tool
--------------------------
Author: Natalia Quintana Prieto
Description:
    This script queries the ClinVar database for a specific gene and variant in any format the variant is provided.
    It retrieves its ClinVar ID, and detailed variant information.

    This simple script handles cases where multiple genes share the same variant name
    by filtering results to only return records matching the specified gene.

Dependencies:
    - requests
    - urllib.parse

Example:
    $ python clinvar_query.py
    Enter the gene name (e.g., ASXL1): CHD8
    Enter your variant (Residue & Allele changes admitted): p.Arg1580Trp
"""

import requests
from urllib.parse import quote

#### ESEARCH  #############

def query_clinvar_for_specific_variant(gene_name, variant):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
   
   # variant = variant.split(':')[-1] 
   
    # Construct the search term
    search_term = f"{gene_name}[gene] AND {variant}[Variation Name]"
    encoded_term = quote(search_term)
    
    # Use esearch to find the specific variant
    esearch_url = f"{base_url}esearch.fcgi?db=clinvar&term={encoded_term}&retmode=json"
    #print("check the file:",{esearch_url})
    
    try:
        response = requests.get(esearch_url)
        response.raise_for_status()
        data = response.json()
        id_list = data['esearchresult'].get('idlist', [])
    except requests.exceptions.RequestException as e:
        return f"Error: Unable to search ClinVar. {str(e)}"
    
    if not id_list:
        return f"No variants found for gene: {gene_name}"
    
    #####ESUMMARY####### 

    for var_id in id_list:
        esummary_url = f"{base_url}esummary.fcgi?db=clinvar&id={var_id}&retmode=json"
        try:
            response = requests.get(esummary_url)
            response.raise_for_status()
            summary_data = response.json()
         
        except requests.exceptions.RequestException as e:
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
            
    #genes_in_record = [g['symbol'] for g in var_data.get('genes', []) if isinstance(g, dict)]
    if gene_name.upper() not in [g.upper() for g in gene_symbols]:
        return f"Variant found but not associated with gene {gene_name}. Found genes: {', '.join(gene_symbols)}"
            
    # Get canonical_spdi        
    variation_set=var_data.get('variation_set',[])
    cannonical_spid='N/A'
    if variation_set and isinstance(variation_set[0],dict):
        canonical_spdi=variation_set[0].get('canonical_spdi','NA')
    
    variant_info = {
        "Variation ID": var_id,
        "Accession": var_data.get('accession', 'N/A'),
        "Title": var_data.get('title', 'N/A'),
        "Canonical spdi": canonical_spdi,
        "Gene Symbol": ', '.join(gene_symbols),
        "Chromosome": var_data.get('chr_sort', 'N/A'),
        "ACMG score": var_data.get('germline_classification', {}).get('description', 'N/A'),
        "Molecular Consequence":var_data.get('molecular_consequence_list','N/A')
    }
    
    return variant_info


############ MAIN USER INTERFACE ##################

def main():
    gene_name = input("Enter the gene name (e.g., ASXL1): ")
    variant = input("Enter your variant(Residue & Allele changes admitted):  ")
    
    result = query_clinvar_for_specific_variant(gene_name, variant)
    
    if isinstance(result, dict):
        print("\nDetailed Variant Information:")
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print(result)  # This will print the error message if no variant was found

if __name__ == "__main__":
    main()