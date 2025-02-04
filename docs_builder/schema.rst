JSON Schema
===========
The JSON schema for FROG version 1 is available from
`frog-schema-version-1.json <https://raw.githubusercontent.com/matthiaskoenig/fbc_curation/develop/src/fbc_curation/resources/schema/frog-schema-version-1.json>`__

.. code:: json

    {
      "title": "FrogReport",
      "description": "Definition of the FROG standard.",
      "type": "object",
      "properties": {
        "metadata": {
          "$ref": "#/definitions/FrogMetaData"
        },
        "objectives": {
          "$ref": "#/definitions/FrogObjectives"
        },
        "fva": {
          "$ref": "#/definitions/FrogFVA"
        },
        "reaction_deletions": {
          "$ref": "#/definitions/FrogReactionDeletions"
        },
        "gene_deletions": {
          "$ref": "#/definitions/FrogGeneDeletions"
        }
      },
      "required": [
        "metadata",
        "objectives",
        "fva",
        "reaction_deletions",
        "gene_deletions"
      ],
      "definitions": {
        "Tool": {
          "title": "Tool",
          "description": "Tool description.",
          "type": "object",
          "properties": {
            "name": {
              "title": "Name",
              "description": "Name of tool/software/library.",
              "type": "string"
            },
            "version": {
              "title": "Version",
              "description": "Version of tool/software/library.",
              "type": "string"
            },
            "url": {
              "title": "Url",
              "description": "URL of tool/software/library.",
              "type": "string"
            }
          },
          "required": [
            "name"
          ]
        },
        "Creator": {
          "title": "Creator",
          "description": "Creator/curator in ModelHistory and other COMBINE formats.\n\nExtended by optional orcid.",
          "type": "object",
          "properties": {
            "familyName": {
              "title": "Familyname",
              "type": "string"
            },
            "givenName": {
              "title": "Givenname",
              "type": "string"
            },
            "email": {
              "title": "Email",
              "type": "string"
            },
            "organization": {
              "title": "Organization",
              "type": "string"
            },
            "site": {
              "title": "Site",
              "type": "string"
            },
            "orcid": {
              "title": "Orcid",
              "type": "string"
            }
          },
          "required": [
            "familyName",
            "givenName"
          ]
        },
        "FrogMetaData": {
          "title": "FrogMetaData",
          "description": "FROG metadata.",
          "type": "object",
          "properties": {
            "model.location": {
              "title": "Model.Location",
              "description": "Location of the model in the COMBINE archive for which the FROG analysis was performed.",
              "type": "string"
            },
            "model.md5": {
              "title": "Model.Md5",
              "description": "MD5 hash of model",
              "type": "string"
            },
            "frog_id": {
              "title": "Frog Id",
              "description": "Id for the FROG analysis. All frog_ids within an archive must be unique.",
              "type": "string"
            },
            "frog.software": {
              "title": "Frog.Software",
              "description": "Software used to run FROG (e.g. 'fbc_curation'",
              "allOf": [
                {
                  "$ref": "#/definitions/Tool"
                }
              ]
            },
            "frog.curators": {
              "title": "Frog.Curators",
              "description": "Curators which executed the FROG analysis.",
              "type": "array",
              "items": {
                "$ref": "#/definitions/Creator"
              }
            },
            "software": {
              "title": "Software",
              "description": "Software used to run FBC (e.g. 'cameo', 'COBRA', 'cobrapy'",
              "allOf": [
                {
                  "$ref": "#/definitions/Tool"
                }
              ]
            },
            "solver": {
              "title": "Solver",
              "description": "Solver used to solve LP problem (e.g. 'CPLEX', 'GUROBI', 'GLPK').",
              "allOf": [
                {
                  "$ref": "#/definitions/Tool"
                }
              ]
            },
            "environment": {
              "title": "Environment",
              "description": "Execution environment such as Linux.",
              "type": "string"
            }
          },
          "required": [
            "model.location",
            "frog_id",
            "frog.software",
            "frog.curators",
            "software",
            "solver"
          ]
        },
        "StatusCode": {
          "title": "StatusCode",
          "description": "Status code for simulation results.",
          "enum": [
            "optimal",
            "infeasible"
          ],
          "type": "string"
        },
        "FrogObjective": {
          "title": "FrogObjective",
          "description": "Frog Objective.",
          "type": "object",
          "properties": {
            "model": {
              "title": "Model",
              "type": "string"
            },
            "objective": {
              "title": "Objective",
              "type": "string"
            },
            "status": {
              "$ref": "#/definitions/StatusCode"
            },
            "value": {
              "title": "Value",
              "type": "number"
            }
          },
          "required": [
            "model",
            "objective",
            "status",
            "value"
          ]
        },
        "FrogObjectives": {
          "title": "FrogObjectives",
          "description": "Definition of FROG Objectives.",
          "type": "object",
          "properties": {
            "objectives": {
              "title": "Objectives",
              "type": "array",
              "items": {
                "$ref": "#/definitions/FrogObjective"
              }
            }
          },
          "required": [
            "objectives"
          ]
        },
        "FrogFVASingle": {
          "title": "FrogFVASingle",
          "description": "Frog FVA.",
          "type": "object",
          "properties": {
            "model": {
              "title": "Model",
              "type": "string"
            },
            "objective": {
              "title": "Objective",
              "type": "string"
            },
            "reaction": {
              "title": "Reaction",
              "type": "string"
            },
            "flux": {
              "title": "Flux",
              "type": "number"
            },
            "status": {
              "$ref": "#/definitions/StatusCode"
            },
            "minimum": {
              "title": "Minimum",
              "type": "number"
            },
            "maximum": {
              "title": "Maximum",
              "type": "number"
            },
            "fraction_optimum": {
              "title": "Fraction Optimum",
              "type": "number"
            }
          },
          "required": [
            "model",
            "objective",
            "reaction",
            "status",
            "fraction_optimum"
          ]
        },
        "FrogFVA": {
          "title": "FrogFVA",
          "description": "Definition of FROG FVA.",
          "type": "object",
          "properties": {
            "fva": {
              "title": "Fva",
              "type": "array",
              "items": {
                "$ref": "#/definitions/FrogFVASingle"
              }
            }
          },
          "required": [
            "fva"
          ]
        },
        "FrogReactionDeletion": {
          "title": "FrogReactionDeletion",
          "description": "Frog reaction deletion.",
          "type": "object",
          "properties": {
            "model": {
              "title": "Model",
              "type": "string"
            },
            "objective": {
              "title": "Objective",
              "type": "string"
            },
            "reaction": {
              "title": "Reaction",
              "type": "string"
            },
            "status": {
              "$ref": "#/definitions/StatusCode"
            },
            "value": {
              "title": "Value",
              "type": "number"
            }
          },
          "required": [
            "model",
            "objective",
            "reaction",
            "status"
          ]
        },
        "FrogReactionDeletions": {
          "title": "FrogReactionDeletions",
          "description": "Definition of FROG Reaction deletions.",
          "type": "object",
          "properties": {
            "deletions": {
              "title": "Deletions",
              "type": "array",
              "items": {
                "$ref": "#/definitions/FrogReactionDeletion"
              }
            }
          },
          "required": [
            "deletions"
          ]
        },
        "FrogGeneDeletion": {
          "title": "FrogGeneDeletion",
          "description": "Frog gene deletion.",
          "type": "object",
          "properties": {
            "model": {
              "title": "Model",
              "type": "string"
            },
            "objective": {
              "title": "Objective",
              "type": "string"
            },
            "gene": {
              "title": "Gene",
              "type": "string"
            },
            "status": {
              "$ref": "#/definitions/StatusCode"
            },
            "value": {
              "title": "Value",
              "type": "number"
            }
          },
          "required": [
            "model",
            "objective",
            "gene",
            "status"
          ]
        },
        "FrogGeneDeletions": {
          "title": "FrogGeneDeletions",
          "description": "Definition of FROG Gene deletions.",
          "type": "object",
          "properties": {
            "deletions": {
              "title": "Deletions",
              "type": "array",
              "items": {
                "$ref": "#/definitions/FrogGeneDeletion"
              }
            }
          },
          "required": [
            "deletions"
          ]
        }
      }
    }
