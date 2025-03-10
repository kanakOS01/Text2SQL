from urllib.parse import urlparse


def check_valid_uri(uri: str) -> bool:
    """
    Check if the URI is valid and return the scheme if it is valid

    Supported URI schemes: Postgres, MySQL, SQLite
    """
    try:
        parsed_uri = urlparse(uri)

        valid_schemes = ["postgres", "mysql", "sqlite", "mssql", "oracle"]
        if parsed_uri.scheme in valid_schemes:
            if parsed_uri.scheme == "sqlite":
                return bool(parsed_uri.path)
            else:
                return bool(parsed_uri.netloc)
        return False
    except Exception:
        return False


def extract_scheme(uri: str) -> str:
    """
    Extract the scheme from the URI
    """
    return urlparse(uri).scheme
