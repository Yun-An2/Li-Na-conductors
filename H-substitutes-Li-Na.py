#!/usr/bin/env python3

import os
from pymatgen.io.cif import CifParser, CifWriter
from pymatgen.core import Structure, Composition

def create_h_doped_materials(input_folder, output_folder, concentration=0.50):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all CIF files in the input folder
    for cif_file in os.listdir(input_folder):
        if cif_file.endswith('.cif'):
            # Parse the CIF file
            cif_path = os.path.join(input_folder, cif_file)
            structure = CifParser(cif_path).get_structures(primitive=False)[0]

            # Get the original composition
            original_comp = structure.composition
            original_comp_dict = original_comp.as_dict()

            # Calculate total number of Li and Na cations
            total_cations = sum(original_comp_dict.get(element, 0) for element in ['Li', 'Na'])
            # Calculate the number of H+ to be introduced based on the concentration
            num_h_dopants = int(total_cations * concentration)

            # Initialize `replaced` to keep track of how many atoms have been replaced
            replaced = 0

            # Create a list of atomic species and coordinates
            species = [str(site.specie) for site in structure.sites]
            coords = structure.frac_coords.tolist()

            # Replace Li or Na with H
            if num_h_dopants > 0:
                for i, specie in enumerate(species):
                    if specie in ['Li', 'Na']:
                        species[i] = 'H'  # Replace Li or Na with H
                        replaced += 1
                        if replaced >= num_h_dopants:
                            break

            # Check if the replacements were successful
            if replaced < num_h_dopants:
                print(f"Warning: Could not replace enough Li or Na atoms with H in {cif_file}.")

            # Update the composition after H doping
            new_comp_dict = original_comp_dict.copy()
            if 'Li' in new_comp_dict:
                new_comp_dict['Li'] = max(new_comp_dict['Li'] - replaced, 0)
            if 'Na' in new_comp_dict:
                new_comp_dict['Na'] = max(new_comp_dict['Na'] - replaced, 0)
            new_comp_dict['H'] = new_comp_dict.get('H', 0) + replaced

            new_comp = Composition(new_comp_dict)

            # Create a new structure with updated species
            if len(species) == len(coords):
                new_structure = Structure(
                    lattice=structure.lattice,
                    species=species,  # Replace species with updated list
                    coords=coords,
                    site_properties=structure.site_properties
                )

                # Modify the chemical formula after H doping
                new_formula = new_comp.reduced_formula

                # Save the new structure to a CIF file
                new_cif_file_name = f"H_doped_{cif_file}"
                new_cif_file_path = os.path.join(output_folder, new_cif_file_name)

                # Write the structure with updated formula and species
                cif_writer = CifWriter(new_structure)
                with open(new_cif_file_path, 'w') as f:
                    f.write(f"# generated using pymatgen\n")
                    f.write(f"data_{new_formula}\n")
                    f.write(cif_writer.__str__())

                print(f"Saved H-doped CIF for {cif_file} as {new_cif_file_name}")
                print(f"Original composition: {original_comp}")
                print(f"New composition after H-doping: {new_comp}")
            else:
                print(f"Warning: Mismatch detected in {cif_file}. Expected {len(species)} species, but got {len(coords)} coordinates.")

if __name__ == "__main__":
    large_bandgap_folder = "large-bandgap-materials"
    h_doped_folder = "H_doped_materials"

    create_h_doped_materials(large_bandgap_folder, h_doped_folder)

