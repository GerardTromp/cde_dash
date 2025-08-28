import configparser
import json

class ValidatingConfig:
    def __init__(self, spec, filename=None):
        """
        spec: dict of parameter validation rules
              Example:
              {
                  "main": {
                      "param_int": {"type": "int", "min": 1, "max": 10},
                      "param_float": {"type": "float", "min": 0.0, "max": 1.0},
                      "param_str": {"type": "str", "choices": ["apple", "banana"]},
                      "param_bool": {"type": "bool"},
                  }
              }
        """
        self.config = configparser.ConfigParser()
        self.spec = spec
        if filename:
            self.load(filename)

    def load(self, filename):
        self.config.read(filename)

    def save(self, filename):
        with open(filename, "w") as f:
            self.config.write(f)

    def validate(self, section, option, value):
        if section not in self.spec or option not in self.spec[section]:
            # No spec → accept any string
            return value, None

        spec = self.spec[section][option]
        t = spec["type"]

        try:
            if t == "int":
                v = int(value)
                if "min" in spec and v < spec["min"]:
                    raise ValueError(f"{option} must be ≥ {spec['min']}")
                if "max" in spec and v > spec["max"]:
                    raise ValueError(f"{option} must be ≤ {spec['max']}")
                return str(v), None

            elif t == "float":
                v = float(value)
                if "min" in spec and v < spec["min"]:
                    raise ValueError(f"{option} must be ≥ {spec['min']}")
                if "max" in spec and v > spec["max"]:
                    raise ValueError(f"{option} must be ≤ {spec['max']}")
                return str(v), None

            elif t == "str":
                if "choices" in spec and value not in spec["choices"]:
                    raise ValueError(f"{option} must be one of {spec['choices']}")
                return str(value), None

            elif t == "bool":
                if str(value).lower() in ["true", "1", "yes", "on"]:
                    return "true", None
                elif str(value).lower() in ["false", "0", "no", "off"]:
                    return "false", None
                else:
                    raise ValueError(f"{option} must be true/false")

            elif t == "lr_float":
                # Allow special string values like "auto"
                if isinstance(value, str) and value.lower() in {"auto"}:
                    return value.lower(), None
    
                try:
                    v = float(value)
                except Exception:
                    raise ValueError(f"{option} must be a float or 'auto'")
    
                if "min" in spec and v < spec["min"]:
                    raise ValueError(f"{option} must be ≥ {spec['min']}")
                if "max" in spec and v > spec["max"]:
                    raise ValueError(f"{option} must be ≤ {spec['max']}")
    
                # Always store as string for ini
                return str(v), None

            elif t == "dict":
                if isinstance(value, dict):
                    return json.dumps(value), None
    
                if isinstance(value, str):
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, dict):
                            return json.dumps(parsed), None
                    except Exception:
                        raise ValueError(f"{option} must be valid JSON representing a dict")
    
                raise ValueError(f"{option} must be a dict or JSON string of a dict")

        except Exception as e:
            return None, str(e)

        return str(value), None

    def set(self, section, option, value):
        v, err = self.validate(section, option, value)
        if err:
            raise ValueError(f"Invalid value for {section}.{option}: {err}")
        if section not in self.config:
            self.config[section] = {}
        self.config[section][option] = v

    def get(self, section, option, fallback=None):
        if not self.config.has_option(section, option):
            return fallback

        value = self.config[section][option]
        spec = self.spec.get(section, {}).get(option)
        if not spec:
            return value

        t = spec["type"]
        if t == "int":
            return int(value)
        if t == "float":
            return float(value)
        if t == "bool":
            return value.lower() in ["true", "1", "yes", "on"]
        return value  # string