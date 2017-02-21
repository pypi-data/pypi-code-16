from os import path

from experipy.system import python_script
from experipy        import Experiment

if __name__ == "__main__":
    testscript = path.join(path.dirname(__file__), "test.py")
    
    script = python_script(testscript, outputs=["test.out"])
    
    Experiment(script, "test",
        path.join(path.dirname(__file__), "results")
    ).run(rm_rundir=False)
