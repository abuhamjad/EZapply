"""Create an interactive local Selenium browser session when requested."""

from typing import Any


def _edge_driver(webdriver: Any, headless: bool) -> Any:
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    if headless:
        options.add_argument("--headless=new")
    return webdriver.Edge(options=options)


def _chrome_driver(webdriver: Any, headless: bool) -> Any:
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    if headless:
        options.add_argument("--headless=new")
    return webdriver.Chrome(options=options)


def _firefox_driver(webdriver: Any, headless: bool) -> Any:
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    return webdriver.Firefox(options=options)


def create_driver(headless: bool = False) -> tuple[Any, str]:
    """Open the first Selenium-compatible browser installed locally."""
    try:
        from selenium import webdriver
    except ImportError as exc:
        raise RuntimeError("Install the Selenium browser dependency first.") from exc

    drivers = (
        ("edge", _edge_driver),
        ("chrome", _chrome_driver),
        ("firefox", _firefox_driver),
    )
    errors: list[str] = []
    for name, factory in drivers:
        try:
            return factory(webdriver, headless), name
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    detail = "; ".join(errors)
    raise RuntimeError(f"No supported browser could start. {detail}")
