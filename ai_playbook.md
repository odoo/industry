# Playbook: merge a `website_custom_XXX` export into an industry module

Give this file to an AI agent along with:
- **Source folder**: the raw export module (e.g. `website_custom_vete/`)
- **Target folder**: the existing industry module to merge it into (e.g.
  `veterinary_clinic/`)

The agent should execute the steps below **in order**, verifying each one
before moving to the next. Do not skip verification steps — every failure
mode described here fails **silently** (no error, no crash, just missing or
wrong data), so the only way to catch problems is to check actual state, not
absence of errors.

## Step 0 — Inventory

List both folders and identify the source module's name (from its
`__manifest__.py` folder name) and the target module's name.

```bash
find <source>/ -type f | sort
find <target>/ -type f | sort
```

The export now produces **three** kinds of file, not two:
- `demo/website/` — site content: pages, menu, assets, images, server_actions,
  the `website` record itself.
- `data/product_*.xml` — the product catalog (`product_template.xml` and its
  config: categories, attributes, tags, attribute lines).
- `data/<business>.xml` — **records from apps that merely surface on the site**
  (new, see Step 3bis): `event_event.xml` (+ `event_event_ticket.xml`),
  `appointment_type.xml` (+ `appointment_slot.xml`, `appointment_resource.xml`),
  `loyalty_program.xml` (+ `loyalty_rule.xml`, `loyalty_reward.xml`),
  `product_pricing.xml` (rentals), `blog_*.xml`, `slide_channel.xml`,
  `forum_forum.xml`, and `ir_attachment_business.xml` (cover images for the
  above). The export puts all of these in `data/`, but most are **sample
  business records that belong in the target's `demo/` list** — Step 3bis
  decides. Never leave them in `data/` by reflex just because that's where the
  export put them.

All three kinds get merged; they go into the target's `data` or `demo` manifest
list depending on Steps 3/3bis — never mix them up.

## Step 1 — Copy files into the target module

Copy files that don't already exist in the target. If a file with the same
purpose already exists in the target (e.g. both have `data/product_template.xml`),
merge their contents manually — don't blindly overwrite.

```bash
cp -rn <source>/demo/website <target>/demo/
cp -n <source>/data/*.xml <target>/data/
cp -rn <source>/static/src/* <target>/static/src/
```

## Step 2 — Rename every reference to the source module name

The exported folder's name (e.g. `website_custom_vete`) appears everywhere
inside its own files: external IDs, `file=` attributes, view `key` fields,
image URLs embedded in page HTML. Rename all of it to the target module name,
inside the files you just copied:

```bash
grep -rl "<source_name>" <target>/demo/website <target>/data | xargs sed -i '' 's/<source_name>/<target_name>/g'
```

Then verify nothing is left:

```bash
grep -rn "<source_name>" <target>/
```

If this returns anything, do not proceed — fix it first. Pay special
attention to patterns `sed` can miss if written unusually:
- `ref('<source_name>.xxx')`
- `file="<source_name>/static/..."`
- `<field name="key"><source_name>.page_home</field>`
- `<img src="/web/image/<source_name>.xxx">` inside page HTML bodies

## Step 3 — Update `<target>/__manifest__.py`

1. Add every copied file to `data` (persistent) or `demo` (only loaded with
   demo data) — whichever list matches where you put it. A file present on
   disk but missing from the manifest is silently never loaded.
2. **Delete old website-creation files the new `demo/website/` folder
   replaces.** A target module that already had a website before this merge
   often has legacy top-level files like `demo/website.xml`,
   `demo/website_view.xml`, `demo/website_theme_apply.xml` — these predate the
   `demo/website/` folder structure the export brings in (which has its own
   `website.xml`, `pages/`, `menu.xml`, etc. doing the same job in a more
   granular way). Find them first:
   ```bash
   ls <target>/demo/website*.xml 2>/dev/null
   grep -n "'demo/website" <target>/__manifest__.py
   ```
   Delete the old files from disk **and** remove their entries from the
   manifest's `demo` list. Leaving them in place means the website gets built
   twice (old flat files + new `demo/website/` folder), which causes
   duplicate/conflicting records (menus, pages, the `website` record itself)
   depending on load order — the same class of bug as Step 6's menu
   duplicates, but for the whole site structure.
3. Remove any other manifest entries pointing to files that don't exist
   anymore (typo'd paths, renamed files).
4. Order the `demo` list so that dependencies load first:
   1. `demo/website/website.xml` (creates the `website` record) — must be
      first, since everything else references it via `ref('module.website_industry')`.
   2. `demo/website/views/*.xml` — the header/footer COW views, before
      `server_actions.xml`: that action activates views with
      `write({'active': True})` under a `website_id` context, and if our
      website-specific view doesn't exist yet Odoo's COW forks a copy of the
      *generic* view instead of touching ours.
   3. `demo/website/pages/*.xml`, `demo/website/menu.xml`,
      `demo/website/assets.xml`, `demo/website/images.xml` — any order among
      themselves is fine.
   4. `demo/website/server_actions.xml` — **last**. The export emits a single
      file holding every one-shot `ir.actions.server` (view
      activation/deactivation *and* the dynamic snippet filter id fix-up), and
      the fix-up rewrites the arch of the views the page files create: loaded
      before them it finds nothing to fix and the dynamic snippets stay broken.
      Running the deactivation part after the pages is safe — Odoo's COW
      `write()` finds the view to touch **by key**, and our page views use key
      `<module>.page_<id>`, never `website.homepage`, so it can only ever hit a
      fresh copy of the generic view. If you are merging an **older** export
      that still ships two files (`server_actions.xml` +
      `server_actions_dynamic_filters.xml`), keep the filter one after the
      pages; you can concatenate both into one file since they are plain
      `<odoo>` documents.
   5. Any `product_template_attribute_line.xml` (sets `value_ids`) must load
      before any file referencing the resulting attribute values.

## Step 3bis — Business-app data (events, appointments, loyalty, rentals, …)

The export emits, under `data/`, records from apps that surface on the site
(see Step 0). These need different handling from the product catalog:

1. **Relocate sample records to `demo/`.** In industry modules, sample business
   records — events, appointment types/slots/resources, loyalty
   programs/rules/rewards, calendar events — live in the `demo` list, not
   `data`. Move each such file from `data/` to `demo/` on disk **and** put its
   manifest entry in the `demo` list. What stays in `data/`: the product
   *catalog* (`product_template.xml` & config) and rental *pricing*
   (`product_pricing.xml`, which refs `product_template` xmlids loaded from
   `data/`). When unsure, check where the target module already keeps that
   model (e.g. `ls <target>/demo/event_event.xml`).
2. **Merge, don't overwrite.** If the target already ships a file of the same
   purpose (often `demo/event_event.xml`, `demo/loyalty_program.xml`, …), fold
   the exported records into the existing file and keep xmlids unique — don't
   replace the file wholesale (you'd drop the records the module already had).
3. **Events: convert absolute dates to relative.** The export writes the real
   `date_begin`/`date_end` (a faithful snapshot). For demo events to stay
   *upcoming* over time, rewrite them as `relativedelta`-based evals matching
   the target's existing events, e.g.:
   ```xml
   <field name="date_begin" model="res.users" eval="
       pytz.timezone(obj().env.user.tz or 'UTC').localize(
           datetime.now().replace(hour=15, minute=30, second=0) + relativedelta(weeks=4, weekday=1)
       ).astimezone(pytz.UTC).replace(tzinfo=None)"/>
   ```
   Add `context="{'mail_auto_subscribe_no_notify': True}"` on the `<odoo>` root
   as the existing demo files do, to avoid notification noise on import.
4. **Cover images: merge `ir_attachment_business.xml`.** Fold its
   `ir.attachment` records into the target's existing attachment data file
   (e.g. `data/ir_attachment_pre.xml`) so every attachment loads *before* the
   record whose `cover_properties` references it. Keep the binaries under
   `static/src/binary/ir_attachment/`. The cover URL in each event
   (`/web/image/<module>.ir_attachment_<id>`) is already renamed by Step 2.
5. **Load order within `demo`/`data`:** attachment file first; then parent
   before child (`event_event` before `event_event_ticket`, `appointment_type`
   before `appointment_slot`, `loyalty_program` before its rules/rewards);
   `product_pricing.xml` after `product_template.xml`.
6. **Fidelity caveats to flag to the user.** The export deliberately omits
   non-portable refs: appointment `staff_user_ids` (`res.users`) and event
   `address_id`/venue (`res.partner`) are not exported. If the site needs them,
   add them by hand. Also, any placeholder text left in the builder DB (generic
   event descriptions, etc.) is exported verbatim — fix it in the builder, not
   here.

## Step 4 — Check for fields from modules you don't depend on

An export taken from an instance with more modules installed can contain
fields your target module can't use. Search the copied files for fields you
don't recognize and confirm which module defines them:

```bash
grep -rn "field name=" <target>/data <target>/demo | sort -u -t'"' -k2,2
```

For each unfamiliar field name, check:

```bash
grep -rn "<field_name> = fields\." core/addons/*/models/*.py core/addons/*/*/models/*.py enterprise/*/models/*.py 2>/dev/null
```

If the defining module isn't in `<target>/__manifest__.py`'s `depends`, either
add the dependency or delete the field from the XML — don't guess, check.

## Step 5 — Never duplicate `product.template.attribute.value`

If any `product_template_attribute_line.xml` sets `value_ids` with
`eval="[(6, 0, [ref(...)])]"`, Odoo auto-creates the matching
`product.template.attribute.value` rows. If the source also ships a
`product_template_attribute_value.xml` explicitly creating the same
combinations with XML IDs, **delete that file** and remove it from the
manifest — it will hit `duplicate key value violates unique constraint`.

If another file references one of those XML IDs (e.g. in a sale order line),
replace the broken `ref()` with a `search=` lookup:

```xml
<field name="product_no_variant_attribute_value_ids"
       model="product.template.attribute.value"
       search="[('attribute_line_id', '=', ref('<target>.line_id')),
                ('product_attribute_value_id', '=', ref('<target>.value_id'))]"/>
```

## Step 6 — Check for menu duplicates

Some dependency modules auto-create top-level website menus on every new
website (e.g. `website` core creates Home/Contact Us, `website_appointment`
creates an Appointment menu copied onto every new site). Before keeping a
`<record model="website.menu">` in the copied `menu.xml`, check whether a
dependency already creates a menu with that same name/URL:

```bash
grep -rln "model=\"website.menu\"" core/addons/*/data/*.xml enterprise/*/data/*.xml 2>/dev/null | xargs grep -l "<field name=\"url\">/appointment</field>\|<field name=\"url\">/contactus</field>" 2>/dev/null
```

If a dependency already provides it, delete the duplicate from the module's
`menu.xml`.
