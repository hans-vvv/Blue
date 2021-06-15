import re

##string = 'switchport mode access'
##match = re.search(r'switchport mode (\w+)', string)
##if match:
##    value = format(match.group(1))
##    
##print(value)
##
class ReSearcher(object):
    match = None

    def __call__(self, pattern, string):
        self.match = re.search(pattern, string)
        return self.match

    def __getattr__(self, name):
        return getattr(self.match, name)
        
match = ReSearcher()

string = 'switchport mode trunk'
if match(r'switchport mode (\w+)', string):
    value = format(match.group(1))
    
print(value)


