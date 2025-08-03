#!/usr/bin/env python3

import os
from pymatgen.ext.matproj import MPRester
from pymatgen.io.cif import CifWriter

# Materials Project API key here
API_KEY = "xxx"   # Your API key from MP

# Initialize MPRester
def initialize_mpr(api_key):
    try:
        mpr = MPRester(api_key)
        return mpr
    except Exception as e:
        print(f"Failed to initialize MPRester: {e}")
        return None

# Function to search for Li/Na-containing compounds
def search_li_na_conductors():
    # Initialize MPRester
    mpr = initialize_mpr(API_KEY)

    if mpr is None:
        print("Error: MPRester could not be initialized. Please check your API key.")
        return

      # List to hold the combined results
    combined_results = []

    try:
        # Perform a search for materials containing Li along with other elements
        li_results = mpr.materials.summary.search(
            elements=["Li"],  # Search for systems containing Li
            fields=["material_id", "formula_pretty", "structure", "elements", "band_gap"]
        )

        # Perform a search for materials containing Na along with other elements
        na_results = mpr.materials.summary.search(
            elements=["Na"],  # Search for systems containing Na
            fields=["material_id", "formula_pretty", "structure", "elements", "band_gap"]
        )

        # Combine the results from both queries
        combined_results = li_results + na_results

    except Exception as e:
        print(f"Query failed: {e}")
        return

    # Check if we retrieved any materials
    if not combined_results:
        print("No materials found containing Li or Na along with other elements.")
        return

    # Initialize a list to hold screened materials
    screened_materials = []


    # Create output folders for both all retrieved materials and large bandgap materials
    all_output_folder = "Li-or-Na-ion-conductors"
    large_bandgap_folder = "large-bandgap-materials"
    os.makedirs(all_output_folder, exist_ok=True)  # Create the folder if it doesn't exist
    os.makedirs(large_bandgap_folder, exist_ok=True)  # Create the folder for large bandgap materials if it doesn't exist

    # Initialize lists to track filtered materials
    large_bandgap_materials = []

    for material in combined_results:
        material_id = material.material_id
        formula = material.formula_pretty
        structure = material.structure
        band_gap = material.band_gap if material.band_gap is not None else "Unknown"

        # Save all retrieved materials in 'Li-or-Na-ion-conductors'
        all_cif_file_name = os.path.join(all_output_folder, f"{formula}_{material_id}.cif")
        CifWriter(structure).write_file(all_cif_file_name)
        print(f"Saved CIF for {formula}, Material ID: {material_id}, Band Gap: {band_gap} (saved in '{all_output_folder}')")

        # Check if the band gap is greater than 2 eV for large bandgap materials
        if band_gap and band_gap > 2.0:
            large_bandgap_materials.append(material)
            # Writing CIF file for large bandgap materials
            large_cif_file_name = os.path.join(large_bandgap_folder, f"{formula}_{material_id}.cif")
            CifWriter(structure).write_file(large_cif_file_name)
            print(f"Saved CIF for {formula}, Material ID: {material_id}, Band Gap: {band_gap} (saved in '{large_bandgap_folder}')")

    print(f"Total materials saved in '{all_output_folder}': {len(combined_results)}")
    print(f"Total large bandgap materials saved in '{large_bandgap_folder}': {len(large_bandgap_materials)}")

if __name__ == "__main__":
    search_li_na_conductors()
