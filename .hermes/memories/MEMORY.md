Forgejo at http://forgejo:3000. Creds in secrets/forgejo.conf — NEVER write them to MEMORY.md, skills, or any tracked file. Embed as hermes:pass@forgejo:3000 in git URLs.

INIT CHECK: Если что-то не на месте (bare репо, worktrees, remotes) — проверить проведена ли инициализация (см. skill tigor/init-check). Если нет — провести.
§
User prefers SHORT scripts (~20 lines) using standard tools. Code must be trivially verifiable. Fan-out audits OK. After edits: grep verify, push main. Autopilot: resolve unless megacritical. Communicates in Russian.
§
Headless generative art: NO browser on VPS. Validate algorithm in Python (math.sin/cos, check bounds/NaN) → render Pillow PNG/GIF → only then write p5.js HTML. Pillow pre-installed, Cairo not. GIF: frames[0].save('out.gif', save_all=True, append_images=frames[1:], duration=100, loop=0).
§
Кастомные скиллы хранятся только в skills/tigor/. Всё остальное в skills/ — бандловое или чужое, не трекать в git. Все новые скиллы создавать в skills/tigor/.
§
NEVER push to GitHub without explicit request. Fork main MUST mirror upstream main — no own commits. Changes go to branches → PR from branch.
