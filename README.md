Problem: Extracting detailed pathogenicity and ACMG classifications for multiple genetic variants from ClinVar can be tedious when performed manually.
Researchers and clinicians often need to gather  variant-level information (e.g., classification, molecular consequence, accession IDs) across hundreds of entries, 
this process that can’t be done efficiently through the web interface.

The tool:This Python script automates the retrieval of ClinVar data for a batch of variants provided in an Excel file.
It uses the NCBI E-utilities API to query ClinVar programmatically, returning structured data such as: Variation ID, Accession, Canonical SPDI, 
Gene Symbol, Chromosome, ACMG classification, and Molecular consequence. Results are saved in a new excel file.

Example:
input -  [Gene] CHD8 , [Variant] p.Arg1580Trp
output - ACMG class: Likely pathogenic , Variation ID: 1929445, canonical SPDI: NC_000014.9:21400059:G:A, Gene Symbol: CHD8, Chromosome 14, Molecular Consequence: Missense
