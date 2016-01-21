from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_ReviewQueueWidget import Ui_ReviewQueueWidget
from AddressList import AddressListModel
import Controller

class ReviewQueueWidget( Ui_ReviewQueueWidget, QWidget ):

    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self._addressListModel = AddressListModel()
        self._addressListModel.setColumns(
          ['id','version', 'displayNum', 'displayRoad', 'submittedDate', 'changeTypeName', 'addressType', 'suburbLocality', 'lifecycle', 'townCity', 'objectType', 'addressPositionType', 'queueStatusName', 'submitterUserName'],
          ['changeId','version', 'Number', 'Road','submittedDate', 'changeType', 'addressType', 'suburb', 'lifecycle', 'townCity', 'objectType', 'addressPositionType', 'queueStatus', 'submitter' ]
         )
                
        self.uAddressListView.setModel( self._addressListModel )
        self.setController( controller )
        #self._controller.getResData() 

    def setController( self, controller ):
        ''' Initially init'd from the compiled UI file
        of the same name, therefore a controller instance is not
        passed at init and thus sorted out by this method '''
        if not controller:
            controller = Controller.instance()
        #self._addressListModel.setAddressList( controller.reviewList())
        #controller.reviewSelected.connect( self.addressSelected )
        #self.uReviewEditor.setController( controller )
        self._controller = controller

  