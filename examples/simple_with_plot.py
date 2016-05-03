from cinfdata import Cinfdata
from matplotlib import pyplot as plt

db = Cinfdata('stm312', use_caching=True)
spectrum = db.get_data(6688)
metadata = db.get_metadata(6688)

plt.plot(spectrum[:,0], spectrum[:, 1])
plt.title(metadata['Comment'])
plt.show()
