import abc


class RepositorySource(abc.ABC):
    @abc.abstractmethod
    def get_content(self) -> bytes:
        """Return the raw repository content (e.g. ZIP bytes)."""
        pass

    @abc.abstractmethod
    def get_filename(self) -> str:
        """Return the source identifier or filename."""
        pass
