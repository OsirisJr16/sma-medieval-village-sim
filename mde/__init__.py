"""Model-Driven Engineering (MDE) package.

Holds the artifacts for a future code-generation pipeline:

* ``uml/`` — source UML models (e.g. class/state diagrams).
* ``templates/`` — code-generation templates.
* ``generated/`` — output produced by the generator (git-ignored).

The pipeline (parse UML -> apply templates -> emit code) is not implemented yet;
this package reserves the structure so it can be added without reorganizing the
project.
"""
