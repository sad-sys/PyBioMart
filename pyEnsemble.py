import requests
from lxml import etree

# Custom Mart class to store relevant information
class Mart:
    def __init__(self, dataset, biomart, host=None, http_config=None):
        self.dataset = dataset
        self.biomart = biomart
        self.host = host
        self.http_config = http_config

def mart_check(mart, biomart=None):
    if mart is None or not isinstance(mart, Mart):
        raise ValueError("You must provide a valid Mart object. To create a Mart object use the function: useMart. Check ?useMart for more information.")
    
    if biomart is not None:
        if mart.biomart not in biomart:
            raise ValueError(f"This function only works when used with the {biomart} BioMart.")
    
    if mart.dataset == "":
        raise ValueError("No dataset selected, please select a dataset first. You can see the available datasets by using the listDatasets function see ?listDatasets for more information. Then you should create the Mart object by using the useMart function. See ?useMart for more information")

def bm_request(request, http_config=None, verbose=False):
    if verbose:
        print(f"Attempting web service request:\n{request}")
    response = requests.get(request, **(http_config or {}))
    response.raise_for_status()
    return response.text

def clean_host_url(host, warn=True):
    if not host.startswith("http://") and not host.startswith("https://"):
        host = "http://" + host
    if host.endswith("/"):
        host = host.rstrip("/")
    return host

def list_marts(mart=None, host="https://www.ensembl.org", path="/biomart/martservice", port=None, include_hosts=False, archive=False, http_config=None, verbose=False):
    if port is None:
        port = 443 if "https" in host else 80

    if "https://.*ensembl.org" in host and http_config is None:
        http_config = {"verify": True}  # Assuming getEnsemblSSL()

    if http_config is None:
        http_config = {}

    return _list_marts(mart=mart, host=host, path=path, port=port, include_hosts=include_hosts, archive=archive, verbose=verbose, http_config=http_config, ensembl_redirect=True)

def _list_marts(mart=None, host="www.ensembl.org", path="/biomart/martservice", port=80, include_hosts=False, archive=False, verbose=False, http_config=None, ensembl_redirect=None, warn=True):
    request = None
    if mart is None:
        host = clean_host_url(host, warn=warn)
        if archive:
            raise ValueError("The archive = TRUE argument is now defunct. Use listEnsemblArchives() to find the URL to directly query an Ensembl archive.")
        else:
            if port == 443:
                request = f"{host}{path}?type=registry&requestid=biomaRt"
            else:
                request = f"{host}:{port}{path}?type=registry&requestid=biomaRt"
    elif isinstance(mart, Mart):
        request = f"{mart.host}?type=registry&requestid=biomaRt"
        http_config = mart.http_config
    else:
        raise ValueError(f"{mart} object needs to be of class Mart created with the useMart function. If you don't have a Mart object yet, use listMarts() without arguments or only specify the host argument")

    if not ensembl_redirect and "ensembl.org" in request:
        request = f"{request}&redirect=no"

    registry = bm_request(request=request, http_config=http_config, verbose=verbose)

    if "<MartRegistry>" not in registry:
        print(f"Unexpected registry response: {registry}")
        if "status.ensembl.org" in registry:
            raise RuntimeError("Your query has been redirected to http://status.ensembl.org indicating this Ensembl service is currently unavailable. Look at useEnsembl for details on how to try a mirror site.")
        else:
            raise RuntimeError(f'Unexpected format to the list of available marts. Please check the following URL manually, and try listMarts for advice: {request}')

    registry_xml = etree.fromstring(registry)
    marts = []
    for child in registry_xml:
        if child.attrib.get("visible") == "1":
            marts.append({
                "biomart": child.attrib.get("name"),
                "version": child.attrib.get("displayName"),
                "vschema": child.attrib.get("serverVirtualSchema")
            })

    if include_hosts:
        return marts
    else:
        return [{ "biomart": mart["biomart"], "version": mart["version"] } for mart in marts]

# Example usage
if __name__ == "__main__":
    # Create a Mart object for testing
    mart = Mart(dataset="example_dataset", biomart="ensembl")

    # Test mart_check function
    try:
        mart_check(mart, biomart=["ensembl", "other_biomart"])
        print("Mart check passed.")
    except ValueError as e:
        print(e)

    # Test list_marts function
    try:
        marts = list_marts()
        print(marts)
    except RuntimeError as e:
        print(e)
