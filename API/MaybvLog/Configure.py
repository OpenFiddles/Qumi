# API\MaybvLog\Configure.py
import os



class Configure:
    def __init__(self, config_file="..\qu.config"):
        self.config_file = config_file
        self.config = {}
    
    def _create_if_not_exist(self):
        with open(self.config_file, "x") as f:
            f.write("""
Username=
Displayname=
OpenLicense=
OpenUser=
PACKAGE_BUNDLE=
LicenseBy=
            
            """)
    
    def get_config_value(self, namse):
        try:
            with open(self.config_file, "r") as f:
                for line in f:
                    if "=" in line and namse in line:
                        name, val = line.strip().split("=")
                        self.config[name] = val
                        return self.config[namse]
        except FileNotFoundError as e:
            self._create_if_not_exist()
            print("""
            
            File Not Found... With this error
            ================================
            {}
            =================================
            Creating now
            """.format(str(e)))
    


        
            
if __name__ == '__main__':
    c = Configure(config_file="qu.config")
    print(str(c.get_config_value("Username")))