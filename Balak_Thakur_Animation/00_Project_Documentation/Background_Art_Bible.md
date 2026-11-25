# 🎨 STUDIO GHIBLI BACKGROUND ART BIBLE & SCENIC ROADMAP
## Project: Param Bismoy Balak Thakur (পরম বিস্ময় বালক ঠাকুর)
### Setting: Rural Bengal (Ujanchar, Kaulipara, Medinimandal, Dogachhi, Titas River — 1920s)

> [!NOTE]
> **Execution Status**: **PLANNED & STRUCTURED FOR NEXT PRODUCTION PHASE**.
> This document specifies the visual style, color palettes, multiplane layer slicing, and prompt formulas for all background environments across Episodes 1–5. Actual asset painting/rendering will be executed in a dedicated upcoming session.

---

## 🌿 1. Visual Pillars: Studio Ghibli Hand-Painted Aesthetic

Following the legendary scenic artistry of **Kazuo Oga** (*My Neighbor Totoro*, *Princess Mononoke*) and Studio Ghibli background traditions:

1. **Gouache & Watercolor Texture**:
   * Rich, tactile brushwork with visible wet-edge watercolor bleeding and dry gouache highlights on rough watercolor paper grain.
   * Zero flat vector shapes; zero harsh synthetic gradients.
2. **Atmospheric Lighting & Luminous Nature**:
   * Dappled sunlight (*komorebi*) filtering through ancient banyan (*bot-gach*), mango groves (*aam-bagan*), and banana leaves (*kola-pata*).
   * Warm, radiant, golden-hour morning light; nostalgic indigo twilight with fireflies and earthen oil lamps.
3. **Authentic 1920s Rural Bengal Topography**:
   * Earth-baked clean mud courtyards (*maatir uthon*) swept clean with straw brooms.
   * River Titas with wooden country ferry boats (*kheya nouka*) and sprawling banks of white Kash flowers (*kaash phool*).
   * Tin-roof bungalows, thatched huts (*chala ghor*), clay stoves (*unoon*), and brass water jars (*kolshi*).

---

## 🗂 2. Master Background Directory Structure

```
Balak_Thakur_Animation/06_Backgrounds/
├── BG01_Ancestral_Courtyard_Day/          <-- Ep 1 & 2: Courtyard, Tulsi mancha, veranda
│   ├── Layer0_FG_Foliage.png
│   ├── Layer1_Veranda_Ground.png
│   ├── Layer2_MG_MudHuts.png
│   └── Layer3_BG_Sky_Trees.png
│
├── BG02_Kali_Puja_Night/                  <-- Ep 1: Dipanwita festival midnight, lamps, mist
│   ├── Layer0_FG_Pradeep_Hanging.png
│   ├── Layer1_Courtyard_Dhup.png
│   └── Layer2_BG_Midnight_Sky.png
│
├── BG03_Pond_and_Banyan_Grove/            <-- Ep 2: Pond, turtles, water lilies, roots
│   ├── Layer0_FG_Lilypads.png
│   ├── Layer1_Water_Reflections.png
│   └── Layer2_Banyan_Roots.png
│
├── BG04_Titas_Riverbank_Sunset/           <-- Ep 3: Kash flowers, river ripples, sunset
│   ├── Layer0_FG_Kaash_Flowers.png
│   ├── Layer1_Boat_Ghat.png
│   └── Layer2_Crimson_Sunset.png
│
├── BG05_Titas_Night_Storm/                <-- Ep 3: Dramatic tempest, lanterns, meadow
│   ├── Layer0_FG_Swirling_Dust.png
│   ├── Layer1_Lanterns_Meadow.png
│   └── Layer2_Storm_Clouds.png
│
├── BG06_Lob_Babu_Pathshala/               <-- Ep 4: Tin-roof school, slates, paddy window
│   ├── Layer0_FG_Window_Frame.png
│   ├── Layer1_Benches_Slates.png
│   └── Layer2_Paddy_Fields.png
│
├── BG07_Dogachhi_Orchard/                 <-- Ep 4: Mango grove, bamboo fence, dirt lane
│   ├── Layer0_FG_Blossoms.png
│   ├── Layer1_Dirt_Path.png
│   └── Layer2_Distant_Huts.png
│
└── BG08_Sanatan_Master_Pathshala/         <-- Ep 5: Intimate earthen porch, exam day
    ├── Layer0_FG_Pillars.png
    ├── Layer1_Master_Bench.png
    └── Layer2_Village_Green.png
```

---

## 🎨 3. Multiplane Layer Parallax Standard for Blender 2D

Every background is designed at **3840 × 2160 (4K UHD 16:9)** split into 4 depth planes for realistic camera parallax and depth of field:

| Layer ID | Depth Name | Parallax Speed | Blur / Depth of Field | Contents |
| :---: | :--- | :---: | :---: | :--- |
| **Layer 0** | **Foreground Framing** | `1.35x` | Slight Gaussian blur (3–5px) | Overhanging tree branches, foreground leaves, hanging oil lamps, Kash flower stalks. |
| **Layer 1** | **Character Action Plane** | `1.00x` | Sharp / In-Focus (0px) | Main ground, mud veranda, school benches, boat deck, pond edge. Where characters walk and sit. |
| **Layer 2** | **Midground Scenery** | `0.55x` | Subtle atmospheric haze (1–2px) | Neighboring thatched huts, bamboo cluster, garden fence, cattle shed. |
| **Layer 3** | **Distant Background** | `0.20x` | Soft atmospheric perspective | Distant horizon banyan tree line, river bend, paddy field vistas. |
| **Layer 4** | **Sky Matte & Atmosphere** | `0.05x` | Dreamy diffuse glow | Hand-painted watercolor clouds, golden sunbeams (*crepuscular rays*), moon, stars. |

---

## 🌈 4. Official Scenic Color Palette

```
Studio Ghibli Rural Bengal Master Swatches:
* Morning Sunlight Gold:   #FDE6A4  (Luminous sunbeam warmth filtering through foliage)
* Banyan Canopy Moss:      #385739  (Deep rich green with warm olive undertones)
* Earth Veranda Ochre:     #C48D56  (Hand-swept sun-baked alluvial clay)
* River Titas Indigo:      #2A455A  (Cool deep water reflecting twilight clouds)
* Kash Flower Pure White:  #F8F7F2  (Delicate feathered cream-white seed heads)
* Brass Lamp Flame Amber:  #FFA53B  (Warm radiant candlelight and hurricane lantern glow)
* Monsoonal Rain Slate:    #4D5663  (Dramatic storm sky over open floodplain)
```

---

## 📝 5. Production Prompts & Scenic Recipes (For AI Diffusion & Matte Painting)

When executing background generation (via ComfyUI SDXL/Flux ControlNet workflows or digital painting):

### Scene 1: Ancestral Courtyard (Morning Sunlight)
```
Studio Ghibli hand-painted background art by Kazuo Oga, a serene traditional 1920s rural Bengal mud-baked courtyard in Ujanchar, a sacred Tulsi-mancha in the center with a brass water pot, ancestral thatched-roof clay veranda with wooden support posts, sweeping dappled morning sunlight filtering through ancient banyan and mango foliage, soft komorebi sunbeams, idyllic countryside tranquility, rich gouache texture, soft watercolor edges, high aesthetic, 4k master.
--no modern elements, wires, concrete, plastic, cars
```

### Scene 2: Titas Riverbank at Sunset (Kash Flowers & Boat)
```
Studio Ghibli watercolor landscape by Kazuo Oga and Hayao Miyazaki, the banks of the wide River Titas at golden hour sunset, endless fields of fluffy white Kash flowers (Saccharum spontaneum) swaying in a gentle breeze, an old wooden country ferry boat moored at a rustic bamboo ghat, shimmering water surface reflecting vibrant amber, crimson and indigo evening clouds, peaceful Bengali riverine atmosphere, hand-painted anime background, 4k resolution.
--no modern boats, metal poles, engines
```

### Scene 3: River Meadow Lantern Gathering (Night Tempest)
```
Studio Ghibli theatrical anime background, dramatic night scene on an open rural floodplain in Bengal, a swirling gathering of wind and mist under an indigo and charcoal storm sky, warm flickering golden glow from several antique glass hurricane lanterns resting on the grass, delicate trails of white incense smoke curling into the air, mysterious, majestic, spiritual atmosphere, hand-painted cinematic matte, 4k.
--no electric lights, modern lamps, neon
```

### Scene 4: Traditional Village Pathshala (Lob Babu's & Sanatan Master's School)
```
Studio Ghibli interior background art, a cozy rural 1920s village schoolhouse in Bengal, tin bungalow roof with exposed rustic timber rafters, polished mud floor with woven grass sitting mats, weathered wooden teacher's table with handwritten student slates and chalk sticks, wide open windows framing a view of lush vibrant green paddy fields under bright blue sky, nostalgic, heartwarming, hand-painted gouache, 4k master.
--no modern desks, whiteboards, plastic chairs
```

---

## 📅 6. Execution Roadmap for Backgrounds

- [x] **Architecture & Scenic Specifications Complete** (Current Document)
- [ ] **Phase A (Upcoming Day)**: Generate 4K scenic masters for `BG01` (Courtyard), `BG04` (Titas Riverbank), and `BG06` (Pathshala).
- [ ] **Phase B**: Multiplane separation in Photoshop/GIMP into 4 RGBA planes per environment.
- [ ] **Phase C**: Import into Blender 5.3 scene collections with multiplane parallax camera rigs for episodic animation.
