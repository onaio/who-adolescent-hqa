import os
import importlib
import operator

COUNTRY_SPECIFIC_SETTINGS = 'WHOAHQA_COUNTRY_SETTING'


empty = object()


def new_method_proxy(func):
    def inner(self, *args):
        if self._wrapped is empty:
            self._setup()
        return func(self._wrapped, *args)
    return inner


class LazyObject(object):
    """
    A wrapper for another class that can be used to delay instantiation of
    the wrapped class.
    """
    _wrapped = None

    def __init__(self):
        self._wrapped = empty

    __getattr__ = new_method_proxy(getattr)

    def __setattr__(self, name, value):
        if name == "_wrapped":
            # Assign to __dict__ to avoid infinite __setattr__ loops.
            self.__dict__["_wrapped"] = value
        else:
            if self._wrapped is empty:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name):
        if name == "_wrapped":
            raise TypeError("can't delete _wrapped.")
        if self._wrapped is empty:
            self._setup()
        delattr(self._wrapped, name)

    def _setup(self):
        """
        Must be implemented by subclasses to initialize the wrapped object.
        """
        raise NotImplementedError(
            'subclasses of LazyObject must provide a _setup() method')

    # Introspection support
    __dir__ = new_method_proxy(dir)

    # Dictionary methods support
    __getitem__ = new_method_proxy(operator.getitem)
    __setitem__ = new_method_proxy(operator.setitem)
    __delitem__ = new_method_proxy(operator.delitem)

    __len__ = new_method_proxy(len)
    __contains__ = new_method_proxy(operator.contains)


class LazyCharacteristics(LazyObject):
    """
    A lazy proxy for either general characteristic settings or country specific
    settings
    """
    def _setup(self, name=None):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time we need any settings at all, if the user has not
        previously configured the settings manually.
        """
        characteristic_settings = os.environ.get(
            COUNTRY_SPECIFIC_SETTINGS,
            "whoahqa.constants.base_characteristics")
        if not characteristic_settings:
            desc = ("characteristic %s" % name) if name else "characteristics"
            raise Exception(
                "Requested %s, but settings are not configured. "
                "You must either define the environment variable %s "
                "or call settings.configure() before accessing settings."
                % (desc, COUNTRY_SPECIFIC_SETTINGS))

        self._wrapped = BaseCharacteristics(characteristic_settings)

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._setup(name)
        return getattr(self._wrapped, name)


class BaseCharacteristics(object):
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

    def __init__(self, settings_module):
        mod = importlib.import_module(settings_module)
        self._explicit_settings = set()

        for setting in dir(mod):
            setting_value = getattr(mod, setting)
            setattr(self, setting, setting_value)
            self._explicit_settings.add(setting)

characteristics = LazyCharacteristics()
