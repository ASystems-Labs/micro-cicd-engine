import logging, subprocess
from pathlib import Path

log = logging.getLogger("cicd")

class CommandError(RuntimeError): pass

class CommandRunner:
    def run(self, args, cwd=None):
        log.info("run: %s", " ".join(map(str,args)))
        p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
        if p.returncode:
            log.error("stderr: %s", p.stderr[-4000:])
            raise CommandError(f"command failed: {args[0]}")
        return p.stdout

class DeploymentPipeline:
    def __init__(self, runner, repo_dir, compose_file):
        self.runner, self.repo_dir, self.compose_file = runner, Path(repo_dir), compose_file

    def execute(self):
        self.runner.run(["git","fetch","--all","--prune"], cwd=self.repo_dir)
        self.runner.run(["git","reset","--hard","origin/HEAD"], cwd=self.repo_dir)
        self.runner.run(["python3","-m","pytest","-q"], cwd=self.repo_dir)
        self.runner.run(["docker","compose","-f",self.compose_file,"build"], cwd=self.repo_dir)
        self.runner.run(["docker","compose","-f",self.compose_file,"up","-d","--remove-orphans"], cwd=self.repo_dir)
        return {"status":"deployed"}
