<div align="center">
  <img src=".github/icon.svg" alt="Logo" height="80">
  <h3>Trojsten ID</h3>
  <p>Identity Provider pre služby Trojstenu.</p>
</div>

## O projekte

Trojsten ID vznikol ako náhrada predchádzajúceho `login.trojsten.sk` riešenia. Jeho snahou je vytvoriť jednotný
prihlasovací systém pre všetky Trojsten stránky a služby. Taktiež poskytuje informácie o používateľoch a
verejné profily.

## Inštalácia a quick-start

Na rozbehanie vývojového prostredia potrebuješ Docker. Na formátovanie kódu používame `pre-commit` hooky, ktoré je vhodné
si nainštalovať.

```bash
uv sync --dev
uv run pre-commit install
```

Development server si vieš spustiť nasledovným príkazom. Trojsten ID by sa ti mal zjaviť na http://localhost:8000.
Niekedy je potrebné rebuildnúť image (napr. pri zmenách Python dependencies), vtedy treba použiť prepínač `--build`.

```bash
docker-compose up
```

Ak potrebuješ používať príkazy v kontajneri, napr. `manage.py`, vieš to spraviť takto:

```bash
docker-compose run --rm web python manage.py ...
```
