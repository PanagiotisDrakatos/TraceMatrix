import subprocess, json, tempfile, os

def run_theharvester(domain: str, limit: int = 100, source: str = "all"):
    """Εκτελεί theHarvester για ένα domain ή όνομα."""
    try:
        cmd = [
            "docker", "exec", "osint_stack_oss-theharvester-1",
            "theHarvester", "-d", domain, "-l", str(limit), "-b", source, "-f", "/results/out.json"
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=180)
        return {"status": "ok", "output": out}
    except Exception as e:
        return {"status": "error", "error": str(e)}
