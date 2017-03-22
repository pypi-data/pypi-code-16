
import subprocess


scanner_install_instructions = {
                                     "safesql":"github.com/stripe/safesql",
                                     "gas":"github.com/GoASTScanner/gas"
                                    }
GO_CMD = "go"

class InstallGOScanners:

    '''Install the scanners as needed

    '''

    def install_scanner(self, scannerName):
        try:
            scanner_installation_message = subprocess.check_output([GO_CMD,
                                                "get", scanner_install_instructions[scannerName]])
            print(scanner_installation_message.decode("utf-8"))
            print("\nINFO: {0} installed successfully!".format(scannerName))
            return 1
        except subprocess.CalledProcessError as err:
            print("\n\nERROR: {0} installation failed with error {1}".format(scannerName, str(err)))
            return 0
