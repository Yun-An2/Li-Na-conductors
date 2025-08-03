#!/usr/bin/env python3

import os
from pymatgen.io.cif import CifParser, CifWriter
from pymatgen.core import Structure, Composition, Element

def create_h_doped_materials(input_folder, output_folder, concentration=1.0):
    os.makedirs(output_folder, exist_ok=True)

    for cif_file in os.listdir(input_folder):
        if cif_file.endswith('.cif'):
            cif_path = os.path.join(input_folder, cif_file)
            structure = CifParser(cif_path).get_structures(primitive=False)[0]

            original_comp = structure.composition
            original_comp_dict = original_comp.as_dict()

            # Calculate the total number of Li and Na cations
            total_cations = sum(original_comp_dict.get(element, 0) for element in ['Li', 'Na'])

            # Calculate the number of H atoms needed to replace the set  concentration of Li/Na
            num_h_dopants = int(total_cations * concentration)

            # Track replacements
            replaced = 0
            species = [str(site.specie) for site in structure.sites]
            coords = structure.frac_coords.tolist()

            # Replace Li or Na with H
            for i, specie in enumerate(species):
                if specie in ['Li', 'Na']:
                    if replaced < num_h_dopants:
                        species[i] = 'H'
                        replaced += 1

            new_comp_dict = original_comp.as_dict()
            if 'Li' in new_comp_dict:
                new_comp_dict['Li'] = max(new_comp_dict['Li'] - replaced, 0)
            if 'Na' in new_comp_dict:
                new_comp_dict['Na'] = max(new_comp_dict['Na'] - replaced, 0)
            new_comp_dict['H'] = new_comp_dict.get('H', 0) + replaced

            new_comp = Composition(new_comp_dict)

            new_structure = Structure(
                lattice=structure.lattice,
                species=species,
                coords=coords,
                site_properties=structure.site_properties
            )

            # Generate the new CIF file name with the updated composition formula
            new_formula = ''.join(f"{el}{int(num)}" for el, num in new_comp.items())
            new_cif_file_name = f"{new_formula}_{cif_file.split('_')[-1]}"
            new_cif_file_path = os.path.join(output_folder, new_cif_file_name)

            cif_writer = CifWriter(new_structure)
            with open(new_cif_file_path, 'w') as f:
                f.write(f"# generated using pymatgen\n")
                f.write(f"data_{new_formula}\n")
                f.write(cif_writer.__str__())

            print(f"Saved H-doped CIF for {cif_file} as {new_cif_file_name}")
            print(f"Original composition: {original_comp}")
            print(f"New composition after H-doping: {new_comp}")

if __name__ == "__main__":
    large_bandgap_folder = "../First-screen/stable-materials"
    h_doped_folder = "H_doped_materials"

    create_h_doped_materials(large_bandgap_folder, h_doped_folder)

