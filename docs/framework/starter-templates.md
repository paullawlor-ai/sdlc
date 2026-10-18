# Starter Template Compatibility

Starter projects support Python 3.10 through 3.13. Framework CI installs every
template from its checked-in `requirements.txt`, imports or starts its primary
entry point without external network calls, and runs its tests on Python 3.12.
The framework itself runs its full test suite on every supported Python version.

Runtime dependencies use bounded compatible ranges. Review dependency updates at
least quarterly and before a framework release. Patch and minor updates may be
accepted after all starter smoke tests pass. Major updates require a change
proposal that records migration impact, security review, and rollback steps.

The chatbot's RAG libraries are included for a complete example but are loaded
only when RAG is enabled. Starter safety checks are educational defaults, not a
claim that a production security control is complete without application-specific
threat modelling, monitoring, and tests.
