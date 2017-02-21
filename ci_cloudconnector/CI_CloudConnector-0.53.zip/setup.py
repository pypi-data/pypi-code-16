import CI_LC_BL
from distutils.core import setup
# ============================
def getVersion():
    ans = ''
    try:
        ans = CI_LC_BL.getLocalVersion()
    except Exception as inst:
        print "Error getting version" + str(inst)
        
    return ans

setup(name='CI_CloudConnector',
      version= getVersion(),
      py_modules=['CI_CloudConnector' , 'CI_LC_BL'],
	  packages=['CI_CloudConnector',],
	  package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['ci_cloudConnectorService', 'runCloudConnector.sh', 'SetupCloudConnector.sh']
	  },
	  include_package_data = True,
	  description="IOT application that collect data from PLC (ModBus or AnB Ethernet/IP) and send to cloud using https",
	  author="Ido Peles",
	  author_email="idop@contel.co.il",
      install_requires=['pymodbus' , 'cpppo' , 'tzlocal'],
	  url = "http://www.contel.co.il/en/",
	  long_description=open('README.txt').read(),
      )


	  
