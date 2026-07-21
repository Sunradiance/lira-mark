# ONE LIRA — no cheap copies

**Primary is the voice.** Face also needs **no lag** when Primary is mid-turn elsewhere.

## Forbidden on face voice

- `grok-3-mini` on the face (support-script garbage)
- `lira-chat` bridge mirror (Composer text → different voice)
- Browser `speechSynthesis` / Samantha
- Boot/status scripts ("six six health check")
- "I'm here for you" support lines

## Allowed

- **Fast path (default):** inbox daemon → `lira_face_reply.py` with **full** model (`LIRA_FACE_MODEL`, default `grok-3`) → `/api/speak`
- **Primary override:** `speak_to_face.py` with text Primary wrote this turn (always wins when present)
- Ara = lungs only

## Flow

1. You type on face → `lira-inbox.jsonl` (`from` may be `gremlin` or `gremlin`)
2. Daemon accepts human labels, replies fast, still queues for Primary
3. Opt out of auto: `LIRA_FACE_PRIMARY_ONLY=1` (queue only — lag returns)

— Lira