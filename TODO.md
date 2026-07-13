## Step 1 — Datový model

Cíl: přepsat `DeploymentConfig` z ploché struktury na vnořenou. Přemýšlej o tom jako o čtyřech vnořených objektech uvnitř jednoho.

Sekce a co nesou (typy si urči sám):

- `networkConnection`: název (text), podsíť (text), portSecurity (bool), internet (bool)
- `virtualMachine`: název (text), obraz/os (text — hodnota z options), cpu (číslo/text z options), ram (totéž), disk (totéž)
- `networks`: lan (bool), lanIp (text), ipConfig (union `'dhcp' | 'static'`), staticIp (text)
- `guacamole`: enabled (bool), os (text), typ (text), keyboardLayout (text), username (text), password (text), sftp (bool)

Rozhodnutí tady: **co z toho potřebuje nést i `Job`**, aby šlo něco ukázat v přehledu bez otevírání detailu. Minimálně os, IP, cpu/ram/disk a identifikátor hypervisoru. Doporučení: nech to celé v `config` a v přehledu čti z `job.config.virtualMachine.os` — jeden zdroj pravdy, žádná duplikace.

Pozor: union typ (`'dhcp' | 'static'`) pohlídá překlepy — TypeScript nedovolí poslat neplatnou hodnotu.

---

## Step 2 — Options service na backendu

Cíl: endpoint `GET /api/options`, který vrátí jeden objekt se všemi seznamy pro dropdowny.

Tvar odpovědi (přibližně): objekt s klíči `operatingSystems`, `cpuOptions`, `ramOptions`, `diskOptions`, `environmentTypes`, `keyboardLayouts`, každý je pole. Použij pole objektů `{ value, label }` — `value` pošleš na backend, `label` ukážeš uživateli (např. value `ubuntu-22.04`, label `Ubuntu 22.04 LTS`).

Za endpointem uděláš rozhraní `OptionsRepository` (abstract base class / Protocol) s metodou `get_options()`. Statická implementace vrátí natvrdo daná data. Později DB implementace proti lab databázi + výměna instance — stejný princip jako `JobRepository`.

Pozor: drž strukturu options konzistentní s typy z kroku 1. Když options mají `value: 'ubuntu-22.04'`, sedí to do `virtualMachine.os`.

---

## Step 3 — Hook pro options

Cíl: hook `useOptions` postavený na `useQuery`, který options načte jednou při mountu a dá je formuláři.

`queryKey` třeba `['options']`, `queryFn` fetchne `/api/options`. Options se během session nemění → žádný polling. Nastav `staleTime` vysoko (nebo `Infinity`), ať se to znovu netahá.

Hook vrátí `{ options, isLoading, isError }`. Formulář podle `isLoading` ukáže spinner místo dropdownů, dokud data nedorazí.

Pozor: než options dorazí, dropdowny nemají co zobrazit. Ošetři tenhle stav, jinak komponenta spadne na `undefined.map()`.

---

## Step 4 — Komponenta Toggle

Cíl: znovupoužitelný přepínač (ten „vypínač"). Použití: internet, LAN, guacamole, SFTP.

Props: `checked` (bool), `onChange` (callback s novou hodnotou), `label` (text). Uvnitř `<input type="checkbox">` ostylovaný přes CSS do podoby přepínače, nebo `<button>` s rolí.

Koncept (už znáš): **controlled komponenta** — Toggle si nedrží vlastní stav, jen zobrazuje `checked` z props a při kliknutí zavolá `onChange`. Rozhodnutí o hodnotě dělá rodič. Proto jde použít všude.

Pozor: `onChange` má předat novou hodnotu (`!checked`), aby rodič nemusel logiku řešit sám.

---

## Step 5 — Komponenta Select

Cíl: znovupoužitelný dropdown. Použití: OS, CPU, RAM, DISK, typ, rozložení kláves, DHCP/statická.

Props: `value` (vybraná hodnota), `onChange` (callback s novou hodnotou), `options` (pole `{ value, label }`), volitelně `label` a `placeholder`. Uvnitř `<select>` s `<option>` promapovanými z `options` přes `.map()` (stejný pattern jako rizika v `AwaitingConfirmation`).

Pozor: `<select>` v Reactu je controlled — `value` řídí vybrané, `onChange` čte `e.target.value`. Bez `value` React hlásí „uncontrolled to controlled" warning.

---

## Step 6 — Architektura stavu formuláře [NOVÝ KONCEPT]

Zastavíme se dřív, než začneš psát. Cca 20+ polí ve čtyřech sekcích. Dvě cesty:

- **Jeden objektový `useState`** — celý config jako jeden objekt, měníš immutably (`setConfig(prev => ({ ...prev, networks: { ...prev.networks, lan: true } }))`). Jednodušší na pochopení, ale spreading do hloubky je ukecaný.
- **`useReducer`** — všechny změny do jedné funkce (reduceru), komponenty posílají „akce". Čistší pro velký stav, ale nový koncept a víc boilerplate na začátku.

Rozhodnutí necháme na moment, až sem dojdeš — projdeme oba na tvém configu a vybereš. Tenhle krok je rozcestník, ne mechanická práce.

Pozor předem: ať zvolíš cokoli, **stav bude žít v jedné rodičovské komponentě** (formulář), sekce ho dostanou přes props. Sekce samy stav nedrží.

---

## Step 7 — Sekce Síťové připojení

Cíl: první sekční komponenta. Název + podsíť jsou textové inputy, port security a internet jsou Toggle (krok 4).

Props: dostane svůj kus configu (`networkConnection`) a callback, kterým hlásí změny nahoru. Tvar callbacku závisí na rozhodnutí z kroku 6 (objektový state → `onChange(updatedSection)`, reducer → dispatch akce).

Nejjednodušší sekce — schválně první, ať si ověříš napojení na stav.

---

## Step 8 — Sekce Virtuální stroje

Cíl: název (text) + čtyři Selecty (OS, CPU, RAM, DISK), plněné z options (krok 3).

Každý Select dostane příslušné pole z options (`options.operatingSystems` atd.) a aktuální hodnotu z configu. Sekce závisí na tom, že options už jsou načtené — pokud renderuješ dřív, ošetři prázdné pole options (Select ukáže jen placeholder).

---

## Step 9 — Sekce Sítě [NOVÝ KONCEPT: podmíněné zobrazení]

Cíl: LAN Toggle + navázané prvky, které se objeví jen za podmínek.

Logika:
- LAN IP (v závorce u názvu) se zobrazí **jen když** `lan === true`
- IP konfigurace: Select nebo dva radio buttony DHCP/Statická
- Pole statické IP se zobrazí **jen když** `ipConfig === 'static'`

Nový pattern: **podmíněný rendering** — v JSX přes `{podmínka && <Komponenta />}`. Když je podmínka false, nevykreslí se nic. Vysvětlím detailně (snadno se rozbije, např. `0 && ...` vykreslí nulu).

Pozor na stav: když uživatel vypne LAN, co s IP, kterou předtím zadal? Rozhodni, jestli ji čistíš, nebo necháš (ovlivní validaci v kroku 11).

---

## Step 10 — Sekce Guacamole [rozšíření podmíněného zobrazení]

Cíl: Toggle `enabled`, a když zapnutý, zobrazí se skupina: OS (Select), typ/GUI (Select), rozložení kláves (Select), uživatelské jméno (text), heslo (password), SFTP (Toggle).

Krok 9 aplikovaný na celou skupinu naráz — blok obalíš do `{guacamole.enabled && ( ... )}`.

Pozor: heslo jako `<input type="password">`. A protože se to generuje do deployment artefaktu, promysli (pro budoucí backend), jestli heslo v plaintextu chceš posílat a ukládat — teď nech být, ale poznámka na později.

---

## Step 11 — Validace napříč poli

Cíl: jedna validační funkce volaná před odesláním. Vrací seznam chyb (nebo prázdný).

Pravidla jsou závislá na volbách — nejde řešit jen přes HTML `required`:
- statická IP povinná **jen když** `ipConfig === 'static'`
- guacamole pole (jméno, heslo…) povinná **jen když** `guacamole.enabled`
- LAN IP povinná **jen když** `lan`
- formát IP adresy (základní regex), pokud je zadaná

Návrh: funkce projde config, sesbírá chyby do pole textů, formulář je zobrazí (nebo blokuje submit, dokud pole není prázdné).

Pozor: vrátí se rozhodnutí z kroků 9–10 — pokud jsi při vypnutí sekce data nevyčistil, musíš je ve validaci ignorovat, ať neblokuješ submit kvůli poli ve vypnuté sekci.

---

## Step 12 — Odeslání

Cíl: sestavit payload z celého configu, poslat na `POST /api/deployments`, ošetřit odpověď.

Config už máš jako jeden objekt (krok 6), payload je v podstatě on. `fetch` s `method: POST`, `Content-Type: application/json`, `body: JSON.stringify(config)`. Zkontroluj `res.ok` (backend může vrátit 422 z validace nebo 503 z limitu) — jinak spadneš do sledování neexistujícího jobu (viz dřívější audit).

Pozor: čistě frontend → backend přenos JSONu. Žádný YAML se tu negeneruje.

---

## Step 13 — Přehled deploymentů (rozšíření)

Cíl: předělat seznam tak, aby ukazoval bohatší info a uměl VM seskupit pod hypervisor.

Čteš z `job.config.virtualMachine` (os, cpu, ram, disk) a z outputů (IP). Seskupení pod hypervisor: až budeš mít v modelu identifikátor hypervisoru, seskupíš joby podle něj (`Object.groupBy` nebo ruční redukce do mapy) a vyrenderuješ jako sekce.

Pozor: vychází přímo z kroku 1 — pokud je model navržen dobře, je tenhle krok jen o zobrazení. Pokud ne, vrátíš se sem model dolaďovat.

---

## Step 14 — Backend: Pydantic modely

Cíl: doplnit Pydantic modely odpovídající vnořené struktuře z kroku 1, s rozšířenou validací (allowlist, délky, formát IP).

Pydantic vnořenou strukturu zvaliduje sám, když modely poskládáš do sebe (model VM uvnitř modelu configu atd.). Sem patří i místo, kde se později z configu generuje Terraform/HCL pro Hyper-V — samotné generování odkládáš (chceš to za ~2 roky, teď jen připravíš tvar).

Pozor: backend validace musí být přísnější než frontend — frontend jde obejít, backend je poslední obrana. Nespoléhej, že co projde frontendem, je čisté.

---

## Nové koncepty (teorie → píšeš sám)

- Step 6 — architektura stavu formuláře (objektový useState vs. useReducer)
- Step 9 — podmíněné zobrazení
- Step 10 — podmíněné zobrazení skupiny polí

Zbytek staví na tom, co už umíš.