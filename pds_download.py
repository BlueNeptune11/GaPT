from datetime import datetime
import pds.peppi as pep

client = pep.PDSRegistryClient()

date1 = datetime.fromisoformat("2012-01-23")
# mercury identifier in PDS, find it, in the type "target"
# in the `PDS keyword search <https://pds.nasa.gov/datasearch/keyword-search/search.jsp>`_
mercury_id = "urn:nasa:pds:context:target:planet.mercury"

# filter here:
products = pep.Products(client).has_target(mercury_id).before(date1).observationals()

for i, p in enumerate(products):
    print(p.id, p.investigations)
    # there a lot of data there, break after a couple of hundreds
    if i > 200:
        break