import re
from typing import Literal
from pathlib import Path

from arclet.entari import BasicConfModel, plugin
from playwright._impl._api_structures import (
    Geolocation,
    HttpCredentials,
    ProxySettings,
    ViewportSize,
)

from .service import PlaywrightService as PlaywrightService


class Config(BasicConfModel):
    browser_type: Literal["chromium", "firefox", "webkit"] = "chromium"
    auto_download_browser: bool = False
    playwright_download_host: str | None = None
    install_with_deps: bool = False
    user_data_dir: str | Path | None = None
    channel: Literal["chromium", "chrome", "chrome-beta", "chrome-dev", "chrome-canary", "msedge", "msedge-beta", "msedge-dev", "msedge-canary", "firefox", "webkit"] | None = None
    executable_path: str | Path | None = None
    args: list[str] | None = None
    ignore_default_args: bool | list[str] | None = None
    handle_sigint: bool | None = None
    handle_sigterm: bool | None = None
    handle_sighup: bool | None = None
    timeout: float | None = None
    env: dict[str, str | float | bool] | None = None
    headless: bool | None = None
    devtools: bool | None = None
    proxy: ProxySettings | None = None
    downloads_path: str | Path | None = None
    slow_mo: float | None = None
    viewport: ViewportSize | None = None
    screen: ViewportSize | None = None
    no_viewport: bool | None = None
    ignore_https_errors: bool | None = None
    java_script_enabled: bool | None = None
    bypass_csp: bool | None = None
    user_agent: str | None = None
    locale: str | None = None
    timezone_id: str | None = None
    geolocation: Geolocation | None = None
    permissions: list[str] | None = None
    extra_http_headers: dict[str, str] | None = None
    offline: bool | None = None
    http_credentials: HttpCredentials | None = None
    device_scale_factor: float | None = None
    is_mobile: bool | None = None
    has_touch: bool | None = None
    color_scheme: Literal["dark", "light", "no-preference"] | None = None
    reduced_motion: Literal["no-preference", "reduce"] | None = None
    forced_colors: Literal["active", "none"] | None = None
    accept_downloads: bool | None = None
    traces_dir: str | Path | None = None
    chromium_sandbox: bool | None = None
    record_har_path: str | Path | None = None
    record_har_omit_content: bool | None = None
    record_video_dir: str | Path | None = None
    record_video_size: ViewportSize | None = None
    base_url: str | None = None
    strict_selectors: bool | None = None
    service_workers: Literal["allow", "block"] | None = None
    record_har_url_filter: str | re.Pattern[str] | None = None
    record_har_mode: Literal["full", "minimal"] | None = None
    record_har_content: Literal["attach", "embed", "omit"] | None = None


__version__ = "0.2.1"

plugin.metadata(
    "Browser 服务",
    [{"name": "RF-Tar-Railt", "email": "rf_tar_railt@qq.com"}],
    __version__,
    description="通用的浏览器服务，可用于网页截图和图片渲染等。使用 Playwright",
    urls={
        "homepage": "https://github.com/ArcletProject/entari-plugin-browser",
    },
    config=Config,
)

_config = plugin.get_config(Config)
playwright_api = plugin.add_service(PlaywrightService(**vars(_config)))


from graiax.text2img.playwright import HTMLRenderer, MarkdownConverter, PageOption, ScreenshotOption, convert_text, convert_md
from graiax.text2img.playwright.renderer import BuiltinCSS


_html_render = HTMLRenderer(
    page_option=PageOption(device_scale_factor=1.5),
    screenshot_option=ScreenshotOption(type="jpeg", quality=80, full_page=True, scale="device"),
    css=(
        BuiltinCSS.reset,
        BuiltinCSS.github,
        BuiltinCSS.one_dark,
        BuiltinCSS.container,
        "body{background-color:#fafafac0;}",
        "@media(prefers-color-scheme:light){.markdown-body{--color-canvas-default:#fafafac0;}}",
    ),
)

_md_converter = MarkdownConverter()


async def text2img(text: str, width: int = 800, screenshot_option: ScreenshotOption | None = None) -> bytes:
    """内置的文本转图片方法，输出格式为jpeg"""
    html = convert_text(text)

    return await _html_render.render(
        html,
        extra_page_option=PageOption(viewport={"width": width, "height": 10}),
        extra_screenshot_option=screenshot_option,
    )


async def md2img(text: str, width: int = 800, screenshot_option: ScreenshotOption | None = None) -> bytes:
    """内置的Markdown转图片方法，输出格式为jpeg"""
    html = _md_converter.convert(text)

    return await _html_render.render(
        html,
        extra_page_option=PageOption(viewport={"width": width, "height": 10}),
        extra_screenshot_option=screenshot_option,
    )


__all__ = [
    "PlaywrightService",
    "BuiltinCSS",
    "HTMLRenderer",
    "MarkdownConverter",
    "PageOption",
    "ScreenshotOption",
    "convert_text",
    "convert_md",
    "text2img",
    "md2img",
    "playwright_api",
]
