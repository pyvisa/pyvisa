__author__ = 'grecco'


def range_property(attribute_name, min_value, max_value, doc=None, transform=None):

    def getter(self):
        return self.get_visa_attribute(attribute_name)

    def setter(self, value):
        if not min_value <= value <= max_value:
            raise ValueError('%r is an invalid value for attribute %s, should be between %r and %r',
                             value, attribute_name, min_value, max_value)
        self.set_visa_attribute(attribute_name, value)

    return property(fget=getter, fset=setter, doc=doc)


def boolean_property(attribute_name, doc=doc):

    def getter(self):
        return self.get_visa_attribute(attribute_name) == VI_TRUE

    def setter(self, value):
        self.set_visa_attribute(attribute_name, VI_TRUE if value else VI_FALSE)

    return property(fget=getter, fset=setter, doc=doc)


def char_property(attribute_name, doc=doc):

    def getter(self):
        return chr(self.get_visa_attribute(attribute_name))

    def setter(self, value):
        self.set_visa_attribute(attribute_name, ord(value))

    return property(fget=getter, fset=setter, doc=doc)
