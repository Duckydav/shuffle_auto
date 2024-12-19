import nuke
import shuffle

# Add a custom menu in Nuke
dd_tools_menu = nuke.menu('Nuke').addMenu('DD Tools')
dd_tools_menu.addCommand('Shuffle Auto', 'shuffle.run()', 'V')
