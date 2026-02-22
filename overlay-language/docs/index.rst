Overlay Language
================

A dependency injection framework with pytest-fixture syntax, plus a
configuration language for declarative programming.

The configuration language is designed for modularity — independent modules
compose freely without glue code, dissolving the
`Expression Problem <https://en.wikipedia.org/wiki/Expression_problem>`_.
If you prefer declarative programming, you can even move all your business logic
from Python into the Overlay language — it is based on
`Overlay-Calculus <https://arxiv.org/abs/2602.16291>`_, which is provably more
expressive than λ-calculus. As a bonus, your Python code
reduces to thin I/O adapters, trivially mockable, and the same Overlay language
code runs unchanged on both sync and async runtimes
(a.k.a. `function-color <https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/>`_-blind).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   tutorial
   overlay-language-tutorial
   specification
   API Reference <api/overlay.language>
