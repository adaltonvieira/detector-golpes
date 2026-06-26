import sys
from pathlib import Path

# Garante que a pasta src/ esteja no caminho de importacao,
# tanto localmente quanto no Streamlit Cloud.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

# Executa o app (o codigo da interface roda ao importar)
import app  # noqa: F401, E402
