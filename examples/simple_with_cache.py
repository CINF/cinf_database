from cinfdata import Cinfdata

db = Cinfdata('stm312', use_caching=True)
spectrum = db.get_data(6688)
metadata = db.get_metadata(6688)
