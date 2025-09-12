import asyncio
import os
import re
import subprocess
import sys
import signal
from contextlib import nullcontext
from dataclasses import dataclass
from urllib.parse import urlparse

from playwright._impl._driver import compute_driver_executable, get_driver_env

from graiax.playwright.i18n import N_
from .utils import Progress, log
from .signal import (
    register_signal_handler,
    remove_signal_handler,
    shield_signals,
)

download_complete = re.compile("(?P<file>.*) downloaded to (?P<path>.*)")
percent_pat = re.compile("(\\d+)%")
ascii_pat = re.compile("\x1b.*?m")


@dataclass(frozen=True)
class MirrorSource:
    name: str
    url: str
    priority: int


MIRRORS = [
    MirrorSource("Default", "https://playwright.azureedge.net", 1),
    MirrorSource("Taobao", "https://registry.npmmirror.com/-/binary/playwright", 2),
]


async def terminate_process(process: asyncio.subprocess.Process) -> None:
    """
    终止一个进程。

    Args:
        process: 要终止的进程。
    """
    if process.returncode is not None:
        return

    context = shield_signals() if sys.platform.startswith("win") or os.name == "nt" else nullcontext()

    with context:
        if sys.platform.startswith("win") or os.name == "nt":
            os.kill(process.pid, signal.CTRL_BREAK_EVENT)
        else:
            try:
                pgid = os.getpgid(process.pid)
                os.killpg(pgid, signal.SIGTERM)
            except ProcessLookupError:
                process.terminate()

        try:
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            if not (sys.platform.startswith("win") or os.name == "nt"):
                try:
                    pgid = os.getpgid(process.pid)
                    os.killpg(pgid, signal.SIGKILL)
                except ProcessLookupError:
                    process.kill()
            else:
                process.kill()
            await process.wait()


async def create_process(*command, env: dict | None = None):
    should_exit = asyncio.Event()

    def shutdown(sig, frame):
        should_exit.set()

    register_signal_handler(shutdown)

    async def wait_for_exit():
        await should_exit.wait()
        await terminate_process(shell)

    async def wait_for_process():
        await shell.wait()
        should_exit.set()


    if sys.platform.startswith("win") or os.name == "nt":
        shell = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        shell = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            env=env,
            creationflags=0,
            start_new_session=True,
        )

    exit_task = asyncio.create_task(wait_for_exit())
    wait_task = asyncio.create_task(wait_for_process())
    wait_task.add_done_callback(lambda t: remove_signal_handler(shutdown))

    return shell, exit_task, wait_task


async def check_mirror_connectivity(timeout: int = 5) -> MirrorSource | None:
    """检查镜像源的可用性并返回最佳镜像源。

    Args:
        timeout (int): 连接超时时间。

    Returns:
        Optional[MirrorSource]: 可用的最佳镜像源，如果没有可用镜像则返回 None。
    """

    async def _check_single_mirror(mirror: MirrorSource) -> tuple[MirrorSource, float]:
        """检查单个镜像源的可用性。"""
        try:
            parsed_url = urlparse(mirror.url)
            host = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)

            start_time = asyncio.get_event_loop().time()

            _, _ = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=timeout
            )

            elapsed = asyncio.get_event_loop().time() - start_time
            return mirror, round(elapsed, 2)

        except Exception as e:
            log("debug", f"镜像源 {mirror.name} 连接失败: [red]{e!r}[/]")
        return mirror, float("inf")

    mirrors = MIRRORS
    tasks = [_check_single_mirror(mirror) for mirror in mirrors]
    results: list[tuple[MirrorSource, float]] = await asyncio.gather(*tasks)

    available_mirrors = [(m, t) for m, t in results if t != float("inf")]
    if not available_mirrors:
        return None

    log("debug", f"available_mirrors: {available_mirrors}")
    return min(available_mirrors, key=lambda x: (x[1], -x[0].priority))[0]


async def install_playwright(
    download_host: str | None = None,
    browser_type: str = "chromium",
    install_with_deps: bool = False,
):
    env = get_driver_env()
    env["PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT"] = "300000"
    if download_host:
        env["PLAYWRIGHT_DOWNLOAD_HOST"] = download_host
    elif best_mirror := await check_mirror_connectivity():
        log(
            "info",
            f"Using Mirror source: [cyan]{best_mirror.name}[/] {best_mirror.url}"
        )
        env["PLAYWRIGHT_DOWNLOAD_HOST"] = best_mirror.url

    if install_with_deps:
        command = list(compute_driver_executable()) + ["install", "--with-deps", browser_type]
        if sys.platform.startswith("win") or os.name == "nt":
            log(
                "info",
                N_(
                    "Start download Playwright for {browser_type} with dependencies, "
                    "may require administrator privileges from you."
                ).format(browser_type=browser_type),
            )
        else:
            log(
                "info",
                N_(
                    "Start download Playwright for {browser_type} with dependencies, may require you to access sudo."
                ).format(browser_type=browser_type),
            )
    else:
        command = list(compute_driver_executable()) + ["install", browser_type]
        log("info", N_("Start download Playwright for {browser_type}.").format(browser_type=browser_type))
    shell, t1, t2 = await create_process(*command, env=env)
    returncode = None

    assert shell.stdout

    progress: Progress | None = None

    while line := re.sub(ascii_pat, "", (await shell.stdout.readline()).decode("UTF-8")):
        if "Downloading" in line:
            progress = Progress(line[12:-1])
        if percent := percent_pat.findall(line):
            progress_target = float(percent[0])
            if progress:
                progress.update(target=progress_target)
        elif p := download_complete.match(line):
            p = p.groupdict()
            log(
                "success", N_("Downloaded [cyan]{file}[/] to [magenta]{path}[/]").format(file=p["file"], path=p["path"])
            )
        elif line == "Failed to install browsers\n":
            message = await shell.stdout.read()
            log("error", N_("Download Failed:\n") + message.decode("UTF-8"))
            returncode = 1

    if returncode or shell.returncode:
        log("error", N_("Failed to download Playwright for {browser_type}.").format(browser_type=browser_type))
        log("error", N_("Please see: [magenta]https://playwright.dev/python/docs/intro[/]"))
        log(
            "error",
            N_(
                "Run [magenta]poetry run playwright install[/] or "
                "[magenta]pdm run playwright install[/] to install Playwright manually."
            ),
        )
    else:
        log("success", N_("Playwright for {browser_type} is installed.").format(browser_type=browser_type))
