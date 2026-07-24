#!/usr/bin/env python3
"""
Manifest Dependency Optimizer
==============================
Minimizes the `depends` list in an Odoo industry module manifest.

Steps to use the script:
    -Run the Odoo server
    -Install the industry
    -Run this command where script is located

    python3 manifest_cleaning.py \
        --module_path="/path/to/module" \
        --db_name="your_db" \
        --port=9090

"""

import sys
import re
import json
import requests
import argparse
from pathlib import Path
from ast import literal_eval

BASE_URL = "http://localhost:"
PASSWORD = "admin"
LOGIN = "admin"

UNWANTED_DEPENDS = {
    "account_invoice_extract",
    "account_online_synchronization",
    "account_peppol",
    "auth_totp_mail",
    "base_install_request",
    "base_module",
    "__import__",
    "crm_iap_enrich",
    "crm_iap_mine",
    "partner_autocomplete",
    "pos_epson_printer",
    "sale_async_emails",
    "snailmail_account",
    "snailmail_account_followup",
    "web_grid",
    "social_push_notifications",
    "appointment_sms",
    "website_knowledge",
    "base_vat",
    "product_barcodelookup",
    "base_geolocalize",
    "gamification",
    "l10n_be_pos_sale",
    "pos_sms",
    "pos_settle_due",
    "website_partner",
    "website_project",
    "project_sms",
}


def authenticate(db_name, port):
    session = requests.Session()
    resp = session.post(
        f"{BASE_URL}{port}/web/session/authenticate",
        json={
            "jsonrpc": "2.0",
            "method": "call",
            "id": 1,
            "params": {"db": db_name, "login": LOGIN, "password": PASSWORD},
        },
    )
    resp.raise_for_status()
    result = resp.json().get("result", {})
    if not result.get("uid"):
        raise RuntimeError("Authentication failed.")
    return session, result["uid"]


def _rpc(session, port, db_name, uid, model, method, args, kwargs):
    resp = session.post(
        f"{BASE_URL}{port}/jsonrpc",
        json={
            "jsonrpc": "2.0",
            "method": "call",
            "id": 1,
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [db_name, uid, PASSWORD, model, method, args, kwargs],
            },
        },
    )
    resp.raise_for_status()
    return resp.json().get("result", [])


def fetch_module_data(session, db_name, uid, port):
    rows = _rpc(
        session,
        port,
        db_name,
        uid,
        "ir.module.module",
        "search_read",
        [[]],
        {
            "fields": [
                "name",
                "shortdesc",
                "summary",
                "author",
                "state",
                "dependencies_id",
                "auto_install",
                "category_id",
            ]
        },
    )
    auto_install = {r["name"] for r in rows if r.get("auto_install")}

    installed_modules = []
    for r in rows:
        if r.get("state") == "installed":
            cat = r.get("category_id")
            installed_modules.append(
                {
                    "name": r["name"],
                    "shortdesc": r.get("shortdesc") or r["name"],
                    "summary": r.get("summary") or "",
                    "author": r.get("author") or "",
                    "auto_install": bool(r.get("auto_install")),
                    "category": cat[1]
                    if isinstance(cat, (list, tuple)) and len(cat) > 1
                    else "",
                }
            )
    installed_modules.sort(key=lambda x: x["name"])

    all_dep_ids = [d for r in rows for d in r["dependencies_id"]]
    dep_rows = _rpc(
        session,
        port,
        db_name,
        uid,
        "ir.module.module.dependency",
        "read",
        [all_dep_ids],
        {"fields": ["id", "name"]},
    )
    dep_id_to_name = {r["id"]: r["name"] for r in dep_rows}
    graph = {
        r["name"]: {
            dep_id_to_name[d] for d in r["dependencies_id"] if d in dep_id_to_name
        }
        for r in rows
    }
    return graph, auto_install, installed_modules


def build_transitive_cache(graph, seeds):
    cache = {}

    def _trans(mod, visiting=frozenset()):
        if mod in cache:
            return cache[mod]
        if mod in visiting or mod not in graph:
            return set()
        visiting = visiting | {mod}
        result = set(graph[mod])
        for dep in graph[mod]:
            result |= _trans(dep, visiting)
        cache[mod] = result
        return result

    for mod in seeds:
        _trans(mod)
    return cache


def _direct_deps_of_others(module_list, graph, exclude):
    result = set()
    for m in module_list:
        if m != exclude:
            result |= graph.get(m, set())
    return result


def dominator_pass(module_list, graph, label):
    result = []
    for mod in module_list:
        covered_by = [
            other
            for other in module_list
            if other != mod and mod in graph.get(other, set())
        ]
        if not covered_by:
            result.append(mod)
    return result


def auto_install_unwrap_pass(module_list, graph, auto_install, label, pinned=None):
    pinned = pinned or set()
    result = []
    for mod in module_list:
        if mod not in auto_install or mod in pinned:
            result.append(mod)
            continue
        triggers = graph.get(mod, set())
        if not triggers:
            continue
        other_direct = _direct_deps_of_others(module_list, graph, exclude=mod)
        uncovered = triggers - other_direct
        if uncovered:
            result.append(mod)
    return result


# ── HTML export ────────────────────────────────────────────────────────────────
def _build_tree_data(mod, graph, visited, depth):
    is_cycle = mod in visited
    if mod not in graph:
        return {"id": mod, "depth": depth, "cycle": False, "children": []}
    children = sorted(graph.get(mod, set()))
    node = {"id": mod, "depth": depth, "cycle": is_cycle, "children": []}
    if not is_cycle:
        new_visited = visited | {mod}
        for c in children:
            node["children"].append(_build_tree_data(c, graph, new_visited, depth + 1))
    else:
        node["hiddenChildCount"] = len(children)
    return node


def export_html_tree(
    module_name,
    before_depends,
    after_depends,
    graph,
    auto_install,
    installed_modules,
    before_cache,
    after_cache,
    diff_info,
    out_path,
):
    def enrich(depends, cache):
        all_trans = set()
        for m in depends:
            all_trans |= cache.get(m, set())
        all_trans -= set(depends)
        direct_set = set(depends)
        reachable = direct_set | all_trans
        rev = {m: [] for m in reachable}
        for m in reachable:
            for child in graph.get(m, set()):
                if child in reachable:
                    rev.setdefault(child, []).append(m)

        dominated_by = {}
        for mod in depends:
            covers = [
                other
                for other in depends
                if other != mod and mod in graph.get(other, set())
            ]
            if covers:
                dominated_by[mod] = sorted(covers)

        auto_removable = set()
        for mod in depends:
            if mod not in auto_install:
                continue
            triggers = graph.get(mod, set())
            if not triggers:
                auto_removable.add(mod)
                continue
            other_direct = set()
            for other in depends:
                if other != mod:
                    other_direct |= graph.get(other, set())
            if not (triggers - other_direct):
                auto_removable.add(mod)

        meta = {}
        for m in reachable:
            meta[m] = {
                "direct": m in direct_set,
                "auto": m in auto_install,
                "autoRemovable": m in auto_removable,
                "blacklisted": m in UNWANTED_DEPENDS,
                "directDeps": sorted(graph.get(m, set())),
                "reverseDeps": sorted(rev.get(m, [])),
                "depCount": len(graph.get(m, set())),
                "refCount": len(rev.get(m, [])),
            }

        tree_roots = [
            _build_tree_data(d, graph, {module_name}, 0) for d in sorted(depends)
        ]

        return {
            "depends": sorted(depends),
            "directCount": len(depends),
            "transCount": len(all_trans),
            "totalCount": len(depends) + len(all_trans),
            "autoCount": len([m for m in reachable if m in auto_install]),
            "meta": meta,
            "dominatedBy": dominated_by,
            "autoRemovable": sorted(auto_removable),
            "treeRoots": tree_roots,
        }

    before_data = enrich(before_depends, before_cache)
    after_data = enrich(after_depends, after_cache)

    before_set = set(before_depends)
    after_set = set(after_depends)
    annotated_installed = []
    for m in installed_modules:
        m2 = dict(m)
        m2["inBefore"] = m["name"] in before_set
        m2["inAfter"] = m["name"] in after_set
        annotated_installed.append(m2)

    payload = json.dumps(
        {
            "module": module_name,
            "before": before_data,
            "after": after_data,
            "diff": diff_info,
            "blacklist": sorted(UNWANTED_DEPENDS),
            "installedModules": annotated_installed,
        },
        separators=(",", ":"),
    )

    html = (
        r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>"""
        + module_name
        + r""" — Dependency Analyser</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --white:#ffffff;
  --surface:#f8f9fa;
  --surface2:#f1f3f4;
  --surface3:#e8eaed;
  --border:#dadce0;
  --border-subtle:#e8eaed;
  --text:#202124;
  --text-secondary:#5f6368;
  --text-hint:#80868b;
  --blue:#1a73e8;
  --blue-light:#e8f0fe;
  --green:#188038;
  --green-light:#e6f4ea;
  --red:#d93025;
  --red-light:#fce8e6;
  --yellow:#f9ab00;
  --yellow-light:#fef7e0;
  --teal:#137333;
  --teal-light:#e6f4ea;
  --orange:#e37400;
  --orange-light:#fef0cd;
  --purple:#7b1fa2;
  --purple-light:#f3e5f5;
  --shadow-1:0 1px 2px rgba(60,64,67,.3),0 1px 3px 1px rgba(60,64,67,.15);
  --shadow-2:0 1px 2px rgba(60,64,67,.3),0 2px 6px 2px rgba(60,64,67,.15);
}
body{background:var(--surface);color:var(--text);font-family:'Google Sans','Segoe UI',sans-serif;font-size:13px;line-height:1.5;height:100vh;display:flex;flex-direction:column;overflow:hidden}

/* ── Top bar ── */
.topbar{background:var(--white);border-bottom:1px solid var(--border);padding:0 16px;height:56px;display:flex;align-items:center;gap:12px;flex-shrink:0;box-shadow:0 1px 3px rgba(60,64,67,.12)}
.app-icon{width:32px;height:32px;border-radius:8px;background:var(--blue);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.app-icon svg{fill:#fff;width:18px;height:18px}
.module-name{font-size:16px;font-weight:500;color:var(--text);white-space:nowrap;flex-shrink:0}
.module-name span{color:var(--blue);font-weight:700}

/* Tab nav */
.tab-nav{display:flex;gap:0;margin-left:12px;flex-shrink:0}
.tab-btn{padding:8px 20px;border:none;border-bottom:3px solid transparent;background:transparent;color:var(--text-secondary);font-family:'Google Sans',sans-serif;font-size:13px;font-weight:500;cursor:pointer;transition:all .18s;white-space:nowrap}
.tab-btn:hover{color:var(--text);background:var(--surface2)}
.tab-btn.active{color:var(--blue);border-bottom-color:var(--blue)}

/* Segmented control (before/after) */
.seg-wrap{display:flex;background:var(--surface2);border:1px solid var(--border);border-radius:20px;overflow:hidden;flex-shrink:0;margin-left:4px}
.seg-wrap button{padding:5px 16px;border:none;background:transparent;color:var(--text-secondary);font-family:'Google Sans',sans-serif;font-size:12px;font-weight:500;cursor:pointer;transition:all .2s;border-radius:20px}
.seg-wrap button.active{background:var(--blue-light);color:var(--blue);box-shadow:inset 0 0 0 1px var(--blue)}
.seg-wrap button:hover:not(.active){background:var(--surface3);color:var(--text)}

.stats-row{display:flex;gap:8px;margin-left:auto;flex-wrap:wrap;align-items:center}
.stat-chip{display:inline-flex;align-items:center;gap:5px;padding:4px 12px;border-radius:16px;border:1px solid var(--border);background:var(--white);font-size:12px;color:var(--text-secondary);font-family:'Google Sans',sans-serif;font-weight:500}
.stat-chip .val{font-weight:700;font-size:13px}
.stat-chip.blue .val{color:var(--blue)}
.stat-chip.green .val{color:var(--green)}
.stat-chip.gray .val{color:var(--text-secondary)}
.stat-chip.red .val{color:var(--red)}
.stat-chip.teal .val{color:var(--teal)}
.stat-chip.orange .val{color:var(--orange)}
.stat-chip.purple .val{color:var(--purple)}

/* ── Filter bar ── */
.filterbar{background:var(--white);border-bottom:1px solid var(--border);padding:10px 16px;display:flex;align-items:center;gap:10px;flex-shrink:0;flex-wrap:wrap}
.search-wrap{display:flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--border);border-radius:24px;padding:6px 16px;flex:1;min-width:200px;transition:all .2s}
.search-wrap:focus-within{background:var(--white);border-color:var(--blue);box-shadow:0 0 0 2px rgba(26,115,232,.15)}
.search-icon{width:16px;height:16px;flex-shrink:0;opacity:.5}
.search-wrap input{border:none;background:transparent;color:var(--text);font-family:'Google Sans',sans-serif;font-size:13px;outline:none;flex:1}
.search-wrap input::placeholder{color:var(--text-hint)}
#match-count,#inst-match-count{font-size:12px;color:var(--blue);font-weight:500;min-width:64px}
.filter-chips{display:flex;gap:6px;flex-wrap:wrap}
.fchip{padding:5px 14px;border:1px solid var(--border);border-radius:16px;background:var(--white);color:var(--text-secondary);font-family:'Google Sans',sans-serif;font-size:12px;font-weight:500;cursor:pointer;transition:all .18s;display:inline-flex;align-items:center;gap:5px}
.fchip:hover{background:var(--surface2);border-color:var(--text-secondary)}
.fchip.on{background:var(--blue-light);border-color:var(--blue);color:var(--blue)}
.fchip.on::before{content:'✓ ';font-size:11px}
.ctrl-wrap{display:flex;gap:6px;margin-left:auto}
.text-btn{padding:6px 14px;border:none;border-radius:4px;background:transparent;color:var(--blue);font-family:'Google Sans',sans-serif;font-size:13px;font-weight:500;cursor:pointer;transition:background .15s}
.text-btn:hover{background:var(--blue-light)}

/* ── Tab pages ── */
.tab-page{display:none;flex:1;overflow:hidden}
.tab-page.active{display:flex}

/* ── Tree view (deps tab) ── */
.main{display:flex;flex:1;overflow:hidden;width:100%}
.tree-panel{flex:1;overflow-y:auto;overflow-x:auto;padding:16px;min-width:0;background:var(--surface)}
.tree-panel::-webkit-scrollbar{width:8px;height:8px}
.tree-panel::-webkit-scrollbar-thumb{background:var(--surface3);border-radius:4px;border:2px solid var(--surface)}
ul.tree{list-style:none;padding:0}
ul.tree ul{padding-left:24px;border-left:2px solid var(--surface3);margin:2px 0}
ul.tree ul.closed{display:none}
li.tree-item{padding:1px 0}
li.tree-item.hidden{display:none}
.node{display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:20px;cursor:pointer;white-space:nowrap;transition:background .15s,box-shadow .15s;user-select:none;border:1px solid transparent}
.node:hover{background:var(--white);box-shadow:var(--shadow-1)}
.node.selected{background:var(--blue-light);border-color:rgba(26,115,232,.3)}
.node.search-match{background:var(--yellow-light);border-color:rgba(249,171,0,.4)}
.node.search-dim{opacity:.25}
.caret{font-size:10px;width:12px;display:inline-block;transition:transform .15s;color:var(--text-hint);flex-shrink:0}
.node.collapsed .caret{transform:rotate(0deg)}
.node:not(.collapsed) .caret{transform:rotate(90deg)}
.node.no-children .caret{visibility:hidden !important}
.node.direct .nname{color:var(--blue);font-weight:600}
.node.auto .nname{color:var(--teal);font-weight:500}
.node.trans .nname{color:var(--text-secondary)}
.node.blacklisted .nname{color:var(--text-hint);text-decoration:line-through}
.node.selected .nname{color:var(--blue)!important}
.nbadge{font-size:10px;padding:1px 7px;border-radius:10px;font-family:'Google Sans',sans-serif;font-weight:600;flex-shrink:0;letter-spacing:.01em}
.nbadge.direct{background:var(--blue-light);color:var(--blue)}
.nbadge.auto{background:var(--teal-light);color:var(--teal)}
.nbadge.dominated{background:var(--red-light);color:var(--red)}
.nbadge.autoremov{background:var(--orange-light);color:var(--orange)}
.ncount{font-size:11px;color:var(--text-hint);font-family:'Roboto Mono',monospace}

/* ── Detail panel ── */
.detail-panel{width:340px;flex-shrink:0;background:var(--white);border-left:1px solid var(--border);overflow-y:auto;display:flex;flex-direction:column}
.detail-panel::-webkit-scrollbar{width:6px}
.detail-panel::-webkit-scrollbar-thumb{background:var(--surface3);border-radius:3px}
.detail-empty{flex:1;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:10px;padding:24px;text-align:center}
.detail-empty-icon{width:48px;height:48px;border-radius:12px;background:var(--surface2);display:flex;align-items:center;justify-content:center}
.detail-empty-icon svg{width:24px;height:24px;fill:var(--text-hint)}
.detail-empty p{color:var(--text-secondary);font-size:13px;line-height:1.6}
.detail-content{display:flex;flex-direction:column}
.detail-header{padding:16px 20px;border-bottom:1px solid var(--border-subtle);background:var(--white)}
.detail-modname{font-size:14px;font-weight:700;color:var(--text);word-break:break-all;margin-bottom:8px;font-family:'Google Sans',sans-serif}
.detail-badges{display:flex;gap:5px;flex-wrap:wrap}
.dbadge{font-size:11px;padding:3px 10px;border-radius:12px;font-family:'Google Sans',sans-serif;font-weight:600}
.dbadge.direct{background:var(--blue-light);color:var(--blue)}
.dbadge.auto{background:var(--teal-light);color:var(--teal)}
.dbadge.dominated{background:var(--red-light);color:var(--red)}
.dbadge.autoremov{background:var(--orange-light);color:var(--orange)}
.dbadge.blacklisted{background:var(--red-light);color:var(--red)}
.detail-section{padding:14px 20px;border-bottom:1px solid var(--border-subtle)}
.section-label{font-size:11px;font-weight:700;color:var(--text-hint);letter-spacing:.08em;text-transform:uppercase;margin-bottom:10px;font-family:'Google Sans',sans-serif}
.metric-row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.metric-card{background:var(--surface);border:1px solid var(--border-subtle);border-radius:12px;padding:12px;text-align:center}
.metric-val{font-size:22px;font-weight:700;color:var(--blue);font-family:'Google Sans',sans-serif}
.metric-lbl{font-size:11px;color:var(--text-secondary);margin-top:2px}
.alert-card{border-radius:8px;padding:12px 14px;font-size:12px;line-height:1.7}
.alert-card.red{background:var(--red-light);border:1px solid rgba(217,48,37,.2);color:#c5221f}
.alert-card.orange{background:var(--orange-light);border:1px solid rgba(227,116,0,.25);color:#a85400}
.alert-card strong{font-weight:600}
.rule-box{background:var(--surface);border:1px solid var(--border-subtle);border-radius:8px;padding:10px 14px;font-size:12px;color:var(--text-secondary);line-height:1.7}
.chip-list{display:flex;flex-wrap:wrap;gap:5px}
.chip{font-size:11px;padding:3px 10px;border-radius:12px;border:1px solid var(--border);color:var(--text-secondary);cursor:pointer;transition:all .15s;background:var(--white);font-family:'Google Sans',sans-serif}
.chip:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-light)}
.chip.direct{background:var(--blue-light);border-color:rgba(26,115,232,.3);color:var(--blue)}
.chip.auto{background:var(--teal-light);border-color:rgba(19,115,51,.3);color:var(--teal)}

/* ── Installed modules panel ── */
.inst-layout{display:flex;flex:1;overflow:hidden;flex-direction:column}
.inst-toolbar{background:var(--white);border-bottom:1px solid var(--border);padding:10px 16px;display:flex;align-items:center;gap:10px;flex-shrink:0;flex-wrap:wrap}
.inst-grid{flex:1;overflow-y:auto;padding:16px;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px;align-content:start}
.inst-grid::-webkit-scrollbar{width:8px}
.inst-grid::-webkit-scrollbar-thumb{background:var(--surface3);border-radius:4px}
.mod-card{background:var(--white);border:1px solid var(--border);border-radius:12px;padding:14px 16px;cursor:default;transition:box-shadow .15s,border-color .15s;position:relative}
.mod-card:hover{box-shadow:var(--shadow-1);border-color:var(--blue)}
.mod-card.hidden{display:none}
.mod-card.in-before{border-left:3px solid var(--blue)}
.mod-card.in-after{border-left:3px solid var(--green)}
.mod-card.in-both{border-left:3px solid var(--blue)}
.mod-card-name{font-size:12px;font-weight:700;color:var(--text);font-family:'Roboto Mono',monospace;margin-bottom:4px;word-break:break-all}
.mod-card-title{font-size:13px;color:var(--text);margin-bottom:2px;font-weight:500}
.mod-card-cat{font-size:11px;color:var(--text-hint);margin-bottom:6px}
.mod-card-summary{font-size:12px;color:var(--text-secondary);line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.mod-card-badges{display:flex;gap:4px;flex-wrap:wrap;margin-top:8px}
.mod-badge{font-size:10px;padding:2px 8px;border-radius:10px;font-family:'Google Sans',sans-serif;font-weight:600}
.mod-badge.in-before{background:var(--blue-light);color:var(--blue)}
.mod-badge.in-after{background:var(--green-light);color:var(--green)}
.mod-badge.auto{background:var(--teal-light);color:var(--teal)}
.mod-badge.not-in-manifest{background:var(--surface2);color:var(--text-hint)}
.inst-empty{display:none;padding:40px;text-align:center;color:var(--text-secondary);grid-column:1/-1}

/* sort/filter selects */
.inst-select{padding:5px 10px;border:1px solid var(--border);border-radius:8px;background:var(--white);color:var(--text);font-family:'Google Sans',sans-serif;font-size:12px;outline:none;cursor:pointer}
.inst-select:focus{border-color:var(--blue)}

/* ── Status bar ── */
.statusbar{background:var(--white);border-top:1px solid var(--border);padding:7px 20px;display:flex;align-items:center;gap:20px;flex-shrink:0;flex-wrap:wrap}
.leg-item{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--text-secondary)}
.leg-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.leg-dot.direct{background:var(--blue)}
.leg-dot.auto{background:var(--teal)}
.leg-dot.trans{background:var(--surface3);border:1px solid var(--border)}
.leg-dot.dominated{background:var(--red);border-radius:3px}
.leg-dot.autoremov{background:var(--orange);border-radius:3px}
.leg-dot.installed{background:var(--purple);border-radius:3px}
</style>
</head>
<body>

<div class="topbar">
  <div class="app-icon">
    <svg viewBox="0 0 24 24"><path d="M17 12h-5v5h5v-5zM16 1v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-1V1h-2zm3 18H5V8h14v11z"/></svg>
  </div>
  <div class="module-name">Dependency Analyser &nbsp;·&nbsp; <span id="module-title"></span></div>

  <div class="tab-nav">
    <button class="tab-btn active" onclick="switchTab('deps')">Dependencies</button>
    <button class="tab-btn" onclick="switchTab('installed')">Installed Modules</button>
  </div>

  <div class="seg-wrap" id="seg-before-after">
    <button id="btn-before" class="active" onclick="switchMode('before')">Before</button>
    <button id="btn-after"  onclick="switchMode('after')">After optimisation</button>
  </div>

  <div class="stats-row" id="stats-row"></div>
</div>

<!-- ── Deps tab filter bar ── -->
<div class="filterbar" id="deps-filterbar">
  <div class="search-wrap">
    <svg class="search-icon" viewBox="0 0 24 24" fill="currentColor">
      <path d="M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
    </svg>
    <input id="search" type="text" placeholder="Search modules…" oninput="doSearch(this.value)" autocomplete="off" spellcheck="false">
    <span id="match-count"></span>
  </div>
  <div class="filter-chips">
    <span class="fchip" id="f-direct"    onclick="toggleFilter('direct')">Direct only</span>
    <span class="fchip" id="f-auto"      onclick="toggleFilter('auto')">Auto-install</span>
    <span class="fchip" id="f-dominated" onclick="toggleFilter('dominated')">Direct-covered</span>
    <span class="fchip" id="f-autoremov" onclick="toggleFilter('autoremov')">Auto removable</span>
  </div>
  <div class="ctrl-wrap">
    <button class="text-btn" onclick="setAll(true)">Expand all</button>
    <button class="text-btn" onclick="setAll(false)">Collapse all</button>
  </div>
</div>

<!-- ── Installed tab filter bar ── -->
<div class="filterbar" id="inst-filterbar" style="display:none">
  <div class="search-wrap">
    <svg class="search-icon" viewBox="0 0 24 24" fill="currentColor">
      <path d="M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
    </svg>
    <input id="inst-search" type="text" placeholder="Search installed modules…" oninput="doInstSearch(this.value)" autocomplete="off" spellcheck="false">
    <span id="inst-match-count"></span>
  </div>
  <div class="filter-chips">
    <span class="fchip" id="if-in-before"   onclick="toggleInstFilter('in-before')">In manifest (before)</span>
    <span class="fchip" id="if-in-after"    onclick="toggleInstFilter('in-after')">In manifest (after)</span>
    <span class="fchip" id="if-auto"        onclick="toggleInstFilter('auto')">Auto-install</span>
    <span class="fchip" id="if-not-in"      onclick="toggleInstFilter('not-in')">Not in manifest</span>
  </div>
  <div class="ctrl-wrap">
    <select class="inst-select" id="inst-sort" onchange="renderInstalled()">
      <option value="name">Sort: Name A–Z</option>
      <option value="name-desc">Sort: Name Z–A</option>
      <option value="category">Sort: Category</option>
      <option value="in-manifest">Sort: In manifest first</option>
    </select>
  </div>
</div>

<!-- ── DEPS TAB ── -->
<div class="tab-page active" id="tab-deps">
  <div class="main">
    <div class="tree-panel">
      <ul class="tree" id="tree-root"></ul>
    </div>
    <div class="detail-panel" id="detail-panel">
      <div class="detail-empty">
        <div class="detail-empty-icon">
          <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14H7v-2h5v2zm5-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
        </div>
        <p>Click any module<br>to inspect details</p>
      </div>
    </div>
  </div>
</div>

<!-- ── INSTALLED TAB ── -->
<div class="tab-page" id="tab-installed">
  <div class="inst-layout">
    <div class="inst-grid" id="inst-grid">
      <div class="inst-empty" id="inst-empty">No modules match.</div>
    </div>
  </div>
</div>

<div class="statusbar" id="statusbar-deps">
  <div class="leg-item"><div class="leg-dot direct"></div>Direct dependency</div>
  <div class="leg-item"><div class="leg-dot auto"></div>Auto-install</div>
  <div class="leg-item"><div class="leg-dot dominated"></div>Direct-covered (removable)</div>
  <div class="leg-item"><div class="leg-dot autoremov"></div>Auto-install removable</div>
</div>
<div class="statusbar" id="statusbar-inst" style="display:none">
  <div class="leg-item"><div class="leg-dot" style="background:var(--blue);border-radius:3px"></div>In manifest (before)</div>
  <div class="leg-item"><div class="leg-dot" style="background:var(--green);border-radius:3px"></div>In manifest (after)</div>
  <div class="leg-item"><div class="leg-dot auto"></div>Auto-install</div>
  <div class="leg-item" style="margin-left:auto;font-size:12px;color:var(--text-secondary)" id="inst-total-label"></div>
</div>

<script>
const DATA = """
        + payload
        + r""";
let mode='before', activeFilters=new Set(), selectedNode=null, currentTab='deps';
let instActiveFilters=new Set();
function cur(){return DATA[mode]}

/* ── Tab switching ── */
function switchTab(tab){
  currentTab=tab;
  document.querySelectorAll('.tab-btn').forEach((b,i)=>b.classList.toggle('active',['deps','installed'][i]===tab));
  document.querySelectorAll('.tab-page').forEach(p=>p.classList.remove('active'));
  document.getElementById('tab-'+tab).classList.add('active');
  document.getElementById('deps-filterbar').style.display   = tab==='deps'      ? '' : 'none';
  document.getElementById('inst-filterbar').style.display   = tab==='installed' ? '' : 'none';
  document.getElementById('seg-before-after').style.display = tab==='deps'      ? '' : 'none';
  document.getElementById('statusbar-deps').style.display   = tab==='deps'      ? '' : 'none';
  document.getElementById('statusbar-inst').style.display   = tab==='installed' ? '' : 'none';
  if(tab==='installed') renderInstalled();
  else renderStats();
}

/* ── Deps tab helpers ── */
function nodeClass(id){const m=cur().meta[id];if(!m)return 'trans';if(m.direct)return 'direct';if(m.auto)return 'auto';if(m.blacklisted)return 'blacklisted';return 'trans'}
function isDominated(id){return !!(cur().dominatedBy&&cur().dominatedBy[id])}
function isAutoRemovable(id){return cur().autoRemovable&&cur().autoRemovable.includes(id)}

function renderStats(){
  if(currentTab!=='deps') return;
  const c=cur();
  const dominated=Object.keys(c.dominatedBy||{}).length;
  const autoRem=(c.autoRemovable||[]).length;
  document.getElementById('stats-row').innerHTML=
    `<div class="stat-chip blue"><span class="val">${c.directCount}</span> direct</div>`+
    `<div class="stat-chip teal"><span class="val">${c.autoCount}</span> auto-install</div>`+
    `<div class="stat-chip green"><span class="val">${c.totalCount}</span> total</div>`+
    (dominated?`<div class="stat-chip red"><span class="val">${dominated}</span> direct-covered</div>`:'')+
    (autoRem?`<div class="stat-chip orange"><span class="val">${autoRem}</span> auto-removable</div>`:'');
}

function buildNode(nodeData){
  const{id,depth,cycle,children}=nodeData;
  const li=document.createElement('li');
  li.className='tree-item'; li.dataset.id=id;
  const hasChildren=!cycle&&children&&children.length>0;
  const cls=nodeClass(id);
  const dominated=isDominated(id);
  const autoRem=isAutoRemovable(id);
  const span=document.createElement('span');
  span.className='node '+cls+(hasChildren?' collapsed':' no-children');
  span.dataset.id=id;
  const caretEl=document.createElement('span');
  caretEl.className='caret'; caretEl.textContent='▶';
  const nameEl=document.createElement('span');
  nameEl.className='nname'; nameEl.textContent=id;
  span.appendChild(caretEl); span.appendChild(nameEl);
  if(depth===0&&cur().meta[id]?.direct){const b=document.createElement('span');b.className='nbadge direct';b.textContent='direct';span.appendChild(b)}
  if(cur().meta[id]?.auto){const b=document.createElement('span');b.className='nbadge auto';b.textContent='auto';span.appendChild(b)}
  if(dominated&&depth===0){const b=document.createElement('span');b.className='nbadge dominated';b.textContent='direct-covered';span.appendChild(b)}
  if(autoRem&&depth===0&&!dominated){const b=document.createElement('span');b.className='nbadge autoremov';b.textContent='auto-removable';span.appendChild(b)}
  if(hasChildren){const cnt=document.createElement('span');cnt.className='ncount';cnt.textContent=`(${children.length})`;span.appendChild(cnt)}
  li.appendChild(span);
  if(hasChildren){
    const ul=document.createElement('ul');ul.className='tree closed';
    children.forEach(c=>ul.appendChild(buildNode(c)));
    li.appendChild(ul);
    span.onclick=(e)=>{e.stopPropagation();const isClosed=ul.classList.toggle('closed');span.classList.toggle('collapsed',isClosed);handleNodeClick(id,span)};
  } else {
    span.onclick=(e)=>{e.stopPropagation();handleNodeClick(id,span)};
  }
  return li;
}

function renderTree(){const root=document.getElementById('tree-root');root.innerHTML='';cur().treeRoots.forEach(r=>root.appendChild(buildNode(r)))}

function setAll(open){
  document.querySelectorAll('ul.tree ul').forEach(ul=>ul.classList.toggle('closed',!open));
  document.querySelectorAll('.node:not(.no-children)').forEach(n=>n.classList.toggle('collapsed',!open));
}

function switchMode(m){
  mode=m;
  document.getElementById('btn-before').classList.toggle('active',m==='before');
  document.getElementById('btn-after').classList.toggle('active',m==='after');
  activeFilters.clear();
  document.querySelectorAll('.fchip').forEach(b=>b.classList.remove('on'));
  document.getElementById('search').value='';
  document.getElementById('match-count').textContent='';
  renderStats(); renderTree();
  document.getElementById('detail-panel').innerHTML=`<div class="detail-empty"><div class="detail-empty-icon"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14H7v-2h5v2zm5-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg></div><p>Click any module<br>to inspect details</p></div>`;
  selectedNode=null;
}

function doSearch(q){
  q=q.trim().toLowerCase();
  const counter=document.getElementById('match-count');
  if(!q){document.querySelectorAll('.node').forEach(n=>n.classList.remove('search-match','search-dim'));document.querySelectorAll('.tree-item').forEach(li=>li.classList.remove('hidden'));counter.textContent='';return}
  let hits=0;
  document.querySelectorAll('.node').forEach(n=>{const match=(n.dataset.id||'').toLowerCase().includes(q);n.classList.toggle('search-match',match);n.classList.toggle('search-dim',!match);if(match)hits++});
  document.querySelectorAll('.tree-item').forEach(li=>{const hasMatch=li.querySelector('.search-match');li.classList.toggle('hidden',!hasMatch);if(hasMatch){let p=li.parentElement;while(p){if(p.tagName==='UL')p.classList.remove('closed');p=p.parentElement}}});
  counter.textContent=hits?`${hits} result${hits>1?'s':''}`:'No results';
}
document.getElementById('search').addEventListener('keydown',e=>{if(e.key==='Escape'){e.target.value='';doSearch('')}});

function toggleFilter(f){const btn=document.getElementById('f-'+f);if(activeFilters.has(f)){activeFilters.delete(f);btn.classList.remove('on')}else{activeFilters.add(f);btn.classList.add('on')}applyFilters()}
function applyFilters(){
  document.querySelectorAll('.tree-item').forEach(li=>{
    if(!activeFilters.size){li.classList.remove('hidden');return}
    const id=li.dataset.id,m=cur().meta[id]||{};
    let show=true;
    if(activeFilters.has('direct')   &&!m.direct)            show=false;
    if(activeFilters.has('auto')     &&!m.auto)              show=false;
    if(activeFilters.has('dominated')&&!isDominated(id))     show=false;
    if(activeFilters.has('autoremov')&&!isAutoRemovable(id)) show=false;
    li.classList.toggle('hidden',!show);
  });
}

function handleNodeClick(id,spanEl){if(selectedNode)selectedNode.classList.remove('selected');selectedNode=spanEl;spanEl.classList.add('selected');showDetail(id)}

function showDetail(id){
  const m=cur().meta[id];
  const panel=document.getElementById('detail-panel');
  if(!m){panel.innerHTML=`<div class="detail-empty"><div class="detail-empty-icon"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M11 15h2v2h-2zm0-8h2v6h-2zm.99-5C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg></div><p>${id}<br><span style="color:var(--text-hint)">External module</span></p></div>`;return}
  const dominated=cur().dominatedBy?.[id];
  const autoRem=isAutoRemovable(id);
  let html=`<div class="detail-content">`;
  html+=`<div class="detail-header"><div class="detail-modname">${id}</div><div class="detail-badges">`;
  if(m.direct)      html+=`<span class="dbadge direct">Direct dep</span>`;
  if(m.auto)        html+=`<span class="dbadge auto">Auto-install</span>`;
  if(m.blacklisted) html+=`<span class="dbadge blacklisted">Blacklisted</span>`;
  if(dominated)     html+=`<span class="dbadge dominated">Direct-covered</span>`;
  if(autoRem&&!dominated) html+=`<span class="dbadge autoremov">Auto-removable</span>`;
  html+=`</div></div>`;
  html+=`<div class="detail-section"><div class="section-label">Overview</div><div class="metric-row"><div class="metric-card"><div class="metric-val">${m.depCount}</div><div class="metric-lbl">direct deps</div></div><div class="metric-card"><div class="metric-val" style="color:var(--teal)">${m.refCount}</div><div class="metric-lbl">required by</div></div></div></div>`;
  if(dominated&&dominated.length){html+=`<div class="detail-section"><div class="alert-card red"><strong>Direct-covered — safe to remove</strong><br>Appears in direct deps of: ${dominated.map(d=>`<b>${d}</b>`).join(', ')}</div></div>`}
  if(autoRem&&!dominated&&m.auto){html+=`<div class="detail-section"><div class="alert-card orange"><strong>Auto-install — triggers covered</strong><br>All triggers (${m.directDeps.map(t=>`<b>${t}</b>`).join(', ')}) are direct deps of other listed modules.</div></div>`}
  if(!dominated&&!autoRem){html+=`<div class="detail-section"><div class="rule-box">✅ <strong>Not removable</strong><br>Not found in direct deps of any other listed module.${m.auto?' Auto-install triggers not fully covered.':''}</div></div>`}
  if(m.directDeps.length){html+=`<div class="detail-section"><div class="section-label">Requires (${m.directDeps.length})</div><div class="chip-list">${m.directDeps.map(d=>{const dm=cur().meta[d]||{};const cls=dm.direct?'direct':dm.auto?'auto':'';return`<span class="chip ${cls}" onclick="jumpTo('${d}')">${d}</span>`}).join('')}</div></div>`}
  if(m.reverseDeps.length){html+=`<div class="detail-section"><div class="section-label">Required by (${m.reverseDeps.length})</div><div class="chip-list">${m.reverseDeps.map(d=>{const dm=cur().meta[d]||{};const cls=dm.direct?'direct':dm.auto?'auto':'';return`<span class="chip ${cls}" onclick="jumpTo('${d}')">${d}</span>`}).join('')}</div></div>`}
  html+=`</div>`;
  panel.innerHTML=html;
}

function jumpTo(id){const span=document.querySelector(`.node[data-id="${id}"]`);if(span){span.scrollIntoView({behavior:'smooth',block:'center'});span.click()}}

/* ══ Installed Modules tab ══════════════════════════════════════════════════ */

function toggleInstFilter(f){
  const btn=document.getElementById('if-'+f);
  if(instActiveFilters.has(f)){instActiveFilters.delete(f);btn.classList.remove('on')}
  else{instActiveFilters.add(f);btn.classList.add('on')}
  renderInstalled();
}

function doInstSearch(q){renderInstalled()}

function renderInstalled(){
  const q=(document.getElementById('inst-search').value||'').trim().toLowerCase();
  const sortVal=document.getElementById('inst-sort').value;
  let mods=[...DATA.installedModules];

  // sort
  if(sortVal==='name')        mods.sort((a,b)=>a.name.localeCompare(b.name));
  else if(sortVal==='name-desc') mods.sort((a,b)=>b.name.localeCompare(a.name));
  else if(sortVal==='category')  mods.sort((a,b)=>(a.category||'').localeCompare(b.category||'')||a.name.localeCompare(b.name));
  else if(sortVal==='in-manifest') mods.sort((a,b)=>((b.inBefore||b.inAfter)?1:0)-((a.inBefore||a.inAfter)?1:0)||a.name.localeCompare(b.name));

  // filter
  const filters=instActiveFilters;
  if(q||filters.size){
    mods=mods.filter(m=>{
      if(q&&!m.name.toLowerCase().includes(q)&&!(m.shortdesc||'').toLowerCase().includes(q)&&!(m.category||'').toLowerCase().includes(q)) return false;
      if(filters.has('in-before')&&!m.inBefore) return false;
      if(filters.has('in-after') &&!m.inAfter)  return false;
      if(filters.has('auto')     &&!m.auto_install) return false;
      if(filters.has('not-in')   &&(m.inBefore||m.inAfter)) return false;
      return true;
    });
  }

  const grid=document.getElementById('inst-grid');
  // clear old cards (keep empty placeholder)
  Array.from(grid.querySelectorAll('.mod-card')).forEach(c=>c.remove());

  const emptyEl=document.getElementById('inst-empty');
  if(mods.length===0){emptyEl.style.display='block'}
  else {emptyEl.style.display='none'}

  mods.forEach(m=>{
    const card=document.createElement('div');
    let borderCls='';
    if(m.inBefore&&m.inAfter) borderCls='in-both';
    else if(m.inBefore)       borderCls='in-before';
    else if(m.inAfter)        borderCls='in-after';
    card.className=`mod-card ${borderCls}`;

    const badges=[];
    if(m.inBefore) badges.push(`<span class="mod-badge in-before">In manifest (before)</span>`);
    if(m.inAfter)  badges.push(`<span class="mod-badge in-after">In manifest (after)</span>`);
    if(m.auto_install) badges.push(`<span class="mod-badge auto">Auto-install</span>`);
    if(!m.inBefore&&!m.inAfter) badges.push(`<span class="mod-badge not-in-manifest">Not in manifest</span>`);

    card.innerHTML=
      `<div class="mod-card-name">${esc(m.name)}</div>`+
      `<div class="mod-card-title">${esc(m.shortdesc)}</div>`+
      (m.category?`<div class="mod-card-cat">${esc(m.category)}</div>`:'')+
      (m.summary?`<div class="mod-card-summary">${esc(m.summary)}</div>`:'')+
      `<div class="mod-card-badges">${badges.join('')}</div>`;
    grid.appendChild(card);
  });

  // update stat chips for installed tab
  const total=DATA.installedModules.length;
  const inB=DATA.installedModules.filter(m=>m.inBefore).length;
  const inA=DATA.installedModules.filter(m=>m.inAfter).length;
  document.getElementById('stats-row').innerHTML=
    `<div class="stat-chip purple"><span class="val">${total}</span> installed</div>`+
    `<div class="stat-chip blue"><span class="val">${inB}</span> in manifest (before)</div>`+
    `<div class="stat-chip green"><span class="val">${inA}</span> in manifest (after)</div>`;
  document.getElementById('inst-total-label').textContent=`Showing ${mods.length} of ${total} installed modules`;
  document.getElementById('inst-match-count').textContent=q||filters.size?`${mods.length} result${mods.length!==1?'s':''}` : '';
}

function esc(s){return(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}

/* ── Init ── */
document.getElementById('module-title').textContent=DATA.module;
renderStats(); renderTree();
</script>
</body>
</html>"""
    )

    Path(out_path).write_text(html, encoding="utf-8")
    print(f"\n✅ HTML saved → {out_path}")
    print(f"  Open: file://{out_path}\n")


def optimize_manifest(module_path, db_name, port):
    manifest_path = Path(module_path) / "__manifest__.py"
    if not manifest_path.exists():
        print(f"❌ __manifest__.py not found at {manifest_path}{RESET}")
        sys.exit(1)
    manifest = literal_eval(manifest_path.read_text(encoding="utf-8"))
    original_depends = manifest.get("depends", [])
    current = [
        dep
        for dep in original_depends
        if dep not in UNWANTED_DEPENDS and not dep.startswith("theme_")
    ]
    session, uid = authenticate(db_name, port)
    graph, auto_install, installed_modules = fetch_module_data(
        session, db_name, uid, port
    )
    before_depends = list(current)
    before_cache = build_transitive_cache(graph, before_depends)

    MAX_ITER = 20
    for iteration in range(1, MAX_ITER + 1):
        snapshot = set(current)
        # Pass A — direct-dep dominator
        current = dominator_pass(
            current,
            graph,
            label=f"Iter {iteration}·A — Direct-Dep Dominator",
        )
        # Pass B — auto-install trigger check
        current = auto_install_unwrap_pass(
            current,
            graph,
            auto_install,
            label=f"Iter {iteration}·B — Auto-Install Trigger Check",
        )
        if set(current) == snapshot:
            break

    suggested = sorted(set(current))
    after_cache = build_transitive_cache(graph, suggested)

    module_name = Path(module_path).name
    orig_set = set(original_depends)
    sugg_set = set(suggested)
    diff_info = {
        "removed": sorted(orig_set - sugg_set),
        "added": sorted(sugg_set - orig_set),
        "unchanged": sorted(orig_set & sugg_set),
    }
    out = str(Path(module_path) / (module_name + "_deps.html"))
    export_html_tree(
        module_name,
        before_depends,
        suggested,
        graph,
        auto_install,
        installed_modules,
        before_cache,
        after_cache,
        diff_info,
        out,
    )

    if sorted(original_depends) == suggested:
        return

    sys.stdout.flush()
    answer = (
        input("Apply suggested changes to __manifest__.py? (y/N): ").strip().lower()
    )
    if answer != "y":
        return

    raw_text = manifest_path.read_text(encoding="utf-8")
    depends_str = "[\n" + "".join(f"        '{d}',\n" for d in suggested) + "    ]"
    new_text = re.sub(
        r"""(['"]depends['"]\s*:\s*)\[.*?\]""",
        lambda m: m.group(1) + depends_str,
        raw_text,
        flags=re.DOTALL,
    )
    manifest_path.write_text(new_text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Manifest Dependency Optimizer")
    parser.add_argument("--module_path", required=True)
    parser.add_argument("--db_name", required=True)
    parser.add_argument("--port", required=True, type=int)
    args = parser.parse_args()
    optimize_manifest(args.module_path, args.db_name, args.port)


if __name__ == "__main__":
    main()
