"""Mock database manager for testing."""

class DatabaseManager:
    def __init__(self, pool=None):
        self.pool = pool or MockPool()

class MockPool:
    def __init__(self):
        self._connection = MockConnection()

    async def acquire(self):
        return self._connection
    
    def close(self):
        pass

class MockConnection:
    async def fetch(self, query, *args):
        return []
    
    async def fetchrow(self, query, *args):
        return None
    
    async def execute(self, query, *args):
        pass
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        pass
