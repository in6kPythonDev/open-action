# Content of this module is taken from work of Luca Ferroni <luca@befair.it>
# License: AGPLv3
# Some code is taken elsewhere and of respective owners

import re

# Snippet taken somewhere...
class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

#------------------------------------------------------------------------------
# Uniq functions from http://www.peterbe.com/plog/uniqifiers-benchmark

def unordered_uniq(seq): #Peter Bengtsson
    # Not order preserving
    return list(set(seq))

def ordered_uniq(seq): # Dave Kirby
    # Order preserving
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]


#--------------------------------------------------------------------------------

def get_params_from_template(tmpl):

    # split python template
    expr = r"%\((.*?)\)"
    r = re.compile(expr)
    # find attributes
    attr_names = r.findall(tmpl)
    return attr_names


