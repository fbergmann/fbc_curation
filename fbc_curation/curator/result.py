from pathlib import Path
from typing import Dict
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


from fbc_curation.constants import CuratorConstants


class CuratorResults:
    """
    Class for working with fbc curation results.
    CuratorResults can either be created by a Curator or read from file.
    """

    def __init__(self, objective_id: str, objective: pd.DataFrame, fva: pd.DataFrame,
                 gene_deletion: pd.DataFrame, reaction_deletion: pd.DataFrame,
                 num_decimals: int = None
                 ):
        self.objective_id = objective_id
        self.objective = objective
        self.fva = fva
        self.gene_deletion = gene_deletion
        self.reaction_deletion = reaction_deletion

        if not num_decimals:
            num_decimals = CuratorConstants.NUM_DECIMALS
        self.num_decimals = num_decimals


        # FIXME: processing must be done on creating the files ?!
        # round and sort objective value
        for key in ["value"]:
            self.objective[key] = self.objective[key].apply(self._round)
        self.objective.sort_values(by=['objective'], inplace=True)

        # round and sort fva
        for key in ["minimum", "maximum"]:
            self.fva[key] = self.fva[key].apply(self._round)
        self.fva.sort_values(by=['reaction'], inplace=True)
        self.fva.index = range(len(self.fva))

        # round and sort gene_deletion
        for key in ["value"]:
            self.gene_deletion[key] = self.gene_deletion[key].apply(self._round)
        self.gene_deletion.sort_values(by=['gene'], inplace=True)
        self.gene_deletion.index = range(len(self.gene_deletion))

        # round and sort reaction deletion
        for key in ["value"]:
            self.reaction_deletion[key] = self.reaction_deletion[key].apply(self._round)
        self.reaction_deletion.sort_values(by=['reaction'], inplace=True)
        self.reaction_deletion.index = range(len(self.reaction_deletion))

    def _round(self, x):
        if x == CuratorConstants.VALUE_INFEASIBLE:
            return x
        else:
            # FIXME: this creates a bug for negative values
            return abs(round(x, self.num_decimals))  # abs fixes the -0.0 | +0.0 diffs

    def write_results(self, path_out: Path):
        """Write results to path."""
        if not path_out.exists():
            logger.warning(f"Creating results path: {path_out}")
            path_out.mkdir(parents=True)
        for filename, df in dict(zip(
                [CuratorConstants.FILENAME_OBJECTIVE_FILE, CuratorConstants.FILENAME_FVA_FILE,
                 CuratorConstants.FILENAME_GENE_DELETION_FILE, CuratorConstants.FILENAME_REACTION_DELETION_FILE],
                [self.objective, self.fva, self.gene_deletion, self.reaction_deletion]
        )).items():
            print(f"-> {path_out / filename}")
            df.to_csv(path_out / filename, sep="\t", index=False)
        # self.objective.to_csv(path_out / CuratorConstants.FILENAME_OBJECTIVE_FILE, sep="\t", index=False)
        # self.fva.to_csv(path_out / CuratorConstants.FILENAME_FVA_FILE, sep="\t", index=False)
        # self.reaction_deletion.to_csv(path_out / CuratorConstants.FILENAME_REACTION_DELETION_FILE, sep="\t", index=False)
        # self.gene_deletion.to_csv(path_out / CuratorConstants.FILENAME_GENE_DELETION_FILE, sep="\t", index=False)

    @classmethod
    def read_results(cls, path_in: Path):
        """Read fbc curation files from given directory."""
        path_objective = path_in / CuratorConstants.FILENAME_OBJECTIVE_FILE
        path_fva = path_in / CuratorConstants.FILENAME_FVA_FILE
        path_gene_deletion = path_in / CuratorConstants.FILENAME_GENE_DELETION_FILE
        path_reaction_deletion = path_in / CuratorConstants.FILENAME_REACTION_DELETION_FILE
        df_dict = dict()

        for k, path in enumerate([path_objective, path_fva, path_gene_deletion, path_reaction_deletion]):
            if not path_objective.exists():
                logger.error(f"Required file for fbc curation does not exist: '{path}'")
            else:
                df_dict[CuratorConstants.KEYS[k]] = pd.read_csv(path, sep="\t")

        objective_id = df_dict['objective'].objective.values[0]

        return CuratorResults(objective_id=objective_id, **df_dict)

    @staticmethod
    def compare(results: Dict[str, 'CuratorResults']):
        """Compare results against each other"""
        print(results)
        curator_results = list(results.values())
        keys = list(results.keys())
        num_res = len(curator_results)
        # only comparing comparison between two data frames

        print(f"=" * 40)
        all_equal = True

        for key in CuratorConstants.KEYS:
            mat_equal = np.ndarray(shape=(num_res, num_res))
            for p, res1 in enumerate(curator_results):
                for q, res2 in enumerate(curator_results):
                    df1 = getattr(res1, key)
                    df2 = getattr(res2, key)
                    if df1.equals(df2):
                        mat_equal[p, q] = 1
                    else:
                        mat_equal[p, q] = 0

            df_equal = pd.DataFrame(mat_equal, columns=list(keys), index=list(keys), dtype=int)
            print(f"--- {key} ---")
            print(df_equal)
            all_equal = all_equal and np.sum(np.sum(df_equal.values)) == num_res*num_res

        print(f"=" * 40)
        print(f"Equal: {all_equal}")
        print(f"=" * 40)

    def __eq__(self, other):
        """Compare results."""
        pass
        # FIXME: implement

    def validate(self):
        pass
    # FIXME: implement



