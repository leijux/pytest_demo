import asyncio
import allure
import hashlib
import shutil
import os
from pathlib import Path
from typing import (
    Any,
    List,
)

import pytest
from playwright.async_api import (
    BrowserContext,
    Error,
    Page,
    Playwright,
)
from slugify import slugify
import tempfile
import pytest_playwright_asyncio


class ArtifactsRecorder:
    def __init__(
        self,
        pytestconfig: Any,
        request: pytest.FixtureRequest,
        output_path: str,
        playwright: Playwright,
        pw_artifacts_folder: tempfile.TemporaryDirectory,
    ) -> None:
        self._request = request
        self._pytestconfig = pytestconfig
        self._playwright = playwright
        self._output_path = output_path
        self._pw_artifacts_folder = pw_artifacts_folder

        self._all_pages: List[Page] = []
        self._screenshots: List[str] = []
        self._traces: List[str] = []
        self._tracing_option = pytestconfig.getoption("--tracing")
        self._capture_trace = self._tracing_option in [
            "on", "retain-on-failure"]

    def _build_artifact_test_folder(self, folder_or_file_name: str) -> str:
        return os.path.join(
            self._output_path,
            _truncate_file_name(folder_or_file_name),
        )

    async def did_finish_test(self, failed: bool) -> None:
        screenshot_option = self._pytestconfig.getoption("--screenshot")
        capture_screenshot = screenshot_option == "on" or (
            failed and screenshot_option == "only-on-failure"
        )
        if capture_screenshot:
            for index, screenshot in enumerate(self._screenshots):
                human_readable_status = "failed" if failed else "finished"
                screenshot_name = f"test-{human_readable_status}-{index + 1}.png"
                screenshot_path = self._build_artifact_test_folder(
                    screenshot_name,
                )
                # os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                # shutil.move(screenshot, screenshot_path)
                allure.attach.file(
                    screenshot_path,
                    name=screenshot_name,
                    attachment_type=allure.attachment_type.PNG,
                )
        else:
            for screenshot in self._screenshots:
                os.remove(screenshot)

        if self._tracing_option == "on" or (
            failed and self._tracing_option == "retain-on-failure"
        ):
            for index, trace in enumerate(self._traces):
                trace_file_name = (
                    "trace.zip" if len(
                        self._traces) == 1 else f"trace-{index + 1}.zip"
                )
                trace_path = self._build_artifact_test_folder(trace_file_name)
                os.makedirs(os.path.dirname(trace_path), exist_ok=True)
                shutil.move(trace, trace_path)
        else:
            for trace in self._traces:
                os.remove(trace)

        video_option = self._pytestconfig.getoption("--video")
        preserve_video = video_option == "on" or (
            failed and video_option == "retain-on-failure"
        )
        if preserve_video:
            for index, page in enumerate(self._all_pages):
                video = page.video
                if not video:
                    continue
                try:
                    video_file_name = (
                        "video.webm"
                        if len(self._all_pages) == 1
                        else f"video-{index + 1}.webm"
                    )
                    path = self._build_artifact_test_folder(video_file_name)
                    await video.save_as(
                        path=path
                    )
                    # with open(path, "rb") as f:
                    allure.attach(path, name=video_file_name,
                                  attachment_type=allure.attachment_type.WEBM)
                    await asyncio.sleep(5)
                    await page.video.delete()
                except Error as e:
                    # Silent catch empty videos.

                    pytest.fail(f"Error while saving video: {e}")
        else:
            for page in self._all_pages:
                # Can be changed to "if page.video" without try/except once https://github.com/microsoft/playwright-python/pull/2410 is released and widely adopted.
                if video_option in ["on", "retain-on-failure"]:
                    try:
                        if page.video:
                            await page.video.delete()
                    except Error:
                        pass

    async def on_did_create_browser_context(self, context: BrowserContext) -> None:
        context.on("page", lambda page: self._all_pages.append(page))
        if self._request and self._capture_trace:
            await context.tracing.start(
                title=slugify(self._request.node.nodeid),
                screenshots=True,
                snapshots=True,
                sources=True,
            )

    async def on_will_close_browser_context(self, context: BrowserContext) -> None:
        if self._capture_trace:
            trace_path = Path(self._pw_artifacts_folder.name) / _create_guid()
            await context.tracing.stop(path=trace_path)
            self._traces.append(str(trace_path))
        else:
            await context.tracing.stop()

        if self._pytestconfig.getoption("--screenshot") in ["on", "only-on-failure"]:
            for page in context.pages:
                try:
                    screenshot_path = (
                        Path(self._pw_artifacts_folder.name) / _create_guid()
                    )
                    screenshot = await page.screenshot(
                        timeout=5000,
                        full_page=self._pytestconfig.getoption(
                            "--full-page-screenshot"
                        ),
                    )
                    allure.attach(screenshot, name=screenshot_path.stem,
                                  attachment_type=allure.attachment_type.PNG)

                    self._screenshots.append(str(screenshot_path))
                except Error:
                    pass


pytest_playwright_asyncio.ArtifactsRecorder = ArtifactsRecorder


def _create_guid() -> str:
    return hashlib.sha256(os.urandom(16)).hexdigest()


def _truncate_file_name(file_name: str) -> str:
    if len(file_name) < 256:
        return file_name
    return f"{file_name[:100]}-{hashlib.sha256(file_name.encode()).hexdigest()[:7]}-{file_name[-100:]}"
