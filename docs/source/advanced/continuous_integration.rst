.. _advanced-cis:


Continuous integration setup
============================

Testing PyVISA in a thorough manner is challenging due to the need to access both
a VISA library implementation and actual instruments to test against. In their
absence, tests are mostly limited to utility functions and infrastructure. Those
limited tests are found at the root of the testsuite package of pyvisa. They are
run, along with linters and documentation building on each commit using Github
Actions.

Thanks to Keysight tools provided to PyVISA developers, it is also possible to
test most capabilities of message based resources. However due to the hardware
requirements for the build bots, those tests cannot be set up on conventional
hosted CIs platform such as Travis, Azure, Github actions, etc.

Self-hosted builder can be used to run the tests requiring those tools. PyVISA
developer have chosen to use Azure Pipelines to run self-hosted runners. This
choice was based on the ease of use of Azure and the expected low maintenance the
builder should require since the CIs proper is handled through Azure. Github Actions
has also been considered but due to security reason, self-hosted runners should
not run on forks and Github Actions does not currently provide a way to forbid
running self-hosted runners on forks.

An Azure self-hosted runner has been set in place and will remain active till
December 2020. This runner can only test TCPIP based resources. A new runner will
be set up in the first trimester of 2021 with hopefully capabilities extended to
USB::INSTR and GPIB resources.

The setup of the current runner is not perfect and the runner may go offline at
times. If this happen, before December 2020, please contact @MatthieuDartiailh
on Github.

.. note::

    The current runner runs on Windows and uses conda. Due to the working of
    the activation scripts on Windows calls to `activate` or `conda activate`
    must be preceded by `call`.

