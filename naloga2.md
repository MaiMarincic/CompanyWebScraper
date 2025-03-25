# Identifikacija strank podjetja na spletni strani

Za uspešno reševanje naloge predpostavljam, da so podatki o strankah/partnerjih prisotni neposredno na spletni strani (brez dodatnega brskanja po domeni).

Predlagam naslednji **postopkovni pristop**:

---

### 1. **Iskanje skupin slik (strukturna ponovljivost)**  
Najprej analiziramo HTML strukturo in iščemo skupine slik (`<img>` tagi), ki so:
- podobnih dimenzij,
- organizirane v mrežo ali zaporedje (znotraj `div`, `section`, `ul`, ipd.),
- pogosto z enakim `class` imenom ali oblikovanjem.

Takšne skupine pogosto predstavljajo logotipe strank.

---

### 2. **Analiza konteksta (okolica slik)**  
Ko najdemo strukturno smiselne skupine slik, analiziramo **besedilo pred in po tej skupini**. Pogosti izrazi so na primer:
- “Trusted by”, “Our customers”, “Clients”, “Join these companies”…

To besedilo lahko **posredujemo LLM modelu**, ki oceni, ali ta sekcija res predstavlja stranke podjetja. Tako se poveže **struktura** s **semantiko**.

---

### 3. **Ekstrakcija imena podjetja**  
Če logotipi vsebujejo `alt` ali `title` atribute ali pa `src` poti, ki vključujejo imena podjetij (npr. `/logos/google.svg`), lahko iz teh virov neposredno izvlečemo ime stranke.

Če teh podatkov ni, lahko:
- uporabimo LLM za analizo sosednjega besedila in ugotavljanje imena,
- ali uporabimo multimodalni model, ki prepozna logotip na sliki (dobro deluje pri bolj znanih podjetjih).

Če podatkov ne uspemo pridobiti na noben način, lahko predpostavimo, da gre za **false positive** pri detekciji strukture.  
Ker je lahko takih primerov več na eni strani, je smiselno definirati **kriterij zaupanja**, ki oceni, katere skupine so najbolj verjetno relevantne,  
in jih obdelujemo po tej prioriteti. Ko naletimo na primer, kjer uspešno izvlečemo podatke, lahko postopek zaključimo.

---

### 4. **Obravnava dinamične vsebine in napredna obdelava slik**  
Če je vsebina generirana preko JavaScript-a in ni vidna v HTML-ju, lahko naredimo **screenshot sekcije** in:

- uporabimo **OCR** za zaznavo besedila,  
- uporabimo **multimodalni model** za prepoznavo logotipov neposredno iz slike,  
- ali pa najprej uporabimo **custom model za detekcijo logotipov**, ki:
  - razbije skupinsko sliko v posamezne logotipe (npr. z object detection modelom, kot je YOLO ali podoben),
  - nato vsak izrezan logotip ločeno analiziramo z LLM, OCR ali multimodalnim modelom za prepoznavo podjetja.

Ta pristop omogoča večjo fleksibilnost in deluje tudi v primerih, ko ni dostopa do posameznih slik prek HTML-ja.
