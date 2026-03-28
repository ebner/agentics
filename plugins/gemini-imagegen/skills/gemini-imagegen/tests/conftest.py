import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

# Stub out google.genai and google.genai.types so the scripts can be imported
# without the Gemini SDK installed.  We only test pure functions, never the API.
_google = types.ModuleType("google")
_google_genai = types.ModuleType("google.genai")
_google_genai_types = types.ModuleType("google.genai.types")

# Provide a minimal stand-in for types.ImageConfig and types.GenerateContentConfig
_google_genai_types.ImageConfig = MagicMock
_google_genai_types.GenerateContentConfig = MagicMock
_google_genai.types = _google_genai_types
_google_genai.Client = MagicMock
_google.genai = _google_genai

sys.modules.setdefault("google", _google)
sys.modules.setdefault("google.genai", _google_genai)
sys.modules.setdefault("google.genai.types", _google_genai_types)

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
