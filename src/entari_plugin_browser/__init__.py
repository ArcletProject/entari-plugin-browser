from pathlib import Path
from typing import Any

from arclet.entari import plugin

from .service import PlaywrightService as PlaywrightService
from .config import BrowserConfig
from .utils import logger


__version__ = "0.4.1"

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


async def html2img(
    html: str,
    template_path: str | None = None,
    page_option: PageOption | None = None,
    screenshot_option: ScreenshotOption | None = None,
) -> bytes:
    """内置的HTML转图片方法，输出格式为jpeg

    Args:
        html (str): HTML内容
        template_path (str, optional): 模板路径, 如 "file:///path/to/template/"
        page_option (PageOption | None, optional): 网页参数. Defaults to {"viewport": {"width": 800, "height": 10}}.
        screenshot_option (ScreenshotOption | None, optional): 截图配置. Defaults to None.
    """
    _template_path = template_path or Path.cwd().as_uri()

    async def _goto(page):
        await page.goto(_template_path)

    if page_option is None:
        page_option = PageOption(viewport={"width": 800, "height": 10})

    return await _html_render.render(
        html,
        extra_page_option=page_option,
        extra_screenshot_option=screenshot_option,
        extra_page_modifiers=[_goto]
    )


async def template2html(
    template_path: str,
    template_name: str,
    filters: dict[str, Any] | None = None,
    **kwargs,
) -> str:
    """使用jinja2模板引擎通过html生成图片

    Args:
        template_path (str): 模板路径
        template_name (str): 模板名
        filters (Optional[Dict[str, Any]]): 自定义过滤器
        **kwargs: 模板内容
    Returns:
        str: html
    """
    try:
        import jinja2
    except ImportError:
        raise ImportError(
            "template_to_html 需要可选依赖 jinja2，请安装: pip install 'entari-plugin-browser[jinja]'"
        ) from None

    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path),
        enable_async=True,
        autoescape=jinja2.select_autoescape(["html","htm","xml","xhtml"])
    )

    if filters:
        for filter_name, filter_func in filters.items():
            template_env.filters[filter_name] = filter_func
            logger.debug(f"Custom filter loaded: {filter_name}")

    template = template_env.get_template(template_name)

    return await template.render_async(**kwargs)


async def template2img(
    template_path: str,
    template_name: str,
    templates: dict[Any, Any],
    filters: dict[str, Any] | None = None,
    page_option: PageOption | None = None,
    screenshot_option: ScreenshotOption | None = None,
) -> bytes:
    """使用jinja2模板引擎通过html生成图片

    Args:
        template_path (str): 模板路径
        template_name (str): 模板名
        templates (dict[Any, Any]): 模板内容
        filters (Optional[Dict[str, Any]]): 自定义过滤器
        page_option (PageOption | None, optional): 网页参数. Defaults to
            {"base_url": f"file://{os.getcwd()}", "viewport": {"width": 800, "height": 10}}.
        screenshot_option (ScreenshotOption | None, optional): 截图配置. Defaults to None.
    """
    if page_option is None:
        page_option = PageOption(viewport={"width": 800, "height": 10}, base_url=Path.cwd().as_uri())

    html = await template2html(template_path, template_name, filters=filters, **templates)
    return await html2img(
        html=html,
        template_path=Path(template_path).as_uri(),
        page_option=page_option,
        screenshot_option=screenshot_option,
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
    "template2img",
    "html2img",
    "template2html",
    "playwright_api",
]
