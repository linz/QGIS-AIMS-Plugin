from qgis.core import QgsApplication
from qgis.utils import plugins
from PyQt4 import uic
from PyQt4.QtGui import QDialog, QDialogButtonBox
import os
import ConfigParser


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Ui_AimsConfigureDialog.ui'))

CONF_DIR = os.path.join(QgsApplication.qgisSettingsDirPath(), 'aims')
CONF_FILE = os.path.join(CONF_DIR, "aimsConfig.ini")

#Default Config
DEF_CONF = {'user':{
                'org':'linz',
                'name':'test.administrator',
                'pass':'test.administrator.pass'},

            'url':{
                'api':'<aims_web_server>:8080/aims/api'},

            'db':{
                'user':'vagrant',
                'password':'',
                'host':'<aims_db_server>',
                'port':'5432',
                'name':'linz_db'},

            'const':{
                'test_mode':False,
                'thread_join_timeout':5,
                'max_feature_count':1000,
                'first_page':1,
                'page_limit':1000,
                'pool_page_check_delay':0.2,
                'queue_check_delay':1,
                'thread_keepalive':60,
                'last_page_guess':10,
                'null_page_value':0,
                'enable_entity_evaluation':True,
                'swzero':(0.0, 0.0),
                'nezero':(0.0, 0.0),
                'skip_null':True,
                'def_sep':'_',
                'res_path':'resources',
                'local_adl':'aimsdata',
                'merge_response':True,
                'merge_exclude':'workflow_sourceReason',
                'hack_sup_ind':'supplemental',
                'ct_ind':'###'}
        }


class AimsConfigureDialog(QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(AimsConfigureDialog, self).__init__(parent)
        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.UiToFile)
        self.stylize()
        self.ensureConfigExists()
        self.iface = None
        
    def showDialog(self):
        self.fileToUi()
        self.show()

    def setIface(self, iface):
        self.iface=iface 

    def ensureConfigExists(self):
        self.configDirExists()
        self.configFileExists()

    def configDirExists(self, dname=CONF_DIR):
        if not os.path.exists(dname):
            os.makedirs(dname)
        return

    def configFileExists(self, conf_file=CONF_FILE):
        if not os.path.isfile(conf_file): 
            self.createConfig()
        return

    def fileToUi(self, conf_file=CONF_FILE):
        Config = ConfigParser.ConfigParser()
        Config.read(conf_file)
        for section, options in DEF_CONF.iteritems():
            for option in options:
                getattr(self,'{0}_{1}'.format(section, option)).setText(Config.get(section, option)) 

    def UiToFile(self, conf_file=CONF_FILE):
        Config = ConfigParser.ConfigParser()
        config_file = open(CONF_FILE,'w')
        for section, options in DEF_CONF.iteritems():
            Config.add_section(section)
            for option in options:
                value = getattr(self,'{0}_{1}'.format(section, option)).text()
                Config.set(section, option, value)
        Config.write(config_file)
        config_file.close()

    def createConfig(self):
        Config = ConfigParser.ConfigParser()
        config_file = open(CONF_FILE,'w')
        for section, options in DEF_CONF.iteritems():
            Config.add_section(section)
            for k, v in options.iteritems():
                Config.set(section,k,v)
        Config.write(config_file)
        config_file.close()

    def stylize(self):
        """ Stylize the list widget """

        self.uListOptions.setStyleSheet(
            """ QListWidget {
                    background-color: rgb(105, 105, 105);
                    outline: 0;
                }
                QListWidget::item {
                    color: white;
                    padding: 3px;
                }
                QListWidget::item::selected {
                    color: black;
                    background-color:palette(Window);
                    padding-right: 0px;
                };
            """
        )
