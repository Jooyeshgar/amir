## \defgroup Utility
## @{

## Contain global object
class Share:
    mainwin = None
    config  = None
    session = None

    ##Get global object for sharing.
    # \param mainwin Amir main window object
    # \param config  amirconfig instance that contain all config data
    def __init__(self, mainwin=None, config=None):
        self.mainwin = mainwin
        self.config  = config
## @}

try:
    share
except NameError:
    share = Share()
