{
  "title": "Gold Panning in Nova Scotia",
  "slug": "gold-panning-nova-scotia",
  "subtitle": "A Field Guide to the Meguma Gold Country",
  "requester": "Dan (self/internal run)",
  "topic": "Gold panning in Nova Scotia — all aspects including how to find good spots",
  "status": "public-safe",
  "permission_to_publish": true,
  "length_mode": "Standard beta book (~2 hours)",
  "word_count": 17823,
  "chapter_count": 10,
  "estimated_runtime": "7069s / ~1h 58m at 1.0x, ~1h 35m at 1.25x",
  "narrator": "am_michael",
  "author": "Dan Fakkeldy",
  "frontier_author_model": "GLM-5.2 (zai)",
  "review_production_roles": "Cheap editorial reviewer (delegate_task) for citation-first content findings; prose_qc.py for repetition/structure checks",
  "research_mode": "Deep",
  "source_confidence": "deep — multiple source classes compared (NS government primary sources, Mining Association of Nova Scotia, academic geology, Wikipedia cross-references)",
  "sensitive_topic_guardrails": "Arsenic/mercury tailings safety warning included in Ch10. Recreational panning legal framework covered in Ch5 and Ch9. No professional mining/geological advice given.",
  "figure_count": 0,
  "cover_directions": [
    {
      "id": 1,
      "name": "Stream Still Life",
      "description": "Documentary still life — a weathered gold pan in a Nova Scotia stream bed with a gold flake visible in the dark concentrate. Dark green/water palette, bright gold accent. bleed layout.",
      "accent": "#FFD700",
      "tone": "dark"
    },
    {
      "id": 2,
      "name": "Gold Specimen",
      "description": "Editorial hero object — a single crystalline gold specimen dramatically lit against dark Meguma bedrock with quartz veins. Charcoal black palette, warm gold accent. bleed layout.",
      "accent": "#E8B530",
      "tone": "dark"
    },
    {
      "id": 3,
      "name": "Field Notebook",
      "description": "Tactile collage / field-note illustration — a hand-drawn archival-style field-notebook page with a geological anticline cross-section, a gold pan sketch, and a map fragment marking Mooseland. Warm cream paper, brown ink, bright gold accents. High-key. hero layout.",
      "accent": "#F4C430",
      "tone": "bright"
    }
  ],
  "selected_cover": "cover-1 (Stream Still Life) — dark documentary, green/water palette, bright gold accent",
  "output_files": {
    "epub": "dist/gold-panning-nova-scotia.epub",
    "markdown": "dist/gold-panning-nova-scotia.md",
    "m4b": "dist/gold-panning-nova-scotia.m4b",
    "alignment_json": "dist/gold-panning-nova-scotia.alignment.json",
    "cover": "dist/cover.png",
    "cover_candidates": ["dist/cover-1.png", "dist/cover-2.png", "dist/cover-3.png"]
  },
  "qc_gates": {
    "phase_a_style_sweep": "PASSED — no code leaks, no dead phrases, 1 emphasis hit ('heart of gold country' — natural geographic usage, retained), no tradeoff drone",
    "phase_b_editorial_review": "PASSED — 6 findings identified and all resolved by frontier author (1 factual conflict, 1 voice tic, 1 jargon, 1 unclear mechanism, 2 redundancy)",
    "prose_qc_script": "PASSED — repeated phrases reviewed against coverage ledger, all intentional retrievals except 1 verbatim duplication (tightened in Ch5)",
    "heading_consistency": "PASSED — all 10 chapters use '## Chapter N — Title' format",
    "epub_validity": "PASSED — unzip clean, mimetype first entry stored uncompressed",
    "word_count": "17,823 words — within standard beta book range (18k-22k target, slightly under due to tight chapter work; no padding added)",
    "audio_render": "PASSED — echo-cli narrate am_michael, 10 chapters, 7069s audio in 5324s wall (1.3x realtime)",
    "alignment_json": "PASSED — valid JSON, 192 anchors",
    "m4b_duration": "PASSED — 7069.1s (~1h 58m at 1.0x)"
  },
  "throughlines": [
    "NS gold is Meguma gold — the bedrock geology drives everything",
    "Glaciers changed the rules — NS placer gold is sparse compared to the Yukon",
    "The old districts are your map — 65 historical districts guide where to pan",
    "The rules are part of the craft — staked ground, tailings, hand-pan-only"
  ],
  "humanizer_pass": "Not applied (skipped) — manuscript reviewed clean by frontier author after editorial repairs. No AI tics detected in style sweep."
}
