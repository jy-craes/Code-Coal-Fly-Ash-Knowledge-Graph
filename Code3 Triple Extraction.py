# -*- coding: utf-8 -*-
"""Re-run the original candidate-triple extraction rules from notebook cell 44.
This script does not apply the later V2/V3 author-review corrections.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,csv,re,json
import pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument('--corpus',default=str(Path(__file__).resolve().parent/'inputs'/'Author Frozen Corpus 3075.csv'))
ap.add_argument('--out',default=str(Path(__file__).resolve().parent/'outputs'/'Code3 Initial Candidate Triples.csv'))
args=ap.parse_args()

TERM_TRANSLATIONS = json.loads(r'''{"\u7c89\u7164\u7070":"Coal fly ash","\u5236\u5907":"produces","\u7528\u4e8e":"is used for","\u8bc4\u4ef7":"is evaluated by","\u53bb\u9664":"removes","\u56de\u6536":"recovers","\u534f\u540c":"co-processes","\u5173\u8054":"is associated with","\u5305\u542b":"includes","\u5438\u9644\u6750\u6599":"Adsorbents","\u6cb8\u77f3/\u5206\u5b50\u7b5b":"Zeolites/molecular sieves","\u5e9f\u6c34\u5904\u7406\u6750\u6599":"Wastewater-treatment materials","\u6c34\u6ce5/\u6df7\u51dd\u571f/\u7802\u6d46":"Cement/concrete/mortar","\u5730\u805a\u7269\u6750\u6599":"Geopolymer materials","\u78b1\u6fc0\u53d1\u6750\u6599":"Alkali-activated materials","\u9676\u74f7/\u73bb\u7483\u9676\u74f7":"Ceramics/glass-ceramics","\u7a00\u571f/\u5173\u952e\u5143\u7d20\u56de\u6536":"Rare-earth/critical-element recovery","\u94dd/\u6c27\u5316\u94dd\u63d0\u53d6":"Aluminum/alumina extraction","\u91d1\u5c5e\u56de\u6536":"Metal recovery","\u78b3\u6750\u6599":"Carbon materials","\u78b3\u6355\u96c6/\u77ff\u5316\u5c01\u5b58":"Carbon capture/mineral carbonation","\u571f\u58e4\u6539\u826f/\u7a33\u5b9a\u5316":"Soil amendment/stabilization","\u9aa8\u6599/\u8def\u57fa/\u9053\u8def\u6750\u6599":"Aggregates/road-base materials","\u7816/\u70e7\u7ed3\u5236\u54c1":"Bricks/sintered products","\u50ac\u5316/\u5149\u50ac\u5316\u6750\u6599":"Catalytic/photocatalytic materials","\u529f\u80fd\u586b\u6599/\u590d\u5408\u6750\u6599":"Functional fillers/composites","\u7a7a\u5fc3\u5fae\u73e0":"Cenospheres","\u672a\u71c3\u78b3\u56de\u6536/\u6d6e\u9009":"Unburned-carbon recovery/flotation","\u591a\u56fa\u5e9f\u534f\u540c":"Multi-solid-waste co-utilization","\u5e9f\u6c34\u5904\u7406":"Wastewater treatment","\u91cd\u91d1\u5c5e\u53bb\u9664":"Heavy-metal removal","\u67d3\u6599\u5438\u9644":"Dye adsorption","\u5efa\u7b51\u6750\u6599":"Building materials","\u9053\u8def\u5de5\u7a0b":"Road engineering","\u751f\u6001\u4fee\u590d":"Ecological restoration","CO2\u51cf\u6392":"CO2 mitigation","\u8d44\u6e90\u56de\u6536":"Resource recovery","\u5438\u9644\u5bb9\u91cf":"Adsorption capacity","\u53bb\u9664\u7387":"Removal efficiency","\u6297\u538b\u5f3a\u5ea6":"Compressive strength","\u6d78\u51fa\u6bd2\u6027":"Leaching toxicity","\u56de\u6536\u7387":"Recovery rate","\u78b3\u6392\u653e":"Carbon emissions","\u80fd\u8017":"Energy consumption","\u7269\u8017":"Material consumption","\u7ecf\u6d4e\u6027":"Economic performance","\u7a33\u5b9a\u6027":"Stability","SiO2/Al2O3":"SiO2/Al2O3","CaO":"CaO","Fe2O3":"Fe2O3","\u672a\u71c3\u78b3":"Unburned carbon","\u91cd\u91d1\u5c5e\u6d78\u51fa\u98ce\u9669":"Heavy-metal leaching risk","\u7c92\u5f84/\u7ec6\u5ea6":"Particle size/fineness","\u77ff\u7269\u76f8":"Mineral phases","\u78b1\u5ea6":"Alkalinity","\u77ff\u6e23":"Slag","\u94a2\u6e23":"Steel slag","\u8d64\u6ce5":"Red mud","\u8131\u786b\u77f3\u818f":"Desulfurization gypsum","\u6c61\u6ce5":"Sludge","\u6c34\u6ce5\u7a91\u7070":"Cement kiln dust","\u5c3e\u77ff":"Tailings","\u751f\u7269\u8d28\u7070":"Biomass ash","\u6280\u672f\u8def\u5f84":"Valorization pathway","\u5e94\u7528\u573a\u666f":"Application","\u8bc4\u4ef7\u6307\u6807":"Evaluation indicator","\u539f\u6599\u7279\u6027":"Feedstock property","\u534f\u540c\u56fa\u5e9f":"Co-utilized solid waste","\u539f\u6599":"Feedstock","\u76ee\u6807\u5143\u7d20":"Target element","\u6c61\u67d3\u7269/\u5bf9\u8c61":"Pollutant/target","\u73af\u5883\u529f\u80fd\u6750\u6599":"Environmental functional materials","\u9ad8\u9644\u52a0\u503c\u6750\u6599":"High-value-added materials","\u5efa\u6750\u5229\u7528":"Construction materials","\u5730\u805a\u7269\u4e0e\u78b1\u6fc0\u53d1\u6750\u6599":"Geopolymers and alkali-activated materials","\u5143\u7d20\u63d0\u53d6":"Element extraction","\u80fd\u6e90\u4e0e\u78b3\u76f8\u5173\u5229\u7528":"Energy- and carbon-related uses","\u751f\u6001\u4e0e\u56de\u586b\u5229\u7528":"Ecological and backfill uses","\u534f\u540c\u8d44\u6e90\u5316\u5229\u7528":"Collaborative valorization","\u73af\u5883\u5e94\u7528":"Environmental applications","\u6c61\u67d3\u7269\u53bb\u9664":"Pollutant removal","\u5de5\u7a0b\u5e94\u7528":"Engineering applications","\u751f\u6001\u5e94\u7528":"Ecological applications","\u78b3\u51cf\u6392":"Carbon mitigation","\u73af\u5883\u6027\u80fd":"Environmental performance","\u5de5\u7a0b\u6027\u80fd":"Engineering performance","\u73af\u5883\u98ce\u9669":"Environmental risk","\u8d44\u6e90\u56de\u6536\u6027\u80fd":"Resource-recovery performance","\u73af\u5883\u7ee9\u6548":"Environmental performance","\u8d44\u6e90\u6d88\u8017":"Resource consumption","\u7ecf\u6d4e\u8bc4\u4ef7":"Economic assessment","\u5de5\u7a0b\u7a33\u5b9a\u6027":"Engineering stability","\u5316\u5b66\u7ec4\u6210":"Chemical composition","\u78b3\u7ec4\u5206":"Carbon fraction","\u5f62\u8c8c\u7ec4\u5206":"Morphological component","\u7269\u7406\u6027\u8d28":"Physical properties","\u77ff\u7269\u7ec4\u6210":"Mineral composition","\u5316\u5b66\u6027\u8d28":"Chemical properties","\u5de5\u4e1a\u56fa\u5e9f":"Industrial solid waste","\u77ff\u4e1a\u56fa\u5e9f":"Mining waste","\u7070\u6e23\u7c7b\u56fa\u5e9f":"Ash-related solid waste","\u5206\u7c7b\u5b57\u6bb5":"Classification field","\u91cd\u91d1\u5c5e":"Heavy metals","\u67d3\u6599":"Dyes","\u7a00\u571f\u5143\u7d20":"Rare-earth elements","\u5173\u952e\u5143\u7d20":"Critical elements","\u94dd/\u6c27\u5316\u94dd":"Aluminum/alumina","\u9553":"Gallium","\u9502":"Lithium","\u57fa\u7840\u7814\u7a76":"Basic research","\u5b9e\u9a8c\u5ba4\u5236\u5907":"Laboratory preparation","\u5de5\u827a\u4f18\u5316":"Process optimization","\u5e94\u7528\u9a8c\u8bc1":"Application validation","\u4e2d\u8bd5/\u5de5\u7a0b\u793a\u8303":"Pilot/engineering demonstration","\u4ea7\u4e1a\u5316/\u5546\u4e1a\u5316":"Industrial/commercial application","\u589e\u5f3a\u6c61\u67d3\u7269\u53bb\u9664":"Enhanced pollutant removal","\u63d0\u9ad8\u5f3a\u5ea6/\u8010\u4e45\u6027":"Improved strength/durability","\u6210\u672c\u4e0e\u5e02\u573a\u9700\u6c42":"Cost and market demand","\u964d\u4f4e\u91cd\u91d1\u5c5e\u6d78\u51fa":"Reduced heavy-metal leaching","\u6539\u5584\u5b54\u7ed3\u6784/\u6bd4\u8868\u9762\u79ef":"Improved pore structure/specific surface area","\u8865\u5145Si-Al-Ca\u7ec4\u5206":"Supply of Si-Al-Ca components","\u4fc3\u8fdb\u80f6\u51dd/\u805a\u5408\u53cd\u5e94":"Enhanced hydration/polymerization","\u4fc3\u8fdb\u70e7\u7ed3/\u7194\u878d\u6210\u578b":"Enhanced sintering/melt forming","\u73af\u5883\u4fee\u590d\u9700\u6c42":"Environmental remediation demand","\u4fc3\u8fdb\u78b3\u9178\u5316\u56fa\u5b9a":"Enhanced carbonation and sequestration","\u78b1\u6fc0\u53d1\u5242":"Alkali activator","\u70ed\u6d3b\u5316/\u70e7\u7ed3":"Thermal activation/sintering","\u63d0\u9ad8\u5de5\u7a0b\u9002\u914d\u6027":"Improved engineering suitability","\u77ff\u6e23/\u94a2\u6e23":"Slag/steel slag","\u6c34\u6ce5\u719f\u6599/\u77f3\u7070":"Cement clinker/lime","\u78b3\u51cf\u6392/CO2\u77ff\u5316\u9700\u6c42":"Carbon mitigation/CO2 mineralization demand","\u964d\u4f4e\u80fd\u8017\u6216\u6210\u672c":"Reduced energy use or cost","\u653f\u7b56/\u6807\u51c6\u7ea6\u675f":"Policy/standard constraints","\u8c03\u8282\u78b1\u5ea6/pH":"Alkalinity/pH adjustment","\u4fc3\u8fdb\u6c34\u5316/\u805a\u5408\u53cd\u5e94":"Enhanced hydration/polymerization","\u6539\u5584\u5b54\u9699\u7ed3\u6784":"Improved pore structure","\u6210\u672c\u7ea6\u675f":"Cost constraints","\u5de5\u7a0b\u5927\u5b97\u6d88\u7eb3\u9700\u6c42":"Demand for large-scale engineering utilization","\u5e9f\u73bb\u7483":"Waste glass","\u9178/\u78b1\u6d17\u9884\u5904\u7406":"Acid/alkali washing pretreatment"}''')
df=pd.read_csv(args.corpus,encoding='utf-8-sig',dtype=str,keep_default_na=False).fillna('')
df.columns=df.columns.str.strip()
assert 'Paper_ID' in df.columns, 'Paper_ID must come from the frozen 3075 corpus'
assert len(df)==3075, f'Expected 3075 records, got {len(df)}; check the frozen 2000-2025 input'
# 3. Identify input columns automatically
# =========================================================

def find_col(possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

col_title = find_col(["Title", "Article Title", "\u9898\u540d", "\u6807\u9898"])
col_title_en = find_col(["Title_EN", "English Title", "Title English"])
col_abstract = find_col(["Abstract", "Abstract Note", "\u6458\u8981"])
col_year = find_col(["Year_clean", "Year", "Publication Year", "\u5e74\u4efd"])
col_primary = find_col(["Primary Category", "Primary_Category", "Revised Category", "\u6280\u672f\u5927\u7c7b", "Category"])
col_subroute = find_col(["Sub-route Label", "Subroute", "Sub_route", "Subroute_Label", "\u5177\u4f53\u6280\u672f\u8def\u5f84", "Sub-route"])

keyword_cols = []
for c in ["Keywords", "Author Keywords", "Keywords Plus", "Index Keywords"]:
    if c in df.columns:
        keyword_cols.append(c)

print("Title column:", col_title)
print("Abstract column:", col_abstract)
print("Year column:", col_year)
print("Primary-category column:", col_primary)
print("Subroute column:", col_subroute)
print("Keyword columns:", keyword_cols)

if col_title is None:
    raise ValueError("No title column found. Check Title / Article Title.")

# =========================================================
# 4. Text normalization
# =========================================================

def norm_text(x):
    x = str(x).lower()
    x = x.replace("–", "-").replace("—", "-")
    x = x.replace("_", " ")
    x = x.replace("co₂", "co2")
    x = x.replace("co 2", "co2")
    x = x.replace("al₂o₃", "al2o3")
    x = x.replace("sio₂", "sio2")
    x = x.replace("fe₂o₃", "fe2o3")
    x = x.replace("cao", "cao")
    x = re.sub(r"\s+", " ", x)
    return x

def contains_any(text, patterns):
    hit = []
    for p in patterns:
        p2 = norm_text(p)
        if p2 and p2 in text:
            hit.append(p)
    return hit

# =========================================================
# 5. Entity dictionaries
# =========================================================
# Dictionary format
# Research implementation note.
# Research implementation note.
# Research implementation note.
# Research implementation note.
# }

tech_dict = {
    "Adsorbents": {
        "type": "Valorization pathway",
        "category": "Environmental functional materials",
        "patterns": ["adsorption", "adsorbent", "adsorbents", "sorption", "biosorption", "activated carbon"]
    },
    "Zeolites/molecular sieves": {
        "type": "Valorization pathway",
        "category": "High-value-added materials",
        "patterns": ["zeolite", "zeolites", "molecular sieve", "molecular sieves"]
    },
    "Wastewater-treatment materials": {
        "type": "Valorization pathway",
        "category": "Environmental functional materials",
        "patterns": ["wastewater treatment", "water treatment", "sewage treatment"]
    },
    "Cement/concrete/mortar": {
        "type": "Valorization pathway",
        "category": "Construction materials",
        "patterns": ["cement", "cements", "concrete", "mortar", "cement mortar", "portland cement", "opc"]
    },
    "Geopolymer materials": {
        "type": "Valorization pathway",
        "category": "Geopolymers and alkali-activated materials",
        "patterns": ["geopolymer", "geopolymers", "geopolymerization", "geopolymerisation"]
    },
    "Alkali-activated materials": {
        "type": "Valorization pathway",
        "category": "Geopolymers and alkali-activated materials",
        "patterns": ["alkali activation", "alkali-activated", "alkali activated", "sodium hydroxide", "naoh"]
    },
    "Ceramics/glass-ceramics": {
        "type": "Valorization pathway",
        "category": "High-value-added materials",
        "patterns": ["ceramic", "ceramics", "glass-ceramic", "glass ceramic", "glass-ceramics", "glass ceramics", "mullite"]
    },
    "Rare-earth/critical-element recovery": {
        "type": "Valorization pathway",
        "category": "Element extraction",
        "patterns": ["rare earth", "rare earth elements", "ree", "rees", "critical elements", "critical element"]
    },
    "Aluminum/alumina extraction": {
        "type": "Valorization pathway",
        "category": "Element extraction",
        "patterns": ["alumina", "aluminum oxide", "aluminium oxide", "aluminum extraction", "aluminium extraction"]
    },
    "Metal recovery": {
        "type": "Valorization pathway",
        "category": "Element extraction",
        "patterns": ["metal recovery", "metals recovery", "recovery of metals", "extract metals"]
    },
    "Carbon materials": {
        "type": "Valorization pathway",
        "category": "Energy- and carbon-related uses",
        "patterns": ["carbon materials", "activated carbon", "porous carbon", "carbon nanotube", "carbon fiber"]
    },
    "Carbon capture/mineral carbonation": {
        "type": "Valorization pathway",
        "category": "Energy- and carbon-related uses",
        "patterns": ["co2 capture", "carbon capture", "carbon dioxide capture", "mineral carbonation", "carbonation"]
    },
    "Soil amendment/stabilization": {
        "type": "Valorization pathway",
        "category": "Ecological and backfill uses",
        "patterns": ["soil amendment", "soil stabilization", "soil stabilisation", "soil remediation", "soil improvement"]
    },
    "Aggregates/road-base materials": {
        "type": "Valorization pathway",
        "category": "Construction materials",
        "patterns": ["aggregate", "aggregates", "road material", "road base", "roadbed", "pavement"]
    },
    "Bricks/sintered products": {
        "type": "Valorization pathway",
        "category": "Construction materials",
        "patterns": ["brick", "bricks", "sintered products", "sintering"]
    },
    "Catalytic/photocatalytic materials": {
        "type": "Valorization pathway",
        "category": "High-value-added materials",
        "patterns": ["catalyst", "catalysts", "photocatalyst", "photocatalysis", "photocatalytic"]
    },
    "Functional fillers/composites": {
        "type": "Valorization pathway",
        "category": "High-value-added materials",
        "patterns": ["filler", "fillers", "composite", "composites", "polymer composite"]
    },
    "Cenospheres": {
        "type": "Valorization pathway",
        "category": "High-value-added materials",
        "patterns": ["cenosphere", "cenospheres", "hollow microsphere", "hollow microspheres"]
    },
    "Unburned-carbon recovery/flotation": {
        "type": "Valorization pathway",
        "category": "Energy- and carbon-related uses",
        "patterns": ["unburned carbon", "unburnt carbon", "carbon recovery", "flotation"]
    },
    "Multi-solid-waste co-utilization": {
        "type": "Valorization pathway",
        "category": "Collaborative valorization",
        "patterns": ["co-utilization", "co utilization", "co-processing", "multi-solid waste", "multi waste", "solid waste synergy"]
    }
}

application_dict = {
    "Wastewater treatment": {
        "type": "Application",
        "category": "Environmental applications",
        "patterns": ["wastewater treatment", "water treatment", "sewage treatment", "aqueous solution"]
    },
    "Heavy-metal removal": {
        "type": "Application",
        "category": "Pollutant removal",
        "patterns": ["heavy metals", "heavy metal", "pb(ii)", "cd(ii)", "cr(vi)", "cu(ii)", "lead", "cadmium", "chromium", "copper"]
    },
    "Dye adsorption": {
        "type": "Application",
        "category": "Pollutant removal",
        "patterns": ["dye", "dyes", "methylene blue", "rhodamine", "malachite green"]
    },
    "Building materials": {
        "type": "Application",
        "category": "Engineering applications",
        "patterns": ["construction material", "building material", "cement", "concrete", "mortar"]
    },
    "Road engineering": {
        "type": "Application",
        "category": "Engineering applications",
        "patterns": ["road", "roadbed", "pavement", "road base", "highway"]
    },
    "Ecological restoration": {
        "type": "Application",
        "category": "Ecological applications",
        "patterns": ["ecological restoration", "remediation", "soil remediation", "land reclamation"]
    },
    "CO2 mitigation": {
        "type": "Application",
        "category": "Carbon mitigation",
        "patterns": ["co2 reduction", "carbon reduction", "carbon emission", "carbon dioxide", "carbon capture"]
    },
    "Resource recovery": {
        "type": "Application",
        "category": "Resource recovery",
        "patterns": ["resource recovery", "metal recovery", "element recovery", "rare earth recovery"]
    }
}

indicator_dict = {
    "Adsorption capacity": {
        "type": "Evaluation indicator",
        "category": "Environmental performance",
        "patterns": ["adsorption capacity", "sorption capacity", "qmax", "maximum adsorption"]
    },
    "Removal efficiency": {
        "type": "Evaluation indicator",
        "category": "Environmental performance",
        "patterns": ["removal efficiency", "removal rate", "removal percentage"]
    },
    "Compressive strength": {
        "type": "Evaluation indicator",
        "category": "Engineering performance",
        "patterns": ["compressive strength", "strength", "mechanical strength"]
    },
    "Leaching toxicity": {
        "type": "Evaluation indicator",
        "category": "Environmental risk",
        "patterns": ["leaching toxicity", "leachability", "leaching concentration", "toxicity characteristic"]
    },
    "Recovery rate": {
        "type": "Evaluation indicator",
        "category": "Resource-recovery performance",
        "patterns": ["recovery rate", "extraction efficiency", "leaching efficiency", "recovery efficiency"]
    },
    "Carbon emissions": {
        "type": "Evaluation indicator",
        "category": "Environmental performance",
        "patterns": ["carbon emission", "co2 emission", "greenhouse gas", "gwp", "global warming potential"]
    },
    "Energy consumption": {
        "type": "Evaluation indicator",
        "category": "Resource consumption",
        "patterns": ["energy consumption", "energy demand", "energy use"]
    },
    "Material consumption": {
        "type": "Evaluation indicator",
        "category": "Resource consumption",
        "patterns": ["material consumption", "material demand", "material flow"]
    },
    "Economic performance": {
        "type": "Evaluation indicator",
        "category": "Economic assessment",
        "patterns": ["cost", "economic", "techno-economic", "benefit", "feasibility"]
    },
    "Stability": {
        "type": "Evaluation indicator",
        "category": "Engineering stability",
        "patterns": ["stability", "durability", "immobilization", "stabilization"]
    }
}

property_dict = {
    "SiO2/Al2O3": {
        "type": "Feedstock property",
        "category": "Chemical composition",
        "patterns": ["sio2", "silica", "al2o3", "alumina", "aluminosilicate", "si/al"]
    },
    "CaO": {
        "type": "Feedstock property",
        "category": "Chemical composition",
        "patterns": ["cao", "calcium oxide", "free lime", "lime"]
    },
    "Fe2O3": {
        "type": "Feedstock property",
        "category": "Chemical composition",
        "patterns": ["fe2o3", "iron oxide", "ferric oxide"]
    },
    "Unburned carbon": {
        "type": "Feedstock property",
        "category": "Carbon fraction",
        "patterns": ["unburned carbon", "unburnt carbon", "loss on ignition", "loi"]
    },
    "Cenospheres": {
        "type": "Feedstock property",
        "category": "Morphological component",
        "patterns": ["cenosphere", "cenospheres", "hollow microsphere", "hollow sphere"]
    },
    "Heavy-metal leaching risk": {
        "type": "Feedstock property",
        "category": "Environmental risk",
        "patterns": ["heavy metal", "heavy metals", "leaching toxicity", "leachability", "toxic elements"]
    },
    "Particle size/fineness": {
        "type": "Feedstock property",
        "category": "Physical properties",
        "patterns": ["particle size", "fineness", "specific surface area"]
    },
    "Mineral phases": {
        "type": "Feedstock property",
        "category": "Mineral composition",
        "patterns": ["mullite", "quartz", "hematite", "crystalline phase", "mineral phase"]
    },
    "Alkalinity": {
        "type": "Feedstock property",
        "category": "Chemical properties",
        "patterns": ["alkalinity", "alkaline", "ph"]
    }
}

cowaste_dict = {
    "Slag": {
        "type": "Co-utilized solid waste",
        "category": "Industrial solid waste",
        "patterns": ["slag", "blast furnace slag", "steel slag"]
    },
    "Steel slag": {
        "type": "Co-utilized solid waste",
        "category": "Industrial solid waste",
        "patterns": ["steel slag"]
    },
    "Red mud": {
        "type": "Co-utilized solid waste",
        "category": "Industrial solid waste",
        "patterns": ["red mud", "bauxite residue"]
    },
    "Desulfurization gypsum": {
        "type": "Co-utilized solid waste",
        "category": "Industrial solid waste",
        "patterns": ["desulfurization gypsum", "desulphurization gypsum", "fgd gypsum", "gypsum"]
    },
    "Sludge": {
        "type": "Co-utilized solid waste",
        "category": "Sludge",
        "patterns": ["sludge", "sewage sludge"]
    },
    "Cement kiln dust": {
        "type": "Co-utilized solid waste",
        "category": "Industrial solid waste",
        "patterns": ["cement kiln dust", "ckd"]
    },
    "Tailings": {
        "type": "Co-utilized solid waste",
        "category": "Mining waste",
        "patterns": ["tailings", "mine tailings"]
    },
    "Biomass ash": {
        "type": "Co-utilized solid waste",
        "category": "Ash-related solid waste",
        "patterns": ["biomass ash", "rice husk ash"]
    }
}

# =========================================================
# 6. Helper functions for entity matching
# =========================================================

def match_entities(text, entity_dict):
    results = {}
    for std_name, info in entity_dict.items():
        hits = contains_any(text, info["patterns"])
        if hits:
            results[std_name] = {
                "type": info["type"],
                "category": info["category"],
                "hits": hits
            }
    return results

def safe_get(row, col):
    if col is None:
        return ""
    return str(row.get(col, ""))

# =========================================================
# 7. Generate candidate triples
# =========================================================

triples = []
seen = set()

def add_triple(
    paper_id, year, title, primary, subroute,
    source, relation, target,
    source_type, target_type,
    evidence, confidence="Medium", need_check="No"
):
    key = (paper_id, source, relation, target)
    if key in seen:
        return
    seen.add(key)
    
    triples.append({
        "Paper_ID": paper_id,
        "Year": year,
        "Title": title,
        "Primary_Category": primary,
        "Subroute": subroute,
        "Source": source,
        "Relation": relation,
        "Target": target,
        "Source_Type": source_type,
        "Target_Type": target_type,
        "Evidence_Text": evidence,
        "Confidence": confidence,
        "Need_Check": need_check
    })

for idx, row in df.iterrows():
    paper_id = str(row.get("Paper_ID", "")).strip()
    if paper_id == "":
        paper_id = f"P{idx+1:05d}"
    
    year = safe_get(row, col_year)
    title_raw = safe_get(row, col_title)
    title = title_raw if not re.search(r"[\u3400-\u9fff]", title_raw) else safe_get(row, col_title_en)
    abstract = safe_get(row, col_abstract)
    primary = safe_get(row, col_primary)
    primary = TERM_TRANSLATIONS.get(primary, primary)
    subroute = safe_get(row, col_subroute)
    subroute = TERM_TRANSLATIONS.get(subroute, subroute)
    
    kw_text = " ".join([safe_get(row, c) for c in keyword_cols])
    text_all_raw = " ".join([title_raw, abstract, kw_text, primary, subroute])
    text_all = norm_text(text_all_raw)
    
    techs = match_entities(text_all, tech_dict)
    apps = match_entities(text_all, application_dict)
    indicators = match_entities(text_all, indicator_dict)
    props = match_entities(text_all, property_dict)
    cowastes = match_entities(text_all, cowaste_dict)
    
    # -----------------------------------------------------
    # Rule 1: Coal fly ash produces a valorization pathway
    # -----------------------------------------------------
    for tech, info in techs.items():
        add_triple(
            paper_id, year, title, primary, subroute,
            source="Coal fly ash",
            relation="produces",
            target=tech,
            source_type="Feedstock",
            target_type="Valorization pathway",
            evidence="; ".join(info["hits"][:6]),
            confidence="High",
            need_check="No"
        )
    
    # -----------------------------------------------------
    # Rule 2: A valorization pathway is used for an application
    # -----------------------------------------------------
    for tech, tinfo in techs.items():
        for app, ainfo in apps.items():
            add_triple(
                paper_id, year, title, primary, subroute,
                source=tech,
                relation="is used for",
                target=app,
                source_type="Valorization pathway",
                target_type="Application",
                evidence="Tech: " + "; ".join(tinfo["hits"][:3]) + " | App: " + "; ".join(ainfo["hits"][:3]),
                confidence="Medium",
                need_check="No"
            )
    
    # -----------------------------------------------------
    # Rule 3: A valorization pathway is evaluated by an indicator
    # -----------------------------------------------------
    for tech, tinfo in techs.items():
        for ind, iinfo in indicators.items():
            add_triple(
                paper_id, year, title, primary, subroute,
                source=tech,
                relation="is evaluated by",
                target=ind,
                source_type="Valorization pathway",
                target_type="Evaluation indicator",
                evidence="Tech: " + "; ".join(tinfo["hits"][:3]) + " | Indicator: " + "; ".join(iinfo["hits"][:3]),
                confidence="Medium",
                need_check="No"
            )
    
    # -----------------------------------------------------
    # Rule 4: A valorization pathway removes a pollutant/target
    # -----------------------------------------------------
    pollutant_targets = {
        "Heavy metals": ["heavy metal", "heavy metals", "pb(ii)", "cd(ii)", "cr(vi)", "lead", "cadmium", "chromium"],
        "Dyes": ["dye", "dyes", "methylene blue", "rhodamine", "malachite green"]
    }
    
    for target_name, pats in pollutant_targets.items():
        hits = contains_any(text_all, pats)
        if hits:
            for tech, tinfo in techs.items():
                if tech in ["Adsorbents", "Wastewater-treatment materials", "Zeolites/molecular sieves", "Carbon materials", "Catalytic/photocatalytic materials"]:
                    add_triple(
                        paper_id, year, title, primary, subroute,
                        source=tech,
                        relation="removes",
                        target=target_name,
                        source_type="Valorization pathway",
                        target_type="Pollutant/target",
                        evidence="Tech: " + "; ".join(tinfo["hits"][:3]) + " | Target: " + "; ".join(hits[:3]),
                        confidence="High",
                        need_check="No"
                    )
    
    # -----------------------------------------------------
    # Rule 5: Coal fly ash recovers/extracts an element
    # -----------------------------------------------------
    element_targets = {
        "Rare-earth elements": ["rare earth", "rare earth elements", "ree", "rees"],
        "Critical elements": ["critical elements", "critical element"],
        "Aluminum/alumina": ["alumina", "aluminum oxide", "aluminium oxide", "aluminum", "aluminium"],
        "Gallium": ["gallium", "ga"],
        "Lithium": ["lithium", "li"]
    }
    
    extraction_signal = contains_any(
        text_all,
        ["extraction", "extract", "recovery", "recover", "leaching", "acid leaching", "alkali leaching"]
    )
    
    for elem, pats in element_targets.items():
        hits = contains_any(text_all, pats)
        if hits and extraction_signal:
            add_triple(
                paper_id, year, title, primary, subroute,
                source="Coal fly ash",
                relation="recovers",
                target=elem,
                source_type="Feedstock",
                target_type="Target element",
                evidence="Element: " + "; ".join(hits[:3]) + " | Signal: " + "; ".join(extraction_signal[:3]),
                confidence="High",
                need_check="No"
            )
    
    # -----------------------------------------------------
    # Rule 6: A feedstock property is associated with a pathway
    # Do not infer promotion or inhibition; retain the neutral association relation.
    # -----------------------------------------------------
    for prop, pinfo in props.items():
        for tech, tinfo in techs.items():
            add_triple(
                paper_id, year, title, primary, subroute,
                source=prop,
                relation="is associated with",
                target=tech,
                source_type="Feedstock property",
                target_type="Valorization pathway",
                evidence="Property: " + "; ".join(pinfo["hits"][:3]) + " | Tech: " + "; ".join(tinfo["hits"][:3]),
                confidence="Low",
                need_check="Yes"
            )
    
    # -----------------------------------------------------
    # Rule 7: Coal fly ash is co-utilized with another solid waste
    # -----------------------------------------------------
    for cw, cinfo in cowastes.items():
        add_triple(
            paper_id, year, title, primary, subroute,
            source="Coal fly ash",
            relation="co-processes",
            target=cw,
            source_type="Feedstock",
            target_type="Co-utilized solid waste",
            evidence="; ".join(cinfo["hits"][:6]),
            confidence="Medium",
            need_check="No"
        )
    
    # -----------------------------------------------------
    # Rule 8: A primary category includes a specific pathway
    # Derived from the supplied classification fields.
    # -----------------------------------------------------
    if primary and primary.lower() not in ["unclear", "nan", ""]:
        if subroute and subroute.lower() not in ["unclear", "nan", ""]:
            add_triple(
                paper_id, year, title, primary, subroute,
                source=primary,
                relation="includes",
                target=subroute,
                source_type="Primary category",
                target_type="Specific valorization pathway",
                evidence="Classification field",
                confidence="High",
                need_check="No"
            )

# =========================================================

assert len(triples)>0, 'No relation extracted'
out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
with out.open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(triples[0]));writer.writeheader();writer.writerows(triples)
print(f'Original dictionary candidate extraction: {len(df):,} papers, {len(triples):,} candidate supports saved to {out}')
print('This is NOT the author-corrected final 19,177 triple snapshot. V2/V3 decisions must be applied or use the frozen final table.')
