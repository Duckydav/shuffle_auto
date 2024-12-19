import nuke
import shuffle_auto

# Map the shortcuts
nuke.menu("Nuke").addCommand("Tools/Shuffle Auto", "shuffle_auto.run()", "V")
