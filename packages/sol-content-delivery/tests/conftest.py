#!/usr/bin/env python3
"""
sasci360apicore is an internal SAS CI360 package not published on public
PyPI (see requirements.txt). Tests mock it out entirely, but unittest.mock's
@patch still needs the target module importable to resolve the patch path.
Register a lightweight stub if the real package isn't installed.
"""

import sys
import types

if "sasci360apicore" not in sys.modules:
    try:
        import sasci360apicore  # noqa: F401
    except ImportError:
        apicore = types.ModuleType("sasci360apicore")
        encryption = types.ModuleType("sasci360apicore.encryption")

        class Encryption:
            def __init__(self, *args, **kwargs):
                pass

            def generate_jwt(self, *args, **kwargs):
                raise NotImplementedError("stub for testing only")

        encryption.Encryption = Encryption
        apicore.encryption = encryption

        sys.modules["sasci360apicore"] = apicore
        sys.modules["sasci360apicore.encryption"] = encryption
