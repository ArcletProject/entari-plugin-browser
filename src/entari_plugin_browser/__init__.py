import re
from typing import Literal, Optional, Union
from pathlib import Path

from arclet.entari import BasicConfModel, plugin
from graiax.playwright import PlaywrightService
from playwright._impl._api_structures import (
    Geolocation,
    HttpCredentials,
    ProxySettings,
    ViewportSize,
)
from graiax.text2img.playwright import HTMLRenderer, MarkdownConverter, PageOption, ScreenshotOption, convert_text, convert_md
from graiax.text2img.playwright.renderer import BuiltinCSS


class Config(BasicConfModel):
    browser_type: Literal["chromium", "firefox", "webkit"] = "chromium"
    auto_download_browser: bool = False
    playwright_download_host: Optional[str] = None
    install_with_deps: bool = False
    user_data_dir: Union[str, Path, None] = None
    channel: Optional[str] = None
    executable_path: Union[str, Path, None] = None
    args: Optional[list[str]] = None
    ignore_default_args: Union[bool, list[str], None] = None
    handle_sigint: Optional[bool] = None
    handle_sigterm: Optional[bool] = None
    handle_sighup: Optional[bool] = None
    timeout: Optional[float] = None
    env: Optional[dict[str, Union[str, float, bool]]] = None
    headless: Optional[bool] = None
    devtools: Optional[bool] = None
    proxy: Optional[ProxySettings] = None
    downloads_path: Union[str, Path, None] = None
    slow_mo: Optional[float] = None
    viewport: Optional[ViewportSize] = None
    screen: Optional[ViewportSize] = None
    no_viewport: Optional[bool] = None
    ignore_https_errors: Optional[bool] = None
    java_script_enabled: Optional[bool] = None
    bypass_csp: Optional[bool] = None
    user_agent: Optional[str] = None
    locale: Optional[str] = None
    timezone_id: Optional[str] = None
    geolocation: Optional[Geolocation] = None
    permissions: Optional[list[str]] = None
    extra_http_headers: Optional[dict[str, str]] = None
    offline: Optional[bool] = None
    http_credentials: Optional[HttpCredentials] = None
    device_scale_factor: Optional[float] = None
    is_mobile: Optional[bool] = None
    has_touch: Optional[bool] = None
    color_scheme: Optional[Literal["dark", "light", "no-preference"]] = None
    reduced_motion: Optional[Literal["no-preference", "reduce"]] = None
    forced_colors: Optional[Literal["active", "none"]] = None
    accept_downloads: Optional[bool] = None
    traces_dir: Union[str, Path, None] = None
    chromium_sandbox: Optional[bool] = None
    record_har_path: Union[str, Path, None] = None
    record_har_omit_content: Optional[bool] = None
    record_video_dir: Union[str, Path, None] = None
    record_video_size: Optional[ViewportSize] = None
    base_url: Optional[str] = None
    strict_selectors: Optional[bool] = None
    service_workers: Optional[Literal["allow", "block"]] = None
    record_har_url_filter: Union[str, re.Pattern[str], None] = None
    record_har_mode: Optional[Literal["full", "minimal"]] = None
    record_har_content: Optional[Literal["attach", "embed", "omit"]] = None


__version__ = "0.1.0"

plugin.metadata(
    "Browser 服务",
    ["RF-Tar-Railt <rf_tar_railt@qq.com>"],
    __version__,
    description="通用的浏览器服务，可用于网页截图和图片渲染等。使用 Playwright",
    urls={
        "homepage": "https://github.com/ArcletProject/entari-plugin-browser",
    },
    config=Config,
)

_config = plugin.get_config(Config)
playwright_api = plugin.add_service(PlaywrightService(**vars(_config)))

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


async def text2img(text: str, width: int = 800) -> bytes:
    """内置的文本转图片方法，输出格式为jpeg"""
    html = convert_text(text)

    return await _html_render.render(
        html,
        extra_page_option=PageOption(viewport={"width": width, "height": 10}),
    )


async def md2img(text: str, width: int = 800) -> bytes:
    """内置的Markdown转图片方法，输出格式为jpeg"""
    html = _md_converter.convert(text)

    return await _html_render.render(
        html,
        extra_page_option=PageOption(viewport={"width": width, "height": 10}),
    )


__all__ = [
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
