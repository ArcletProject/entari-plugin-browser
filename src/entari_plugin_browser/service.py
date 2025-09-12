from pathlib import Path
from re import Pattern
from typing import Any, Literal, overload

from launart import Service, Launart
from playwright._impl._api_structures import (
    Geolocation,
    HttpCredentials,
    ProxySettings,
    StorageState,
    ViewportSize,
)
from playwright. async_api._context_manager import PlaywrightContextManager
from playwright.async_api import Error as PWError, BrowserType
from playwright.async_api import Playwright, async_playwright
from typing_extensions import ParamSpec

from graiax.playwright.service import PlaywrightPageInterface, PlaywrightContextInterface
from graiax.playwright.i18n import N_
from graiax.playwright.utils import brower_config_list, browser_context_config_list

from .installer import install_playwright
from .installer import log

P = ParamSpec("P")


BROWSER_CHANNEL_TYPES = [
    "chromium",
    "chrome",
    "chrome-beta",
    "chrome-dev",
    "chrome-canary",
    "msedge",
    "msedge-beta",
    "msedge-dev",
    "msedge-canary",
    "firefox",
    "webkit",
]


class PlaywrightService(Service, PlaywrightPageInterface, PlaywrightContextInterface):
    """用于 launart 的浏览器服务

    Args:
        browser_type (Literal["chromium", "firefox", "webkit"]): 你要使用的浏览器。默认为 Chromium
        auto_download_browser (bool): 是否在启动时自动下载 Playwright 所使用的浏览器或检查其更新。若你需要使用
            本地计算机上已有的 Chromium 浏览器，则可以设置为 False
        playwright_download_host (Optional[str]): 如需自动下载浏览器或检查更新，此处可以指定下载/检查更新的地址
        install_with_deps (bool): 是否在下载安装 Playwright 所使用的浏览器时一同安装缺失的系统依赖，可能需要访问
            sudo 或管理员权限
        user_data_dir: (str | Path | None): 用户数据储存目录。传入该参数且不为 None 时，使用持久性上下文模式启动
            Playwright，此时将不可通过 `PlaywrightBrowser` 接口获取浏览器实例
        **kwargs: 详见 <https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch>
    """

    id = "web.render/playwright"
    playwright_mgr: PlaywrightContextManager
    playwright: Playwright
    auto_download_browser: bool
    playwright_download_host: str | None

    launch_config: dict[str, Any] = {}  # 持久性上下文模式时储存的是持久性上下文的启动参数
    global_context_config: dict[str, Any] = {}  # 仅供非持久性上下文模式时储存全局上下文配置

    @overload
    def __init__(
        self,
        browser_type: Literal["chromium", "firefox", "webkit"] = "chromium",
        *,
        auto_download_browser: bool = True,
        playwright_download_host: str | None = None,
        install_with_deps: bool = False,
        user_data_dir: None = None,
        executable_path: str | Path | None = None,
        channel: str | None = None,
        args: list[str] | None = None,
        ignore_default_args: bool | list[str] | None = None,
        handle_sigint: bool | None = None,
        handle_sigterm: bool | None = None,
        handle_sighup: bool | None = None,
        timeout: float | None = None,
        env: dict[str, str | float | bool] | None = None,
        headless: bool | None = None,
        devtools: bool | None = None,
        downloads_path: str | Path | None = None,
        slow_mo: float | None = None,
        traces_dir: str | Path | None = None,
        chromium_sandbox: bool | None = None,
        firefox_user_prefs: dict[str, str | float | bool] | None = None,
        viewport: ViewportSize | None = None,
        screen: ViewportSize | None = None,
        no_viewport: bool | None = None,
        ignore_https_errors: bool | None = None,
        java_script_enabled: bool | None = None,
        bypass_csp: bool | None = None,
        user_agent: str | None = None,
        locale: str | None = None,
        timezone_id: str | None = None,
        geolocation: Geolocation | None = None,
        permissions: list[str] | None = None,
        extra_http_headers: dict[str, str] | None = None,
        offline: bool | None = None,
        http_credentials: HttpCredentials | None = None,
        device_scale_factor: float | None = None,
        is_mobile: bool | None = None,
        has_touch: bool | None = None,
        color_scheme: Literal["dark", "light", "no-preference", "null"] | None = None,
        reduced_motion: Literal["no-preference", "null", "reduce"] | None = None,
        forced_colors: Literal["active", "none", "null"] | None = None,
        accept_downloads: bool | None = None,
        default_browser_type: str | None = None,
        proxy: ProxySettings | None = None,
        record_har_path: str | Path | None = None,
        record_har_omit_content: bool | None = None,
        record_video_dir: str | Path | None = None,
        record_video_size: ViewportSize | None = None,
        storage_state: StorageState | str | Path | None = None,
        base_url: str | None = None,
        strict_selectors: bool | None = None,
        service_workers: Literal["allow", "block"] | None = None,
        record_har_url_filter: str | Pattern[str] | None = None,
        record_har_mode: Literal["full", "minimal"] | None = None,
        record_har_content: Literal["attach", "embed", "omit"] | None = None,
    ):
        ...

    @overload
    def __init__(
        self,
        browser_type: Literal["chromium", "firefox", "webkit"] = "chromium",
        *,
        auto_download_browser: bool = True,
        playwright_download_host: str | None = None,
        install_with_deps: bool = False,
        user_data_dir: str | Path,
        channel: str | None = None,
        executable_path: str | Path | None = None,
        args: list[str] | None = None,
        ignore_default_args: bool | list[str] | None = None,
        handle_sigint: bool | None = None,
        handle_sigterm: bool | None = None,
        handle_sighup: bool | None = None,
        timeout: float | None = None,
        env: dict[str, str | float | bool] | None = None,
        headless: bool | None = None,
        devtools: bool | None = None,
        proxy: ProxySettings | None = None,
        downloads_path: str | Path | None = None,
        slow_mo: float | None = None,
        viewport: ViewportSize | None = None,
        screen: ViewportSize | None = None,
        no_viewport: bool | None = None,
        ignore_https_errors: bool | None = None,
        java_script_enabled: bool | None = None,
        bypass_csp: bool | None = None,
        user_agent: str | None = None,
        locale: str | None = None,
        timezone_id: str | None = None,
        geolocation: Geolocation | None = None,
        permissions: list[str] | None = None,
        extra_http_headers: dict[str, str] | None = None,
        offline: bool | None = None,
        http_credentials: HttpCredentials | None = None,
        device_scale_factor: float | None = None,
        is_mobile: bool | None = None,
        has_touch: bool | None = None,
        color_scheme: Literal["dark", "light", "no-preference"] | None = None,
        reduced_motion: Literal["no-preference", "reduce"] | None = None,
        forced_colors: Literal["active", "none"] | None = None,
        accept_downloads: bool | None = None,
        traces_dir: str | Path | None = None,
        chromium_sandbox: bool | None = None,
        record_har_path: str | Path | None = None,
        record_har_omit_content: bool | None = None,
        record_video_dir: str | Path | None = None,
        record_video_size: ViewportSize | None = None,
        base_url: str | None = None,
        strict_selectors: bool | None = None,
        service_workers: Literal["allow", "block"] | None = None,
        record_har_url_filter: str | Pattern[str] | None = None,
        record_har_mode: Literal["full", "minimal"] | None = None,
        record_har_content: Literal["attach", "embed", "omit"] | None = None,
    ):
        ...

    def __init__(
        self,
        browser_type: Literal["chromium", "firefox", "webkit"] = "chromium",
        *,
        auto_download_browser: bool = True,
        playwright_download_host: str | None = None,
        install_with_deps: bool = False,
        **kwargs,
    ) -> None:
        self.browser_type: Literal["chromium", "firefox", "webkit"] = browser_type
        self.auto_download_browser = auto_download_browser
        self.playwright_download_host = playwright_download_host
        self.install_with_deps = install_with_deps

        if "user_data_dir" in kwargs and kwargs["user_data_dir"] is not None:
            self.use_persistent_context = True

        if "channel" in kwargs and kwargs["channel"] is not None:
            assert kwargs["channel"] in BROWSER_CHANNEL_TYPES, "channel must be one of " + ", ".join(BROWSER_CHANNEL_TYPES)

        if self.use_persistent_context:
            self.launch_config = kwargs
        else:
            for k, v in kwargs.items():
                if k in brower_config_list:
                    self.launch_config[k] = v
                if k in browser_context_config_list:
                    self.global_context_config[k] = v

        super().__init__()

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    async def _setup(self, browser_type: BrowserType):
        if self.use_persistent_context:
            log("info", N_("Playwright is currently starting in persistent context mode."))
            self._context = await browser_type.launch_persistent_context(**self.launch_config)
        else:
            self._browser = await browser_type.launch(**self.launch_config)
            self._context = await self._browser.new_context(**self.global_context_config)

    async def launch(self, m: Launart):
        if self.auto_download_browser:
            await install_playwright(
                self.playwright_download_host,
                self.browser_type,
                self.install_with_deps,
            )

        self.playwright_mgr = playwright_mgr = async_playwright()

        async with self.stage("preparing"):
            self.playwright = await playwright_mgr.__aenter__()
            browser_type = {
                "chromium": self.playwright.chromium,
                "firefox": self.playwright.firefox,
                "webkit": self.playwright.webkit,
            }[self.browser_type]
            need_install = False
            try:
                await self._setup(browser_type)
            except PWError as e:
                if "Executable doesn't exist" in str(e):
                    need_install = True
                else:
                    log(
                        "error",
                        N_(
                            "Unable to launch Playwright for {browser_type}, "
                            "please check the log output for the reason of failure. "
                            "It is possible that some system dependencies are missing. "
                            "You can set [magenta]`install_with_deps`[/] to [magenta]`True`[/] "
                            "to install dependencies when download browser."
                        ).format(browser_type=self.browser_type),
                    )
                    raise
            else:
                log("success", N_("Playwright for {browser_type} is started.").format(browser_type=self.browser_type))

            if need_install:
                await install_playwright(
                    self.playwright_download_host,
                    self.browser_type,
                    self.install_with_deps,
                )
                try:
                    await self._setup(browser_type)
                except PWError:
                    log(
                        "error",
                        N_(
                            "Unable to launch Playwright for {browser_type}, "
                            "please check the log output for the reason of failure. "
                            "It is possible that some system dependencies are missing. "
                            "You can set [magenta]`install_with_deps`[/] to [magenta]`True`[/] "
                            "to install dependencies when download browser."
                        ).format(browser_type=self.browser_type),
                    )
                    raise
                else:
                    log("success", N_("Playwright for {browser_type} is started.").format(browser_type=self.browser_type))

        async with self.stage("blocking"):
            await m.status.wait_for_sigexit()

        async with self.stage("cleanup"):
            # await self.context.close()  # 这里会卡住
            await playwright_mgr.__aexit__()

    async def restart(self):
        """重启 Playwright 浏览器"""
        await self.playwright_mgr.__aexit__()
        self.playwright = await self.playwright_mgr.__aenter__()
        browser_type = {
            "chromium": self.playwright.chromium,
            "firefox": self.playwright.firefox,
            "webkit": self.playwright.webkit,
        }[self.browser_type]
        try:
            await self._setup(browser_type)
        except PWError:
            log(
                "error",
                N_(
                    "Unable to launch Playwright for {browser_type}, "
                    "please check the log output for the reason of failure. "
                    "It is possible that some system dependencies are missing. "
                    "You can set [magenta]`install_with_deps`[/] to [magenta]`True`[/] "
                    "to install dependencies when download browser."
                ).format(browser_type=self.browser_type),
            )
            raise
        else:
            log("success", N_("Playwright for {browser_type} is restarted.").format(browser_type=self.browser_type))


# Patch
from graiax import playwright
playwright.PlaywrightService = PlaywrightService
