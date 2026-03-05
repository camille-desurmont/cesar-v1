"""Run acceptance tests via the main CESAR CLI.

Example: python -m model_acceptance_tests
Same as: cesar acceptance-tests run
"""

import sys

from cli.main import main

if __name__ == "__main__":
    sys.argv = ["cesar", "acceptance-tests", "run"]
    main()
