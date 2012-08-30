# Author: Luca Ferroni <luca@befair.it>
# License: AGPLv3


class ModelExtender(object):

    ext_prefix = "_ext_"

    def contribute_to_class(self, cls, name):
        """Extending cls with object attrs that starts by prefix.

        Prefix is defined in __class__.ext_prefix.
        Original method, if present, is saved in self._orig_method
        """

        prefix = self.__class__.ext_prefix
        self._orig_method = None

        for method_name in dir(self):

            if method_name.startswith(prefix):

                #print("Aggiungo il metodo %s" % method_name)
                
                self._orig_method = getattr(cls, method_name)
                setattr(
                    cls,
                    method_name[len(prefix):],
                    getattr(self.__class__, method_name)
                )
