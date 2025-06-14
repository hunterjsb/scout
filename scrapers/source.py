from typing import Protocol, Any, Dict, Callable


class Source(Protocol):
    """Base protocol defining what any scraper source should support."""

    def __str__(self) -> str:
        """String representation for logging/display."""
        ...

    def get_methods(self) -> Dict[str, Callable]:
        """Get available methods from the source."""
        ...

    def __call__(self, method_name: str, *args, **kwargs) -> Any:
        """Call a method on the source."""
        ...


class SourceAdapter:
    """Automatically wraps any object into Source protocol through introspection."""

    def __init__(self, raw_source: Any):
        self.raw_source = raw_source
        self._methods = self._introspect_methods()

    def _introspect_methods(self) -> Dict[str, Callable]:
        """Discover callable methods from the raw source."""
        methods = {}
        for name in dir(self.raw_source):
            if not name.startswith('_'):  # Skip private methods
                attr = getattr(self.raw_source, name)
                if callable(attr):
                    methods[name] = attr
        return methods

    def __str__(self) -> str:
        return f"SourceAdapter({self.raw_source.__class__.__name__})"

    def get_methods(self) -> Dict[str, Callable]:
        """Get available methods from the source."""
        return self._methods.copy()

    def __call__(self, method_name: str, *args, **kwargs) -> Any:
        """Call a method on the source."""
        if method_name not in self._methods:
            raise AttributeError(f"Method '{method_name}' not found in source")
        return self._methods[method_name](*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to raw source with full typing."""
        # Return the actual method/attribute from raw source for full typing
        return getattr(self.raw_source, name)


def create_source(raw_source: Any) -> SourceAdapter:
    """Create a Source from any object through introspection."""
    return SourceAdapter(raw_source)


class WebSource(Source, Protocol):
    """Protocol for web scraping sources."""
    url: str
    timeout: int
    headers: dict


class APISource(Source, Protocol):
    """Protocol for API scraping sources."""
    base_url: str
    api_key: str
    rate_limit: bool


class TwitterSource(APISource, Protocol):
    """Protocol for Twitter API sources."""
    bearer_token: str
    wait_on_rate_limit: bool


class DatabaseSource(Source, Protocol):
    """Protocol for database sources."""
    connection_string: str
    table_name: str
    query: str


class FileSource(Source, Protocol):
    """Protocol for file-based sources."""
    file_path: str
    encoding: str
    delimiter: str  # For CSV files
