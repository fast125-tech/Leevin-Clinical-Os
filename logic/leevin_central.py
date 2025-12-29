from .brain_cdm import BrainCDM
from .brain_cra import BrainCRA
from .brain_site import BrainSite
from .brain_coder import BrainCoder
from .brain_writer import BrainWriter

class LeevinCentral:
    def __init__(self):
        self.cdm = BrainCDM()
        self.cra = BrainCRA()
        self.site = BrainSite()
        self.coder = BrainCoder()
        self.writer = BrainWriter()
