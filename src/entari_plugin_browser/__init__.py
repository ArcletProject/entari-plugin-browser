from arclet.entari import plugin

from .service import PlaywrightService as PlaywrightService
from .config import BrowserConfig


__version__ = "0.4.0"

plugin.metadata(
    "Browser 服务",
    [{"name": "RF-Tar-Railt", "email": "rf_tar_railt@qq.com"}],
    __version__,
    description="通用的浏览器服务，可用于网页截图和图片渲染等。使用 Playwright",
    urls={
        "homepage": "https://github.com/ArcletProject/entari-plugin-browser",
    },
    config=BrowserConfig,
)

_config = plugin.get_config(BrowserConfig)
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
