# Author: Luca Ferroni <luca@befair.it>
# License: AGPLv3


class ModelExtender(object):

    ext_prefix = "_ext_"

    def contribute_to_class(self, cls, name):
        """Extending cls with object attrs that starts by prefix.

        Prefix is defined in __class__.ext_prefix.
        """

        prefix = self.__class__.ext_prefix

        for method_name in dir(self):

            if method_name.startswith(prefix):

                #print("Aggiungo il metodo %s" % method_name)
                
                sender.add_to_class(
                    method_name[len(prefix):],
                    getattr(self.__class__, method_name)
                )

