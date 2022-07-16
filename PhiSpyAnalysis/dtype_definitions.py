"""
These are some definitions that make reading the datafiles faster and easier on the memory.

They are also ugly, so stored here!

"""

def phages_per_genome_dtypes_objects():
    return {'GENOMEID': 'str', 'Total_bp': 'Int64', 'Contigs': 'Int64', 'Contigs_Checked': 'Int64',
            'Total_Predicted_Prophages': 'Int64', 'Kept': 'Int64', 'No_phage_genes': 'Int64',
            'Not_enough_genes': 'Int64', 'bp_of_kept_prophages': 'Int64', 'bp_no_phage_genes': 'Int64',
            'bp_not_enough_genes': 'Int64', 'Note': 'str'}

def phages_per_genome_dtypes():
    return {'GENOMEID': 'str', 'Total_bp': 'int', 'Contigs': 'int', 'Contigs_Checked': 'int',
            'Total_Predicted_Prophages': 'int', 'Kept': 'int', 'No_phage_genes': 'int',
            'Not_enough_genes': 'int', 'bp_of_kept_prophages': 'int', 'bp_no_phage_genes': 'int',
            'bp_not_enough_genes': 'int', 'Note': 'str'}

def metadata_dtypes():
    return {'genome_id': 'float64', 'genome_name': 'str', 'organism_name': 'str', 'taxon_id': 'Int64',
            'genome_status': 'str', 'strain': 'str', 'serovar': 'str', 'biovar': 'str', 'pathovar': 'str',
            'mlst': 'str', 'other_typing': 'str', 'culture_collection': 'str', 'type_strain': 'str',
            'completion_date': 'str', 'publication': 'str', 'bioproject_accession': 'str', 'biosample_accession': 'str',
            'assembly_accession': 'str', 'genbank_accessions': 'str', 'refseq_accessions': 'str',
            'sequencing_centers': 'str', 'sequencing_status': 'str', 'sequencing_platform': 'str',
            'sequencing_depth': 'str', 'assembly_method': 'str', 'chromosomes': 'float64',
            'plasmids': 'float64', 'contigs': 'float64', 'sequences': 'float64', 'genome_length': 'float64',
            'gc_content': 'float64', 'patric_cds': 'float64', 'brc1_cds': 'float64', 'refseq_cds': 'float64',
            'isolation_site': 'str', 'isolation_source': 'str', 'isolation_comments': 'str',
            'collection_date': 'str', 'isolation_country': 'str', 'geographic_location': 'str', 'latitude': 'str',
            'longitude': 'str', 'altitude': 'str', 'depth': 'str', 'other_environmental': 'str', 'host_name': 'str',
            'host_gender': 'str', 'host_age': 'str', 'host_health': 'str', 'body_sample_site': 'str',
            'body_sample_subsite': 'str', 'other_clinical': 'str', 'antimicrobial_resistance': 'str',
            'antimicrobial_resistance_evidence': 'str', 'gram_stain': 'str', 'cell_shape': 'str',
            'motility': 'str', 'sporulation': 'str', 'temperature_range': 'str', 'optimal_temperature': 'str',
            'salinity': 'str', 'oxygen_requirement': 'str', 'habitat': 'str', 'disease': 'str', 'comments': 'str',
            'additional_metadata': 'str', 'isolation_date': 'float64'}

def gtdb_dtypes():
    return {'accession': 'str', 'ambiguous_bases': 'Int64', 'checkm_completeness': 'float64',
            'checkm_contamination': 'float64', 'checkm_marker_count': 'Int64', 'checkm_marker_lineage': 'str',
            'checkm_marker_set_count': 'Int64', 'checkm_strain_heterogeneity': 'float64', 'coding_bases': 'Int64',
            'coding_density': 'float64', 'contig_count': 'Int64', 'gc_count': 'Int64', 'gc_percentage': 'float64',
            'genome_size': 'Int64', 'gtdb_genome_representative': 'str', 'gtdb_representative': 'str',
            'gtdb_taxonomy': 'str', 'gtdb_type_designation': 'str', 'gtdb_type_designation_sources': 'str',
            'gtdb_type_species_of_genus': 'str', 'l50_contigs': 'Int64', 'l50_scaffolds': 'Int64',
            'longest_contig': 'Int64', 'longest_scaffold': 'Int64', 'lsu_23s_contig_len': 'float64',
            'lsu_23s_count': 'Int64', 'lsu_23s_length': 'float64', 'lsu_23s_query_id': 'str',
            'lsu_5s_contig_len': 'float64', 'lsu_5s_count': 'Int64', 'lsu_5s_length': 'float64',
            'lsu_5s_query_id': 'str', 'lsu_silva_23s_blast_align_len': 'float64',
            'lsu_silva_23s_blast_bitscore': 'float64', 'lsu_silva_23s_blast_evalue': 'float64',
            'lsu_silva_23s_blast_perc_identity': 'float64', 'lsu_silva_23s_blast_subject_id': 'str',
            'lsu_silva_23s_taxonomy': 'str', 'mean_contig_length': 'Int64', 'mean_scaffold_length': 'Int64',
            'mimag_high_quality': 'str', 'mimag_low_quality': 'str', 'mimag_medium_quality': 'str',
            'n50_contigs': 'Int64', 'n50_scaffolds': 'Int64', 'ncbi_assembly_level': 'str',
            'ncbi_assembly_name': 'str', 'ncbi_assembly_type': 'str', 'ncbi_bioproject': 'str',
            'ncbi_biosample': 'str', 'ncbi_contig_count': 'float64', 'ncbi_contig_n50': 'float64',
            'ncbi_country': 'str', 'ncbi_date': 'str', 'assembly_accession': 'str', 'ncbi_genbank_assembly_accession': 'str',
            'ncbi_genome_category': 'str', 'ncbi_genome_representation': 'str', 'ncbi_isolate': 'str',
            'ncbi_isolation_source': 'str', 'ncbi_lat_lon': 'str', 'ncbi_molecule_count': 'Int64',
            'ncbi_ncrna_count': 'float64', 'ncbi_organism_name': 'str', 'ncbi_protein_count': 'float64',
            'ncbi_refseq_category': 'str', 'ncbi_rrna_count': 'float64', 'ncbi_scaffold_count': 'float64',
            'ncbi_scaffold_l50': 'float64', 'ncbi_scaffold_n50': 'float64', 'ncbi_scaffold_n75': 'float64',
            'ncbi_scaffold_n90': 'float64', 'ncbi_seq_rel_date': 'str', 'ncbi_spanned_gaps': 'Int64',
            'ncbi_species_taxid': 'Int64', 'ncbi_ssu_count': 'float64', 'ncbi_strain_identifiers': 'str',
            'ncbi_submitter': 'str', 'ncbi_taxid': 'Int64', 'ncbi_taxonomy': 'str',
            'ncbi_taxonomy_unfiltered': 'str', 'ncbi_total_gap_length': 'Int64', 'ncbi_total_length': 'Int64',
            'ncbi_translation_table': 'float64', 'ncbi_trna_count': 'float64', 'ncbi_type_material_designation': 'str',
            'ncbi_ungapped_length': 'Int64', 'ncbi_unspanned_gaps': 'Int64', 'ncbi_wgs_master': 'str',
            'protein_count': 'Int64', 'scaffold_count': 'Int64', 'ssu_contig_len': 'float64',
            'ssu_count': 'Int64', 'ssu_gg_blast_align_len': 'float64', 'ssu_gg_blast_bitscore': 'float64',
            'ssu_gg_blast_evalue': 'float64', 'ssu_gg_blast_perc_identity': 'float64',
            'ssu_gg_blast_subject_id': 'float64', 'ssu_gg_taxonomy': 'str', 'ssu_length': 'float64',
            'ssu_query_id': 'str', 'ssu_silva_blast_align_len': 'float64', 'ssu_silva_blast_bitscore': 'float64',
            'ssu_silva_blast_evalue': 'float64', 'ssu_silva_blast_perc_identity': 'float64',
            'ssu_silva_blast_subject_id': 'str', 'ssu_silva_taxonomy': 'str',
            'total_gap_length': 'Int64', 'trna_aa_count': 'Int64', 'trna_count': 'Int64',
            'trna_selenocysteine_count': 'Int64'}

def phage_loc_dtypes():
        return {'GENOMEID':'str', 'Contig': 'str', 'Start': 'int', 'Stop': 'int', 'Length': 'int',
                '# CDS': 'int', 'Decision': 'str'}