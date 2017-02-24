import matplotlib.pyplot as plt
import anvil
import io

def plot_image():
  with io.BytesIO() as buf:
    plt.savefig(buf, format='png')
    buf.seek(0)    
    return anvil.BlobMedia('image/png', buf.read())
