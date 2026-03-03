import json
from pathlib import Path


class ConfigService:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.config_dir = base_dir / "app_data"
        self.config_path = self.config_dir / "config.json"

    def carregar(self) -> dict[str, str]:
        if not self.config_path.exists():
            return {}

        try:
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def salvar_pasta_saida(self, pasta: str) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config = self.carregar()
        if pasta.strip():
            config["pasta_atendimentos"] = pasta.strip()
        else:
            config.pop("pasta_atendimentos", None)
        self.config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    def obter_pasta_saida(self, padrao: Path) -> Path:
        config = self.carregar()
        pasta_cfg = str(config.get("pasta_atendimentos", "")).strip()
        if pasta_cfg:
            return Path(pasta_cfg)
        return padrao
