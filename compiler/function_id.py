class FunctionIdGenerator:
    _instance = None

    def __init__(self):
        if FunctionIdGenerator._instance is not None:
            return
        self._current_id = -1
        FunctionIdGenerator._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()
        return cls._instance

    def get_next_id(self) -> int:
        self._current_id += 1
        return self._current_id
