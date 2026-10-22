import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ.get("SECRET_KEY", "cloud-guardian-secops-drift-secret-key-2026")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    
    # Paths
    DATABASE_PATH = BASE_DIR / "database" / "cloud_security.db"
    SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
    DATASET_DIR = BASE_DIR / "dataset"
    BASELINE_JSON = DATASET_DIR / "baseline_rules.json"
    CURRENT_JSON = DATASET_DIR / "current_rules.json"
    CSV_RULES = DATASET_DIR / "sample_security_rules.csv"
    REPORTS_DIR = BASE_DIR / "reports"
    
    # Risk policy definitions
    CRITICAL_PORTS = {
        22: "SSH (Administrative Remote Shell)",
        3389: "RDP (Remote Desktop Protocol)",
        0: "Wildcard Any Port (0-65535)"
    }
    
    HIGH_RISK_PORTS = {
        23: "Telnet (Unencrypted remote terminal)",
        21: "FTP (Unencrypted file transfer)",
        3306: "MySQL Database Port",
        5432: "PostgreSQL Database Port",
        1433: "MSSQL Database Port",
        1521: "Oracle DB Port",
        27017: "MongoDB Database Port",
        6379: "Redis Cache (Often unauthenticated)",
        9200: "Elasticsearch HTTP Port"
    }
    
    PERMISSIVE_CIDRS = ["0.0.0.0/0", "::/0", "any", "*", "Internet"]
