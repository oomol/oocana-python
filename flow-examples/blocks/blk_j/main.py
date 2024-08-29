from oocana import Context
import matplotlib.pyplot as plt # 这个 block 需要手动安装 matplotlib


# "in", "out" is the default node key.
# Redefine the name and type of the node, change it manually below.
# Click on the gear(⚙) to configure the input output UI

def main(inputs: dict, context: Context):
  # inputs.get("in") -> help you get node input value
  fig, ax = plt.subplots()             # Create a figure containing a single Axes.
  ax.plot([1, 2, 3, 4], [1, 4, 2, 3])  # Plot some data on the Axes.
  plt.show()                           # Show the figure.
  return { "out": inputs }