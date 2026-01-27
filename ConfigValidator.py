from typing import List, Dict, Callable

class Config:
    """Represents a service configuration with basic safety defaults."""
    def __init__(self, data: Dict):
        # Using .get() prevents KeyErrors if a developer misses a field
        self.service = data.get("service", "unknown-service")
        self.env = data.get("env", "dev")
        self.cpu = data.get("cpu", 0)
        self.memory = data.get("memory", 0)
        self.replicas = data.get("replicas", 0)
        self.security_group = data.get("security_group", None)

class ConfigValidator:
    def __init__(self):
        # We define rules as a list of functions. 
        # Adding a new rule is now as simple as adding a function to this list.
        self.rules: List[Callable[[Config], str]] = [
            self._check_cpu_memory_ratio,
            self._check_prod_replicas,
            self._check_security_group
        ]

    def _check_cpu_memory_ratio(self, c: Config) -> str:
        if c.memory < (c.cpu * 2):
            return f"Resource Error: Memory ({c.memory}GB) must be at least 2x CPU ({c.cpu})"
        return None

    def _check_prod_replicas(self, c: Config) -> str:
        if c.env == "prod" and c.replicas < 3:
            return f"Reliability Error: Prod requires at least 3 replicas, found {c.replicas}"
        return None

    def _check_security_group(self, c: Config) -> str:
        if not c.security_group:
            return "Security Error: Missing security_group"
        if c.env == "prod" and c.security_group == "default":
            return "Security Error: 'default' security group is blocked in prod"
        return None

    def validate(self, raw_configs: List[Dict]):
        report = {"Deployable": [], "Blocked": [], "Warnings": []}

        for data in raw_configs:
            config = Config(data)
            errors = []

            # Run all rules against the config
            for rule in self.rules:
                error = rule(config)
                if error:
                    errors.append(error)

            # Categorize the result
            if errors:
                report["Blocked"].append({
                    "service": config.service,
                    "reasons": errors
                })
            else:
                # Add a warning if SG is default in non-prod
                if config.security_group == "default":
                    report["Warnings"].append(f"{config.service}: Using default SG in {config.env}")
                
                report["Deployable"].append(config.service)

        return report

# --- Example Usage ---
raw_data = [
    {"service": "auth-api", "env": "prod", "cpu": 2, "memory": 8, "replicas": 3, "security_group": "web-sg"},
    {"service": "data-worker", "env": "dev", "cpu": 1, "memory": 1, "replicas": 1, "security_group": "default"},
    {"service": "cache-node", "env": "prod", "cpu": 1, "memory": 4, "replicas": 2, "security_group": "cache-sg"}
]

validator = ConfigValidator()
results = validator.validate(raw_data)

import json
print(json.dumps(results, indent=2))