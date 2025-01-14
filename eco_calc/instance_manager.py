class InstanceManager:
    _instances = {}

    @classmethod
    def get_instance(self, key):
        return self._instances.get(key)

    @classmethod
    def set_instance(self, key, instance):
        self._instances[key] = instance
