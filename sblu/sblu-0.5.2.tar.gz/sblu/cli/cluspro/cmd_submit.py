import logging
import click
import requests
import json

from sblu import CONFIG
from sblu.cli import make_sig

logger = logging.getLogger(__name__)

URL_SCHEME = "https"
API_ENDPOINT = "/api.php"
CP_CONFIG = CONFIG['cluspro']
FORM_KEYS = [
    'username', 'receptor', 'ligand', 'jobname', 'coeffs', 'rotations',
    'antibodymode', 'othersmode'
]
for f in ('pdb', '_chains', '_attraction', '_dssp'):
    FORM_KEYS.append("rec" + f)
    FORM_KEYS.append("lig" + f)
OPTIONAL_FILE_FIELDS = (
    ("coeffs", "coeff_file"),
    ("rotations", "rots_file"),
    ("restraints", "restraints_file"),
    ("saxs_file", "saxs_file")
)

@click.command('submit', short_help="Submit a job to ClusPro.")
@click.option("--username", default=CP_CONFIG['username'])
@click.option("--secret", default=CP_CONFIG['api_secret'])
@click.option("--server", default=CP_CONFIG['server'])
@click.option("--coeffs", type=click.Path(exists=True), default=None)
@click.option("--rotations", type=click.Path(exists=True), default=None)
@click.option("-j", "--jobname")
@click.option("-a", "--antibodymode", is_flag=True, default=False)
@click.option("-o", "--othersmode", is_flag=True, default=False)
@click.option("--receptor", type=click.Path(exists=True))
@click.option("--ligand", type=click.Path(exists=True))
@click.option("--recpdb")
@click.option("--ligpdb")
@click.option("--rec-chains")
@click.option("--lig-chains")
@click.option("--rec-attraction")
@click.option("--lig-attraction")
@click.option("--rec-dssp", is_flag=True, default=False)
@click.option("--lig-dssp", is_flag=True, default=False)
@click.option("--restraints", type=click.Path(exists=True), default=None)
@click.option("--saxs-file", type=click.Path(exists=True), default=None)
def cli(username, secret, server, coeffs, rotations, jobname, antibodymode,
        othersmode, receptor, recpdb, rec_chains, rec_attraction, rec_dssp,
        ligand, ligpdb, lig_chains, lig_attraction, lig_dssp,
        restraints, saxs_file):
    if username is None or username == "None" or secret is None or secret == "None":
        if username is None or username == "None":
            username = click.prompt("Please enter your cluspro username")
            CP_CONFIG['username'] = username
        if secret is None or secret == "None":
            secret = click.prompt("Please enter your cluspro api secret")
            CP_CONFIG['api_secret'] = secret
        CONFIG.write()

    if receptor is None and recpdb is None:
        raise click.BadOptionUsage("One of --receptor or --recpdb is required")
    if ligand is None and ligpdb is None:
        raise click.BadOptionUsage("One of --ligand or --ligpdb is required")

    form = {
        k: v
        for k, v in locals().items() if k in FORM_KEYS and v is not None
    }

    files = {}
    if form.get("receptor") is not None:
        files['rec'] = open(form['receptor'], 'rb')
        form['userecpdbid'] = '0'
    else:
        form['userecpdbid'] = '1'
    if form.get("ligand") is not None:
        files['lig'] = open(form['ligand'], 'rb')
        form['useligpdbid'] = '0'
    else:
        form['useligpdbid'] = '1'

    for form_key, files_key in OPTIONAL_FILE_FIELDS:
        if form.get(form_key) is not None:
            files[files_key] = open(form[form_key], 'rb')

    form['sig'] = make_sig(form, secret)

    api_address = "{0}://{1}{2}".format(URL_SCHEME, server, API_ENDPOINT)

    try:
        r = requests.post(api_address, data=form, files=files)
        result = json.loads(r.text)
        if result['status'] == 'success':
            print(result['id'])
        else:
            print(result['errors'])
            click.exit(1)
    except Exception as e:
        logger.error("Error submitting job: {}".format(e))
