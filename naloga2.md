# Identifikacija strank podjetja na spletni strani**

Za uspešno reševanje naloge predpostavljam, da so podatki o strankah/partnerjih prisotni neposredno na spletni strani (brez dodatnega brskanja po domeni).

Cilj je poiskati **splošne značilnosti (feature-je)**, ki se pogosto pojavljajo na spletnih straneh in nam omogočajo zanesljivo detekcijo strank. Predlagam naslednji **postopkovni pristop**:

---

### 1. **Iskanje skupin slik (strukturna ponovljivost)**  
Najprej analiziramo HTML strukturo in iščemo skupine slik (`<img>` tagi), ki so:
- podobnih dimenzij,
- organizirane v mrežo ali zaporedje (znotraj `div`, `section`, `ul`, ipd.),
- pogosto z enakim `class` imenom ali oblikovanjem.

Takšne skupine pogosto predstavljajo logotipe strank.

---

### 2. **Analiza konteksta (okolica slik)**  
Ko najdemo strukturno smiselne skupine slik, analiziramo **besedilo pred in po tej skupini**. Pogosti izrazi so npr.:
- “Trusted by”, “Our customers”, “Clients”, “Join these companies”…

To besedilo lahko **posredujemo LLM modelu**, ki oceni, ali ta sekcija res predstavlja stranke podjetja. Tako se poveže **struktura** s **semantiko**.

---

### 3. **Ekstrakcija imena podjetja**  
Če logotipi vsebujejo `alt` ali `title` atribute ali pa `src` poti, ki vsebujejo imena podjetij (npr. `/logos/google.svg`), lahko iz teh virov neposredno izvlečemo ime stranke.

Če teh podatkov ni, lahko:
- uporabimo LLM za analizo sosednjega besedila in inferenco imena,
- ali uporabimo multimodalni model, ki prepozna logotip na sliki (dobro deluje pri bolj znanih podjetjih).

---

### 4. **Obravnava dinamične vsebine in napredna obdelava slik**  
Če je vsebina generirana preko JavaScript-a in ni vidna v HTML-ju, lahko naredimo **screenshot sekcije** in:

- uporabimo **OCR** za zaznavo besedila,  
- uporabimo **multimodalni model** za prepoznavo logotipov neposredno iz slike,  
- ali pa najprej uporabimo **custom model za detekcijo logotipov**, ki:
  - razbije skupinsko sliko v posamezne logotipe (npr. z object detection modelom, kot je YOLO ali podobni),
  - nato pa vsak izrezan logotip posebej analiziramo z LLM/multimodalnim modelom za prepoznavo podjetja.

Ta pristop omogoča večjo fleksibilnost in deluje tudi v primerih, ko ni dostopa do posameznih slik prek HTML-ja.
---
