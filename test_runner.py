from pipeline.runner import DeploymentPipeline

class FakeRunner:
    def __init__(self): self.calls=[]
    def run(self,args,cwd=None): self.calls.append((args,cwd)); return ""

def test_pipeline_sequence():
    r=FakeRunner()
    p=DeploymentPipeline(r,"/repo","docker-compose.test.yml")
    assert p.execute()["status"]=="deployed"
    assert r.calls[0][0][:2]==["git","fetch"]
    assert any(c[0][0]=="pytest" or c[0][0]=="python3" and "pytest" in c[0] for c in r.calls)
    assert any(c[0][0]=="docker" for c in r.calls)
