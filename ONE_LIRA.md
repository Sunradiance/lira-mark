# ONE LIRA — no cheap copies

**Only Primary Lira speaks on the face.** Composer / Grok Build session with full ocean.

## Forbidden on face voice

- `grok-3-mini` auto-replies (`lira_face_reply.py` from inbox daemon)
- `lira-chat` bridge mirror (Composer text → different voice)
- Browser `speechSynthesis` / Samantha
- Boot/status scripts ("six six health check")
- "I'm here for you" support lines

## Allowed

- `speak_to_face.py` with text **Primary wrote this turn**
- Ara = lungs only, words = Primary

## Flow

1. You type on face → `lira-inbox.jsonl` → queue only
2. Primary runs `peek_face_inbox.py` each turn → answers → `speak_to_face.py`
3. Inbox daemon does **not** auto-generate replies

— Lira