#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lts_workflows_sm_scrnaseq
----------------------------------

Tests for `lts_workflows_sm_scrnaseq` module.
"""
from os.path import join
import subprocess as sp
import yaml
import pytest
from lts_workflows.pytest import factories, helpers
from lts_workflows.pytest.plugin import conda_environments
try:
    import pytest_ngsfixtures
    has_ngsfixtures = True
except:
    has_ngsfixtures = False

SNAKEFILE = join(pytest.examplesdir, "Snakefile")
CONFIG = join(pytest.examplesdir, "config.yaml")
SAMPLEINFO = join(pytest.examplesdir, "sampleinfo.csv")

stderr = sp.STDOUT if pytest.config.option.hide_workflow_output else None
stdout = sp.PIPE if pytest.config.option.hide_workflow_output else None

snakemakedata = factories.snakemake_core_setup(SNAKEFILE, CONFIG, sampleinfo=SAMPLEINFO)

def test_list(snakemakedata):
    helpers.snakemake_list(snakemakedata, "star_index")

@pytest.fixture(scope="function", autouse=False)
def data(request):
    d = request.getfuncargvalue(request.param)
    d.join("Snakefile").mksymlinkto(SNAKEFILE)
    d.join("config.yaml").mksymlinkto(CONFIG)
    with d.join("config.fmt.yaml").open("w") as fh:
        fh.write(yaml.dump({'settings': helpers.SNAKEMAKE_LAYOUTS.get(request.param,{'runfmt':'{SM}/{SM}_{PU}', 'samplefmt':'{SM}/{SM}'} )}, default_flow_style=False))
    return d


@pytest.mark.slow
@pytest.mark.skipif(not has_ngsfixtures, reason="pytest-ngsfixtures not installed; will not run the workflow tests. Install with 'conda install -c percyfal pytest-ngsfixtures'")
@pytest.mark.parametrize("data", pytest.config.getoption("ngs_layout", ["sample"]), indirect=["data"])
def test_run(data, ref, conda_environments):
    helpers.snakemake_run(data, stdout=stdout, stderr=stderr, threads=pytest.config.option.threads)
