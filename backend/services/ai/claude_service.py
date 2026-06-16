# ============================================================
# Claude Service — AWS Bedrock Claude API Client
# ============================================================
import json
import time
import threading
from typing import Any, Dict, List, Optional
import requests
from backend.config import (
    AI_MAX_RETRIES, AI_RATE_LIMIT_RPM, AI_REQUEST_TIMEOUT,
    BEDROCK_DEFAULT_MODEL, BEDROCK_DEFAULT_REGION,
)
from backend.core.logger import get_logger

log = get_logger("claude")


class ClaudeService:
    """AWS Bedrock Claude API client with retries, rate limiting, token monitoring."""

    def __init__(self):
        self._api_key: str = ""
        self._region: str = BEDROCK_DEFAULT_REGION
        self._model_id: str = BEDROCK_DEFAULT_MODEL
        self._request_times: List[float] = []
        self._lock = threading.Lock()
        self._total_input_tokens = 0
        self._total_output_tokens = 0

    def configure(self, api_key: str, region: str = "", model_id: str = ""):
        """Set API credentials."""
        self._api_key = api_key
        if region:
            self._region = region
        if model_id:
            self._model_id = model_id
        log.info(f"Claude configured: region={self._region}, model={self._model_id}")

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    @property
    def api_url(self) -> str:
        return f"https://bedrock-runtime.{self._region}.amazonaws.com/model/{self._model_id}/invoke"

    @property
    def token_usage(self) -> Dict:
        return {
            "input_tokens": self._total_input_tokens,
            "output_tokens": self._total_output_tokens,
            "total_tokens": self._total_input_tokens + self._total_output_tokens,
        }

    def _rate_limit_wait(self):
        """Enforce rate limit (requests per minute)."""
        with self._lock:
            now = time.time()
            # Remove requests older than 60s
            self._request_times = [t for t in self._request_times if now - t < 60]
            if len(self._request_times) >= AI_RATE_LIMIT_RPM:
                oldest = self._request_times[0]
                wait = 60 - (now - oldest) + 0.1
                if wait > 0:
                    log.warning(f"Rate limit: waiting {wait:.1f}s")
                    time.sleep(wait)
            self._request_times.append(time.time())

    def call(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.2,
        system: str = "",
    ) -> str:
        """Make a Claude API call with retries and rate limiting.

        Returns response text or empty string on failure.
        """
        if not self._api_key:
            log.warning("Claude not configured — no API key")
            return ""

        self._rate_limit_wait()

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload: Dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt}]},
            ],
        }
        if system:
            payload["system"] = system

        last_error = None
        for attempt in range(1, AI_MAX_RETRIES + 1):
            try:
                resp = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=AI_REQUEST_TIMEOUT,
                )
                resp.raise_for_status()
                result = resp.json()

                # Track token usage
                usage = result.get("usage", {})
                self._total_input_tokens += usage.get("input_tokens", 0)
                self._total_output_tokens += usage.get("output_tokens", 0)

                text = result["content"][0]["text"]
                return text

            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response else 0
                last_error = e
                if status == 429:
                    # Rate limited by API — exponential backoff
                    wait = 2 ** attempt
                    log.warning(f"Rate limited (429). Retry {attempt}/{AI_MAX_RETRIES} in {wait}s")
                    time.sleep(wait)
                elif status >= 500:
                    wait = 2 ** attempt
                    log.warning(f"Server error ({status}). Retry {attempt}/{AI_MAX_RETRIES} in {wait}s")
                    time.sleep(wait)
                else:
                    log.error(f"HTTP {status}: {e}")
                    break
            except requests.exceptions.Timeout:
                last_error = TimeoutError("Request timed out")
                log.warning(f"Timeout. Retry {attempt}/{AI_MAX_RETRIES}")
                time.sleep(1)
            except Exception as e:
                last_error = e
                log.error(f"Unexpected error: {e}")
                break

        log.error(f"Claude call failed after {AI_MAX_RETRIES} retries: {last_error}")
        return ""

    def call_json(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.1,
        system: str = "",
    ) -> Optional[Dict]:
        """Call Claude and parse response as JSON.

        Returns parsed dict or None on failure.
        """
        text = self.call(prompt, max_tokens, temperature, system)
        if not text:
            return None
        try:
            # Find JSON in response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
            # Try array
            start = text.find("[")
            end = text.rfind("]") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError as e:
            log.warning(f"JSON parse failed: {e}")
        return None


# Singleton
claude_service = ClaudeService()
