# Home Living and Interior Design articles: writing spec

Owner decision, 12 Nov 2026: the site (AstroFusion Living, `vastu.astro-fusion.com`) is a happy-home product. Two new article topics sit next to Vastu: **Home Living** (`22_Home_Living`) and **Interior Design** (`23_Interior_Design`). They are published at `/{en,hi,ne}/articles/<topic>/<section>/<slug>`. English is written first; Hindi and Nepali follow from the English.

These are new, original articles. There is no source text. They must be useful to a person arranging a real home in Nepal or India.

## Reader

A home owner or tenant in Nepal or India: a flat of 500 to 1,200 sq ft or a two to three storey family house, an ordinary budget, a carpenter or contractor they deal with directly. Not a designer, not an engineer.

## What every article must contain

1. A plain opening of 2 to 4 sentences that says what the reader will be able to do after reading. No "in today's fast-paced world", no history lesson.
2. Real numbers: clearances, sizes, heights, distances. Metric first with feet and inches in brackets, for example "75 cm (2 ft 6 in)". Use common furniture sizes sold in Nepal and India (a double bed about 150 x 190 cm, a queen about 152 x 198 cm, a king about 180 x 198 cm, a single about 90 x 190 cm).
3. One worked example on a real room size, for example "a 3.0 x 3.6 m (10 x 12 ft) bedroom", walked through step by step with the arithmetic shown.
4. A short checklist the reader can follow with a tape measure.
5. A section of common mistakes (3 to 5).
6. A FAQ section with 4 to 6 questions a real person would ask, answered from the article.
7. A closing line that points to one tool ("You can try this layout in Spaces, the floor-plan editor in AstroFusion Living") without a link. Links are added by the site.

Length: 900 to 1,500 words of body text. Do not pad.

## Rules

- No invented statistics, studies, surveys or percentages. No "research shows" unless the study is named, and prefer to leave it out.
- No promises about health, sleep quality, wealth, relationships, productivity or mood. Say what a choice does physically (more daylight, easier movement, less glare, easier cleaning).
- No brand names, no shop names, no prices in currency. "Low, medium, high cost" is fine.
- Dimensions are common practice, stated as "a comfortable minimum is" or "aim for". Never present them as a legal requirement.
- Anything about structure, electrical wiring, gas, waterproofing, removing a wall, loads on a slab or balcony: say what to ask and tell the reader to use a licensed engineer or electrician. Never give structural or electrical design advice.
- Damp, mould, heat: explain causes and simple measures (ventilation, sun, fixing leaks) and when to call a professional. No medical claims.
- Vastu: these are not Vastu articles. At most one short paragraph may say what Vastu tradition prefers for the room, worded as tradition ("Vastu tradition places the master bedroom in the south-west"), and only where it is a well-known rule. Never as advice, never as a reason.
- Climate and context: monsoon damp, hot summers in the Terai and the plains, cold winters in the hills, power cuts, water tanks on roofs, joint families, a puja space, shoes off at the door, wet bathrooms. Use them where relevant.
- No anonymous success stories. An example is an illustration ("take a family of five in a 2BHK").
- Write plainly. Short sentences. Second person. No sales tone.

## Format

Plain Markdown only. No JSX, no HTML, no `<`, `>`, `{`, `}` characters in the body (write "less than"). No links to other websites. Tables are fine.

Frontmatter, exactly these keys in this order:

```yaml
---
title: "<30 to 65 characters, says what the article covers>"
description: "<110 to 160 characters>"
pubDate: '2026-11-13'
modifiedDate: '2026-11-13'
locale: 'en'
author: 'AstroFusion Editorial'
keywords:
  - "<5 to 8 search phrases people type>"
---
```

Body: one `# ` heading equal to the title, then `## ` sections and `### ` subsections. FAQ: a `## ` heading, each question as `### `. End the file with one newline.

File path: `en/<topic folder>/<section folder>/<number>_<snake_case_slug>.mdx`, exactly as listed below. Create the folders. Do not create `_meta.json` or index files; another package generates them.

For Hindi and Nepali later: same path under `hi/` or `ne/`, `locale` changed, `sourceLocale: 'en'` added after `locale`, and the language rules of `docs/vastu-locale-articles-spec.md` (standard Hindi or Nepali, Latin digits, real Nepali vocabulary).

## Article list

### 22_Home_Living / 2201_Room_by_Room

| File | Working title |
|---|---|
| 220101_setting_up_a_small_bedroom.mdx | Setting up a small bedroom: bed, wardrobe and walking space |
| 220102_living_room_for_a_family_of_five.mdx | A living room that seats a family of five |
| 220103_kitchen_work_triangle_and_counter_heights.mdx | Kitchen layout: the work triangle and counter heights |
| 220104_study_corner_in_a_shared_room.mdx | Making a study corner in a shared room |
| 220105_childrens_room_that_grows_with_the_child.mdx | A children's room that grows with the child |
| 220106_room_for_elderly_parents.mdx | A safe, easy room for elderly parents |
| 220107_entrance_and_shoe_area.mdx | The entrance: shoes, bags and a place to sit |
| 220108_bathroom_layout_wet_and_dry_areas.mdx | Bathroom layout: keeping wet and dry areas apart |
| 220109_dining_space_in_a_small_home.mdx | A dining space in a small home |
| 220110_puja_space_in_a_modern_flat.mdx | A puja space in a modern flat |

### 22_Home_Living / 2202_Small_Homes_and_Flats

| File | Working title |
|---|---|
| 220201_making_a_2bhk_feel_bigger.mdx | Making a 2BHK feel bigger without breaking a wall |
| 220202_storage_in_a_600_sq_ft_flat.mdx | Storage in a 600 sq ft flat |
| 220203_one_room_two_uses.mdx | One room, two uses: guest room and study |
| 220204_studio_and_single_room_living.mdx | Living well in a single room |
| 220205_balcony_as_a_usable_room.mdx | Turning a balcony into a usable space |
| 220206_under_stair_and_loft_storage.mdx | Under-stair and loft storage done properly |
| 220207_furniture_sizes_for_small_rooms.mdx | Furniture sizes that fit small rooms |
| 220208_joint_family_in_a_three_bedroom_home.mdx | A joint family in a three-bedroom home |
| 220209_working_from_home_in_a_small_flat.mdx | Working from home in a small flat |
| 220210_decluttering_room_by_room.mdx | Decluttering room by room: a practical order |

### 22_Home_Living / 2203_Light_Air_and_Comfort

| File | Working title |
|---|---|
| 220301_daylight_in_a_north_facing_room.mdx | Getting more daylight into a north-facing room |
| 220302_cross_ventilation_basics.mdx | Cross ventilation: how air really moves through a home |
| 220303_keeping_a_top_floor_flat_cool.mdx | Keeping a top-floor flat cool in summer |
| 220304_keeping_a_home_warm_in_a_hill_winter.mdx | Keeping a home warm in a hill winter |
| 220305_damp_and_mould_causes_and_first_steps.mdx | Damp and mould: causes and first steps |
| 220306_monsoon_proofing_your_home.mdx | Getting your home ready for the monsoon |
| 220307_reducing_noise_in_a_city_flat.mdx | Reducing noise in a city flat |
| 220308_curtains_blinds_and_privacy.mdx | Curtains, blinds and privacy without losing light |
| 220309_indoor_plants_that_survive.mdx | Indoor plants that survive, and where to put them |
| 220310_kitchen_smoke_and_smell_ventilation.mdx | Kitchen smoke and smell: chimney, exhaust fan and windows |

### 23_Interior_Design / 2301_Layout_and_Furniture

| File | Working title |
|---|---|
| 230101_clearances_around_bed_sofa_and_table.mdx | Clearances around a bed, a sofa and a dining table |
| 230102_arranging_a_long_narrow_room.mdx | Arranging a long, narrow room |
| 230103_sofa_and_tv_distances.mdx | Sofa and TV: viewing distance and height |
| 230104_wardrobe_planning_and_internal_layout.mdx | Planning a wardrobe: width, depth and inside layout |
| 230105_door_swings_and_circulation_paths.mdx | Door swings and walking paths |
| 230106_modular_kitchen_planning.mdx | Planning a modular kitchen: shapes, sizes and order of work |
| 230107_bed_placement_and_side_tables.mdx | Where to put the bed, and what goes beside it |
| 230108_open_plan_living_and_dining.mdx | Open living and dining: zoning without walls |
| 230109_mirrors_shelves_and_wall_heights.mdx | Hanging heights for mirrors, shelves, switches and pictures |
| 230110_reading_a_floor_plan.mdx | How to read a floor plan before you buy or rent |

### 23_Interior_Design / 2302_Colour_Light_and_Materials

| File | Working title |
|---|---|
| 230201_choosing_wall_colours_by_light.mdx | Choosing wall colours by the light a room gets |
| 230202_warm_and_cool_lamps.mdx | Warm and cool lamps: which light for which room |
| 230203_layered_lighting_for_a_living_room.mdx | Layered lighting for a living room |
| 230204_flooring_for_nepali_and_indian_climates.mdx | Flooring for Nepali and Indian climates |
| 230205_paint_finishes_and_where_to_use_them.mdx | Paint finishes and where to use each |
| 230206_wood_plywood_and_laminates.mdx | Wood, plywood and laminates: what furniture is made of |
| 230207_tiles_for_bathrooms_and_kitchens.mdx | Tiles for bathrooms and kitchens: size, grip and grout |
| 230208_making_a_low_ceiling_feel_higher.mdx | Making a low ceiling feel higher |
| 230209_colour_for_a_small_room.mdx | Colour in a small room: what really helps |
| 230210_fabrics_rugs_and_soft_furnishings.mdx | Fabrics, rugs and soft furnishings that last |

### 23_Interior_Design / 2303_Budget_and_Planning

| File | Working title |
|---|---|
| 230301_what_to_do_first_on_a_small_budget.mdx | What to do first on a small budget |
| 230302_working_with_a_carpenter.mdx | Working with a carpenter: drawings, measurements and checks |
| 230303_working_with_a_contractor.mdx | Working with a contractor: scope, stages and handover |
| 230304_order_of_work_in_a_home_renovation.mdx | The right order of work in a home renovation |
| 230305_measuring_a_room_properly.mdx | Measuring a room properly |
| 230306_estimating_paint_and_tiles.mdx | Estimating paint and tiles before you buy |
| 230307_renting_improvements_you_can_take_with_you.mdx | Renting: improvements you can take with you |
| 230308_furnishing_a_new_home_in_stages.mdx | Furnishing a new home in stages |
| 230309_electrical_points_planning_checklist.mdx | Planning switches and sockets: a checklist to give your electrician |
| 230310_handover_checklist_for_a_new_flat.mdx | A handover checklist for a new flat |
