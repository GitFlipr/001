"""
Convert YAML strategy files to NewBacktesting strategy classes
"""
import yaml
from pathlib import Path


def load_yaml_strategy(file_path: str) -> dict:
    with open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def convert_yaml_to_python(yaml_data: dict, output_dir: str = "."):
    """Convert YAML strategy definition to a Python strategy file"""
    strategy_name = yaml_data.get("strategy_name", "Strategy").replace(" ", "").replace("-", "_").replace("/", "_")
    description = yaml_data.get("description", "")
    params = yaml_data.get("parameters", {})

    # Extract parameters for __init__
    init_params = []
    param_defaults = []
    for cat, params_dict in params.items():
        for key, value in params_dict.items():
            if isinstance(value, dict):
                for subkey, subval in value.items():
                    param_name = f"{cat}_{key}_{subkey}" if cat != "indicators" else f"{key}_{subkey}"
                    init_params.append(param_name)
                    param_defaults.append(f"{param_name} = self.params.get('{param_name}', {repr(subval)})")
            else:
                init_params.append(key)
                param_defaults.append(f"{key} = self.params.get('{key}', {repr(value)})")

    # Generate Python code
    code = f'''"""
{description}
"""
import pandas as pd
from backtest.strategies.base import Strategy
from backtest.utils.indicators import sma, ema, rsi, bollinger_bands, macd, atr, crossover


class {strategy_name}(Strategy):
    """
    {description}
    """
    def __init__(self, params: dict = None):
        super().__init__(params)
        # Load parameters
'''
    for line in param_defaults:
        code += f"        {line}\n"

    code += '''

    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals"""
        df = self.data.copy()
        # TODO: Implement indicator calculations and signal generation based on rules
        # Add your indicator calculations here
        
        df["signal"] = 0
        return df[["signal"]]
'''
    output_path = Path(output_dir) / f"{strategy_name.lower()}.py"
    output_path.write_text(code, encoding="utf-8")
    return str(output_path)
