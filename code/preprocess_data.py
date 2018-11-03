from collections import defaultdict
import os
import pickle
import sys

import numpy as np

from rdkit import Chem


def create_atoms(mol):
    atoms = [atom_dict[a.GetSymbol()] for a in mol.GetAtoms()]
    return np.array(atoms)


def create_adjacency(mol):
    adjacency = Chem.GetAdjacencyMatrix(mol)
    return np.array(adjacency)


def create_ijbonddict(mol):
    i_jbond_dict = defaultdict(lambda: [])
    for b in mol.GetBonds():
        i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
        bond = bond_dict[str(b.GetBondType())]
        i_jbond_dict[i].append((j, bond))
        i_jbond_dict[j].append((i, bond))
    return i_jbond_dict


def create_fingerprints(atoms, i_jbond_dict, radius):
    """Extract the r-radius subgraphs (i.e., fingerprints)
    from a molecular graph using WeisfeilerLehman-like algorithm."""

    if (len(atoms) == 1) or (radius == 0):
        return np.array(atoms)

    else:
        vertices = atoms
        for _ in range(radius):
            fingerprints = []
            for i, j_bond in i_jbond_dict.items():
                neighbors = [(vertices[j], bond) for j, bond in j_bond]
                fingerprint = (vertices[i], tuple(sorted(neighbors)))
                fingerprints.append(fingerprint_dict[fingerprint])
            vertices = fingerprints
        return np.array(fingerprints)


def split_sequence(sequence, ngram):
    words = [word_dict[sequence[i:i+ngram]]
             for i in range(len(sequence)-ngram+1)]
    return np.array(words)


def pickle_dump(dictionary, file_name):
    with open(file_name, 'wb') as f:
        pickle.dump(dict(dictionary), f)


if __name__ == "__main__":

    DATASET, radius, ngram = sys.argv[1:]
    radius, ngram = map(int, [radius, ngram])

    with open('../dataset/' + DATASET +
              '/original/smiles_sequence_interaction.txt', 'r') as f:
        data_list = f.read().strip().split('\n')
    N = len(data_list)

    atom_dict = defaultdict(lambda: len(atom_dict))
    bond_dict = defaultdict(lambda: len(bond_dict))
    fingerprint_dict = defaultdict(lambda: len(fingerprint_dict))
    word_dict = defaultdict(lambda: len(word_dict))

    Compounds, Adjacencies, Proteins, Interactions = [], [], [], []

    for no, data in enumerate(data_list):

        smiles, sequence, interaction = data.strip().split()

        """We exclude the data including '.' in the smiles."""
        if ('.' not in smiles):

            print('/'.join(map(str, [no, N])))

            mol = Chem.MolFromSmiles(smiles)
            atoms = create_atoms(mol)

            i_jbond_dict = create_ijbonddict(mol)

            fingerprints = create_fingerprints(atoms, i_jbond_dict, radius)
            Compounds.append(fingerprints)

            adjacency = create_adjacency(mol)
            Adjacencies.append(adjacency)

            words = split_sequence(sequence, ngram)
            Proteins.append(words)

            interaction = np.array([int(interaction)])
            Interactions.append(interaction)

    radius, ngram = str(radius), str(ngram)
    dir_input = ('../dataset/' + DATASET + '/input/radius' +
                 radius + '_ngram' + ngram + '/')
    if not os.path.isdir(dir_input):
        os.mkdir(dir_input)
    np.save(dir_input + 'compounds', Compounds)
    np.save(dir_input + 'adjacencies', Adjacencies)
    np.save(dir_input + 'proteins', Proteins)
    np.save(dir_input + 'interactions', Interactions)

    if (radius == 0):
        fingerprint_dict = atom_dict
    pickle_dump(fingerprint_dict, dir_input + 'fingerprint_dict' + '.pickle')
    pickle_dump(word_dict, dir_input + 'word_dict' + '.pickle')

    print('The preprocess has finished!')
