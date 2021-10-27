"""Base class for all FBC curators."""
import os

# from sys import platform
import platform
from collections import defaultdict, namedtuple
from datetime import date
from pathlib import Path
from typing import Dict, List

import cobra
import libsbml
import pandas as pd
from cobra.io import read_sbml_model
from pymetadata import log
from pymetadata.console import console

from fbc_curation import __citation__, __software__, __version__
from fbc_curation.frog import (
    FrogFVA,
    FrogGeneDeletions,
    FrogMetaData,
    FrogObjective,
    FrogReactionDeletions,
    FrogReport,
    Tool,
)


ObjectiveInformation = namedtuple(
    "ObjectiveInformation", "active_objective objective_ids"
)

logger = log.get_logger(__name__)


class Curator:
    """Base class of all Curator implementations."""

    def __init__(self, model_path: Path, objective_id: str = None):
        """Create instance."""
        if not model_path.exists():
            raise ValueError(f"model_path does not exist: '{model_path}'")

        self.model_path: Path = model_path
        self.model_location: str = f"./{self.model_path.name}"
        self.active_objective, self.objective_ids = Curator._read_objective_information(
            model_path
        )

        self.objective_id: str
        if objective_id is None:
            logger.warning(
                f"No objective id provided, using the active objective: "
                f"{self.active_objective}"
            )
            self.objective_id = self.active_objective
        else:
            if objective_id not in self.objective_ids:
                logger.error(
                    f"objective id does not exist in model: '{self.objective_id}', "
                    f"using the active objective: {self.active_objective}"
                )
                self.objective_id = self.active_objective
            else:
                self.objective_id = objective_id

    def __str__(self):
        """Create string representation."""
        lines = [
            f"--- {self.__class__.__name__} ---",
            f"\tmodel_path: {self.model_path}",
            f"\tobjective_id: {self.objective_id}",
        ]
        return "\n".join(lines)

    def read_model(self):
        raise NotImplementedError

    def metadata(self, software: Tool, solver: Tool) -> FrogMetaData:
        today = date.today()
        md = FrogMetaData(
            frog_date=date(year=today.year, month=today.month, day=today.day),
            frog_version="1.0",
            frog_curators=[],
            frog_software=Tool(
                name=__software__,
                version=__version__,
                url=__citation__,
            ),
            environment=f"{os.name}, {platform.system()}, {platform.release()}",
            model_filename=self.model_path.name,
            model_md5=FrogMetaData.md5_for_path(self.model_path),
            software=software,
            solver=solver,
        )

        return md

    def objective(self) -> FrogObjective:
        raise NotImplementedError

    def fva(self) -> FrogFVA:
        raise NotImplementedError

    def gene_deletions(self) -> FrogGeneDeletions:
        raise NotImplementedError

    def reaction_deletions(self) -> FrogReactionDeletions:
        raise NotImplementedError

    def run(self) -> FrogReport:
        """Run the curator and stores the results."""

        console.rule("CuratorResults", style="white")
        self._print_header(f"{self.__class__.__name__}: metadata")
        metadata = self.metadata()

        self._print_header(f"{self.__class__.__name__}: objective")
        objective = self.objective()

        self._print_header(f"{self.__class__.__name__}: fva")
        fva = self.fva()

        self._print_header(f"{self.__class__.__name__}: gene_deletion")
        gene_deletions = self.gene_deletions()

        self._print_header(f"{self.__class__.__name__}: reaction_deletion")
        reaction_deletions = self.reaction_deletions()

        return FrogReport(
            metadata=metadata,
            objective=objective,
            fva=fva,
            gene_deletions=gene_deletions,
            reaction_deletions=reaction_deletions,
        )

    # def _round_and_sort(self):
    #     """Round and sort."""
    #     # FIXME: processing must be done on creating the files ?!
    #     # round and sort objective value
    #     for key in ["value"]:
    #         self.objective[key] = self.objective[key].apply(self._round)
    #     self.objective.sort_values(by=["objective"], inplace=True)
    #
    #     # round and sort fva
    #     for key in ["flux", "minimum", "maximum"]:
    #         self.fva[key] = self.fva[key].apply(self._round)
    #     self.fva.sort_values(by=["reaction"], inplace=True)
    #     self.fva.index = range(len(self.fva))
    #
    #     # round and sort gene_deletion
    #     for key in ["value"]:
    #         self.gene_deletion[key] = self.gene_deletion[key].apply(self._round)
    #     self.gene_deletion.sort_values(by=["gene"], inplace=True)
    #     self.gene_deletion.index = range(len(self.gene_deletion))
    #
    #     # round and sort reaction deletion
    #     for key in ["value"]:
    #         self.reaction_deletion[key] = self.reaction_deletion[key].apply(self._round)
    #     self.reaction_deletion.sort_values(by=["reaction"], inplace=True)
    #     self.reaction_deletion.index = range(len(self.reaction_deletion))
    #
    #     # validate
    #     self.validate()
    #
    # def _round(self, x):
    #     """Round the float and sets small values positive.
    #
    #     Ensuring positivity removes -0.0, 0.0 changes to files.
    #     """
    #     if x == CuratorConstants.VALUE_INFEASIBLE:
    #         return x
    #     else:
    #         x = round(x, self.num_decimals)
    #         if abs(x) < 1e-10:
    #             x = abs(x)
    #         return x

    @staticmethod
    def _print_header(title):
        console.print(f"* {title}")

    @staticmethod
    def _knockout_reactions_for_genes(
        model_path: Path, genes=None
    ) -> Dict[str, List[str]]:
        """Calculate mapping of genes to affected reactions.

        Which reactions are knocked out by a given gene.
        A single gene knockout can affect multiple reactions.
        Uses GPR mappings.
        """
        model = read_sbml_model(str(model_path), f_replace={})  # type: cobra.core.Model
        if genes is None:
            genes = model.genes

        knockout_reactions = defaultdict(list)
        for reaction in model.reactions:  # type: cobra.core.Reaction
            gpr = reaction.gene_reaction_rule
            tree, gpr_genes = cobra.core.gene.parse_gpr(gpr)
            for gene in genes:  # type: cobra.core.Gene
                if gene.id not in gpr_genes:
                    gene_essential = False
                else:
                    # eval_gpr: True if the gene reaction rule is true with
                    # the given knockouts otherwise false
                    gene_essential = not cobra.core.gene.eval_gpr(
                        tree, knockouts={gene.id}
                    )
                if gene_essential:
                    knockout_reactions[gene.id].append(reaction.id)

        return knockout_reactions

    @staticmethod
    def _read_objective_information(model_path: Path) -> ObjectiveInformation:
        """Read objective information from SBML file structure."""
        # read objective information from sbml (multiple objectives)
        doc = libsbml.SBMLDocument = libsbml.readSBMLFromFile(str(model_path))
        model: libsbml.Model = doc.getModel()
        fbc_model: libsbml.FbcModelPlugin = model.getPlugin("fbc")
        if fbc_model is None:
            # model is an old SBML model without fbc information (use cobra default)
            # problems with the automatic up-conversions
            active_objective = "obj"
            objective_ids = ["obj"]
        else:
            active_objective = fbc_model.getActiveObjective().getId()
            objective_ids = []
            objective: libsbml.Objective
            for objective in fbc_model.getListOfObjectives():
                objective_ids.append(objective.getId())

        if len(objective_ids) > 1:
            logger.warning(
                f"Multiple objectives exist in SBML-fbc ({objective_ids}), "
                f"only active objective '{active_objective}' results "
                f"are reported"
            )
        return ObjectiveInformation(
            active_objective=active_objective, objective_ids=objective_ids
        )
