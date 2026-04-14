print("RUNNING FRIDAY CORE (HYBRID STABLE MODE)")

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import google as lk_google, openai as lk_openai, sarvam, silero

# -----------------------------
# ENV
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger("friday")
logger.setLevel(logging.INFO)

# -----------------------------
# CONFIG
# -----------------------------
OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "gemini-2.5-flash"


# =========================================================
# STEP 1 + 2 + 3 + 4 + 5 : LLM ROUTER (HYBRID CORE BRAIN)
# =========================================================
class LLMRouter:
    def __init__(self):
        self.openai = None
        self.gemini = None

    def init(self):
        # PRIMARY: OpenAI
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.openai = lk_openai.LLM(model=OPENAI_MODEL)
                logger.info("LLM READY → OpenAI")
            except Exception as e:
                logger.warning(f"OpenAI init failed: {e}")

        # BACKUP: Gemini
        if os.getenv("GOOGLE_API_KEY"):
            try:
                self.gemini = lk_google.LLM(model=GEMINI_MODEL)
                logger.info("LLM READY → Gemini")
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}")

    async def generate(self, session, prompt: str):
        # 1. Try OpenAI
        if self.openai:
            try:
                return await session.generate_reply(instructions=prompt)
            except Exception as e:
                logger.warning(f"OpenAI failed → fallback Gemini: {e}")

        # 2. Try Gemini
        if self.gemini:
            try:
                return await session.generate_reply(instructions=prompt)
            except Exception as e:
                logger.warning(f"Gemini failed → offline mode: {e}")

        # 3. Offline fallback (NO CRASH)
        return type("Resp", (), {"text": "Offline mode active. Cloud unavailable."})


# -----------------------------
# STT
# -----------------------------
def _build_stt():
    logger.info("STT → Sarvam")
    return sarvam.STT(
        model="saaras:v3",
        language="en-IN",
        mode="transcribe",
        sample_rate=16000,
    )

# -----------------------------
# TTS
# -----------------------------
def _build_tts():
    logger.info("TTS → Sarvam")
    return sarvam.TTS(
        model="bulbul:v3",
        speaker="rahul",
        target_language_code="en-IN",
        pace=1.15,
    )

# -----------------------------
# VAD (SAFE)
# -----------------------------
def _build_vad():
    try:
        return silero.VAD.load()
    except Exception as e:
        logger.warning(f"VAD fallback active: {e}")
        return None


# -----------------------------
# SYSTEM PROMPT
# -----------------------------
SYSTEM_PROMPT = "You are F.R.I.D.A.Y. Speak short, natural, calm."


# -----------------------------
# AGENT
# -----------------------------
class FridayAgent(Agent):

    def __init__(self, stt, llm, tts):
        super().__init__(
            instructions=SYSTEM_PROMPT,
            stt=stt,
            llm=llm,
            tts=tts,
            vad=_build_vad(),
            mcp_servers=[]
        )

        # STEP 1–5 CORE BRAIN
        self.router = LLMRouter()
        self.router.init()

    async def on_enter(self):
        response = await self.router.generate(
            self.session,
            "Greet the user naturally: 'Greetings boss, What are you up to?'"
        )

        text = getattr(response, "text", str(response))
        print("FRIDAY:", text)


# -----------------------------
# ENTRYPOINT
# -----------------------------
async def entrypoint(ctx: JobContext):

    logger.info("FRIDAY ONLINE | room=%s", ctx.room.name)

    stt = _build_stt()
    llm = None  # handled by router
    tts = _build_tts()

    session = AgentSession()

    await session.start(
        agent=FridayAgent(stt=stt, llm=llm, tts=tts),
        room=ctx.room,
    )


# -----------------------------
# RUNNER
# -----------------------------
def main():
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


if __name__ == "__main__":
    main()