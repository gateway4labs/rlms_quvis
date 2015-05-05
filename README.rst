QuVis plug-in
=====================

The `LabManager <http://github.com/gateway4labs/labmanager/>`_ provides an API for
supporting more Remote Laboratory Management Systems (RLMS). This project is the
implementation for the `QuVis: The University of St Andrews Quantum Mechanics Visualisation project
<http://www.st-andrews.ac.uk/physics/quvis//>`_ remote laboratory.

Usage
-----

First install the module::

  $ pip install git+https://github.com/gateway4labs/rlms_quvis.git

Then add it in the LabManager's ``config.py``::

  RLMS = ['quvis', ... ]

Profit!
