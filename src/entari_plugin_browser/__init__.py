import re
from typing import Literal
from pathlib import Path

from arclet.entari import BasicConfModel, plugin
from playwright._impl._api_structures import (
    Geolocation,
    HttpCredentials,
    ProxySettings,
    ViewportSize, ClientCertificate,
)

from .service import PlaywrightService as PlaywrightService


class Config(BasicConfModel):
    browser_type: Literal["chromium", "firefox", "webkit"] = "chromium"
    """浏览器类型，可选值为 "chromium"、"firefox" 和 "webkit"，默认为 "chromium"。"""
    auto_download_browser: bool = False
    """是否自动下载浏览器，默认为 False。如果你已经有浏览器环境，可以关闭此选项以加快启动速度。"""
    playwright_download_host: str | None = None
    """Playwright 下载源地址，默认为 None。若未设置此项，会尝试使用内置的镜像源。"""
    install_with_deps: bool = False
    """安装浏览器时是否一并安装依赖，默认为 False。Linux 系统建议开启此选项。"""
    user_data_dir: str | Path | None = None
    """开启持久化上下文时使用的用户数据目录，默认为 None，即不使用持久化上下文。"""
    # 浏览器启动参数
    channel: Literal["chromium", "chrome", "chrome-beta", "chrome-dev", "chrome-canary", "msedge", "msedge-beta", "msedge-dev", "msedge-canary", "firefox", "webkit"] | None = None
    """指定本地现有的浏览器发行版，默认为 None。注意其应该与 browser_type 匹配。"""
    executable_path: str | Path | None = None
    """指定本地现有的浏览器可执行文件路径，默认为 None。"""
    args: list[str] | None = None
    """要传递给浏览器实例的其他参数。Chromium 的标志列表可[在此参考](https://peter.sh/experiments/chromium-command-line-switches/)。
    
    注意：某些参数可能会干扰 Playwright 的正常运行，建议仅在了解其作用的情况下使用。
    """
    ignore_default_args: bool | list[str] | None = None
    """是否忽略默认的浏览器参数，默认为 None，即不忽略。也可以传递一个字符串列表来指定要忽略的参数。"""
    handle_sigint: bool | None = None
    """是否在 Ctrl+C 时关闭浏览器。不配置则默认为 True。"""
    handle_sigterm: bool | None = None
    """是否在进程终止时关闭浏览器。不配置则默认为 True。"""
    handle_sighup: bool | None = None
    """是否在 SIGHUP 信号时关闭浏览器。不配置则默认为 True。"""
    timeout: float | None = None
    """浏览器启动超时时间，单位为毫秒。默认为 None，即使用 Playwright 的默认值 `30000` (30 秒)。
    
    传入 `0` 则表示禁用超时。
    """
    env: dict[str, str | float | bool] | None = None
    """要传递给浏览器进程的环境变量。"""
    headless: bool | None = None
    """是否以无头模式运行浏览器。默认为 None，即使用 Playwright 的默认值 True。"""
    devtools: bool | None = None
    """是否为 Chromium 浏览器打开 DevTools 窗口。默认为 None，即使用 Playwright 的默认值 False。"""
    proxy: ProxySettings | None = None
    """代理设置，默认为 None，即不使用代理。"""
    downloads_path: str | Path | None = None
    """指定浏览器下载文件的保存路径，默认为 None，即使用系统默认的下载路径。"""
    slow_mo: float | None = None
    """在每个 Playwright 操作后等待的时间，单位为毫秒。默认为 None，即不等待。"""
    traces_dir: str | Path | None = None
    """指定保存跟踪文件的目录，默认为 None，即不保存跟踪文件。"""
    chromium_sandbox: bool | None = None
    """是否启用 Chromium 沙盒。默认为 None，即使用 Playwright 的默认值 False。"""
    firefox_user_prefs: dict[str, str | float | bool] | None = None
    """要传递给 Firefox 浏览器的用户首选项。"""
    # 远程浏览器配置
    connect_endpoint: str | None = None
    """是否连接到一个已经运行的远程浏览器实例，默认为 None，即不连接。
    
    根据 `connect_cdp` 的值，连接方式有所不同：
    - 如果 `connect_cdp` 为 True 或 None，则通过 Chrome DevTools Protocol (CDP) 连接。(仅适用于 Chromium 浏览器)
    - 如果 `connect_cdp` 为 False，则通过 Playwright 的 WebSocket 连接。
    """
    connect_cdp: bool | None = None
    """是否通过 Chrome DevTools Protocol (CDP) 连接远程浏览器，默认为 None, 即使用 CDP 连接。(仅适用于 Chromium 浏览器)"""
    connect_headers: dict[str, str] | None = None
    """连接远程浏览器时使用的额外 HTTP 头，默认为 None。"""
    expose_network: str | None = None
    """此选项将连接客户端上的可用网络公开到正在连接的浏览器。由以逗号分隔的规则列表组成。
    
    可用规则：
    1. 主机名模式，例如：`example.com`、`*.org：99`、`x.*.y.com`、`*foo.org`。
    2. IP 地址，例如：`127.0.0.1`、`0.0.0.0:99`、`[::1]`、`[0:0::1]:99`。
    3. <loopback> 匹配本地环回接口的：`localhost`, `*.localhost`, `127.0.0.1`, `[::1]`。

    一些常见的例子：
    - `"*"` 公开所有网络。
    - `"<loopback>"` 公开本地主机网络。
    - `"*.test.internal-domain，*.staging.internal-domain，<loopback>"` 用于公开测试/暂存部署，以及 localhost。
    """
    # 浏览器上下文配置
    viewport: ViewportSize | None = None
    """设置全局的固定视口大小，默认为 None，即使用浏览器默认值 1280x720。"""
    screen: ViewportSize | None = None
    """通过 `window.screen` 模拟网页内可用的一致窗口屏幕大小。仅在设置了 `viewport` 时可用。"""
    no_viewport: bool | None = None
    """不强制固定视口，允许在有头模式下调整窗口大小。"""
    ignore_https_errors: bool | None = None
    """是否忽略 HTTPS 错误，默认为 None，即使用 Playwright 的默认值 False。"""
    java_script_enabled: bool | None = None
    """是否启用 JavaScript，默认为 None，即使用 Playwright 的默认值 True。"""
    bypass_csp: bool | None = None
    """是否绕过页面的内容安全策略，默认为 None，即使用 Playwright 的默认值 False。"""
    user_agent: str | None = None
    """设置浏览器的用户代理字符串，默认为 None，即使用浏览器默认值。"""
    locale: str | None = None
    """设置浏览器的语言环境，默认为 None，即使用浏览器默认值。"""
    timezone_id: str | None = None
    """设置浏览器的时区，默认为 None，即使用浏览器默认值。"""
    geolocation: Geolocation | None = None
    permissions: list[str] | None = None
    """授予页面的权限列表，默认为 None，即不授予任何权限。"""
    extra_http_headers: dict[str, str] | None = None
    """设置额外的 HTTP 头，默认为 None，即不设置额外的头。"""
    offline: bool | None = None
    """是否启用离线模式，默认为 None，即使用 Playwright 的默认值 False。"""
    http_credentials: HttpCredentials | None = None
    """用于 HTTP 认证的凭据，默认为 None，即不使用 HTTP 认证。"""
    device_scale_factor: float | None = None
    """设置设备的缩放因子，默认为 None，即使用浏览器默认值 1。"""
    is_mobile: bool | None = None
    """是否考虑了 `meta viewport` 标记并启用了触摸事件。isMobile 是设备的一部分，因此您实际上不需要手动设置它。默认为 'false'。Firefox 不支持该项。"""
    has_touch: bool | None = None
    """是否启用触摸事件，默认为 None，即使用 Playwright 的默认值 False。"""
    color_scheme: Literal["dark", "light", "no-preference"] | None = None
    """设置浏览器配色方案，默认为 None，即使用浏览器默认值 'light'。"""
    reduced_motion: Literal["no-preference", "reduce"] | None = None
    """设置浏览器的动画偏好，默认为 None，即使用浏览器默认值 'no-preference'。"""
    forced_colors: Literal["active", "none"] | None = None
    """设置浏览器的强制颜色模式，默认为 None，即使用浏览器默认值 'none'。"""
    accept_downloads: bool | None = None
    """是否允许浏览器下载文件，默认为 None，即使用 Playwright 的默认值 True。"""
    record_har_path: str | Path | None = None
    """指定保存 [HAR](http://www.softwareishard.com/blog/har-12-spec) 文件的路径，默认为 None，即不保存 HAR 文件。"""
    record_har_omit_content: bool | None = None
    """是否在 HAR 文件中省略响应内容，默认为 None，即使用 Playwright 的默认值 False。"""
    record_video_dir: str | Path | None = None
    """指定保存录制视频的目录，默认为 None，即不录制视频。"""
    record_video_size: ViewportSize | None = None
    """设置录制视频的分辨率，默认为 None，即使用浏览器默认值。"""
    base_url: str | None = None
    """设置相对 URL 的基础 URL，默认为 None，即不设置基础 URL。"""
    strict_selectors: bool | None = None
    """是否启用严格选择器模式，默认为 None，即使用 Playwright 的默认值 False。"""
    service_workers: Literal["allow", "block"] | None = None
    """设置是否允许或阻止服务工作线程，默认为 None，即使用 Playwright 的默认值 'allow'。
    
    服务工作线程详见 [Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
    """
    record_har_url_filter: str | re.Pattern[str] | None = None
    record_har_mode: Literal["full", "minimal"] | None = None
    """设置为“最小值”时，仅记录从 HAR 路由所需的信息。这省略了从 HAR 重播时不使用的大小、时间、页面、cookie、安全性和其他类型的 HAR 信息。

    默认为“full”。
    """
    record_har_content: Literal["attach", "embed", "omit"] | None = None
    """用于控制资源内容管理的可选设置。
    
    如果指定了“省略”，则不会保留内容。
    如果指定了“attach”，则资源将作为单独的文件持久化，并且所有这些文件都与 HAR 文件一起存档。
    默认为 'embed'，它根据 HAR 规范将内容内联存储到 HAR 文件中。
    """
    client_certificates: list[ClientCertificate] | None = None
    """TLS 客户端身份验证，以允许服务器请求客户端证书并对其进行验证。
    
    传入参数为要使用的客户端证书数组。每个证书对象必须同时具有“certPath”和“keyPath”、单个“pfxPath”或它们相应的直接值等效项（“cert”和“key”或“pfx”）。
    
    （可选）如果证书已加密，则应提供“密码”属性。应为“origin”属性提供与证书有效的请求源完全匹配的属性。
    
    注意：在 macOS 上使用 WebKit 时，访问“localhost”不会获取客户端证书。您可以通过将“localhost”替换为“local.playwright”来使其正常工作。
    """


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
