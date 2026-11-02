#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Match feedstock properties, valorization pathways, and synergy factors
using the original dictionaries archived from the research notebook.

The module reports candidate lexical matches and their source papers. It does
not independently validate relation direction or semantic correctness.
"""
from pathlib import Path
import argparse,csv,json,re
from collections import Counter
HERE=Path(__file__).resolve().parent
DEFAULT=HERE/'inputs'/'Author Frozen Corpus 3075.csv'
FILES=['KG Original 5 Entity Dictionaries.json','Property Pathway Dictionaries.json',
       'Limiting Factors Dictionary.json','External Synergy Dictionaries.json']

def match_text(text,term):
    term=(term or '').strip().lower()
    if not term:return False
    # Exact word boundaries for ASCII phrases prevent e.g. "Pb" matching arbitrary words.
    patt=r'(?<![a-z0-9])'+re.escape(term)+r'(?![a-z0-9])' if re.search(r'[a-z0-9]',term) else re.escape(term)
    return re.search(patt,text.lower()) is not None

def load_dicts():
    merged=[]
    for name in FILES:
        item=json.loads((HERE/'dict'/name).read_text('utf-8'))
        for subgroup,terms in item['dictionaries'].items():
            for entity,info in terms.items():
                merged.append({'Dictionary':name,'Source_Cell':item.get('cell_zero_based',''),
                               'Subgroup':subgroup,'Entity':entity,
                               'Type':info.get('type',info.get('group','')),
                               'English_Name':info.get('en',''),
                               'Patterns':info.get('patterns',[])})
    return merged

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--papers',default=str(DEFAULT));ap.add_argument('--out',default=str(HERE/'outputs'/'Code2 Candidate Entity Matches.csv'))
    ap.add_argument('--include-patterns',action='store_true',help='Reserved for compatibility; output includes the matched pattern.')
    args=ap.parse_args()
    with open(args.papers,'r',encoding='utf-8-sig',newline='') as f:papers=list(csv.DictReader(f))
    definitions=load_dicts();out=Path(args.out);out.parent.mkdir(exist_ok=True,parents=True)
    translation = json.loads(r'''{"\u7c89\u7164\u7070":"Coal fly ash","\u5236\u5907":"produces","\u7528\u4e8e":"is used for","\u8bc4\u4ef7":"is evaluated by","\u53bb\u9664":"removes","\u56de\u6536":"recovers","\u534f\u540c":"co-processes","\u5173\u8054":"is associated with","\u5305\u542b":"includes","\u5438\u9644\u6750\u6599":"Adsorbents","\u6cb8\u77f3/\u5206\u5b50\u7b5b":"Zeolites/molecular sieves","\u5e9f\u6c34\u5904\u7406\u6750\u6599":"Wastewater-treatment materials","\u6c34\u6ce5/\u6df7\u51dd\u571f/\u7802\u6d46":"Cement/concrete/mortar","\u5730\u805a\u7269\u6750\u6599":"Geopolymer materials","\u78b1\u6fc0\u53d1\u6750\u6599":"Alkali-activated materials","\u9676\u74f7/\u73bb\u7483\u9676\u74f7":"Ceramics/glass-ceramics","\u7a00\u571f/\u5173\u952e\u5143\u7d20\u56de\u6536":"Rare-earth/critical-element recovery","\u94dd/\u6c27\u5316\u94dd\u63d0\u53d6":"Aluminum/alumina extraction","\u91d1\u5c5e\u56de\u6536":"Metal recovery","\u78b3\u6750\u6599":"Carbon materials","\u78b3\u6355\u96c6/\u77ff\u5316\u5c01\u5b58":"Carbon capture/mineral carbonation","\u571f\u58e4\u6539\u826f/\u7a33\u5b9a\u5316":"Soil amendment/stabilization","\u9aa8\u6599/\u8def\u57fa/\u9053\u8def\u6750\u6599":"Aggregates/road-base materials","\u7816/\u70e7\u7ed3\u5236\u54c1":"Bricks/sintered products","\u50ac\u5316/\u5149\u50ac\u5316\u6750\u6599":"Catalytic/photocatalytic materials","\u529f\u80fd\u586b\u6599/\u590d\u5408\u6750\u6599":"Functional fillers/composites","\u7a7a\u5fc3\u5fae\u73e0":"Cenospheres","\u672a\u71c3\u78b3\u56de\u6536/\u6d6e\u9009":"Unburned-carbon recovery/flotation","\u591a\u56fa\u5e9f\u534f\u540c":"Multi-solid-waste co-utilization","\u5e9f\u6c34\u5904\u7406":"Wastewater treatment","\u91cd\u91d1\u5c5e\u53bb\u9664":"Heavy-metal removal","\u67d3\u6599\u5438\u9644":"Dye adsorption","\u5efa\u7b51\u6750\u6599":"Building materials","\u9053\u8def\u5de5\u7a0b":"Road engineering","\u751f\u6001\u4fee\u590d":"Ecological restoration","CO2\u51cf\u6392":"CO2 mitigation","\u8d44\u6e90\u56de\u6536":"Resource recovery","\u5438\u9644\u5bb9\u91cf":"Adsorption capacity","\u53bb\u9664\u7387":"Removal efficiency","\u6297\u538b\u5f3a\u5ea6":"Compressive strength","\u6d78\u51fa\u6bd2\u6027":"Leaching toxicity","\u56de\u6536\u7387":"Recovery rate","\u78b3\u6392\u653e":"Carbon emissions","\u80fd\u8017":"Energy consumption","\u7269\u8017":"Material consumption","\u7ecf\u6d4e\u6027":"Economic performance","\u7a33\u5b9a\u6027":"Stability","SiO2/Al2O3":"SiO2/Al2O3","CaO":"CaO","Fe2O3":"Fe2O3","\u672a\u71c3\u78b3":"Unburned carbon","\u91cd\u91d1\u5c5e\u6d78\u51fa\u98ce\u9669":"Heavy-metal leaching risk","\u7c92\u5f84/\u7ec6\u5ea6":"Particle size/fineness","\u77ff\u7269\u76f8":"Mineral phases","\u78b1\u5ea6":"Alkalinity","\u77ff\u6e23":"Slag","\u94a2\u6e23":"Steel slag","\u8d64\u6ce5":"Red mud","\u8131\u786b\u77f3\u818f":"Desulfurization gypsum","\u6c61\u6ce5":"Sludge","\u6c34\u6ce5\u7a91\u7070":"Cement kiln dust","\u5c3e\u77ff":"Tailings","\u751f\u7269\u8d28\u7070":"Biomass ash","\u6280\u672f\u8def\u5f84":"Valorization pathway","\u5e94\u7528\u573a\u666f":"Application","\u8bc4\u4ef7\u6307\u6807":"Evaluation indicator","\u539f\u6599\u7279\u6027":"Feedstock property","\u534f\u540c\u56fa\u5e9f":"Co-utilized solid waste","\u539f\u6599":"Feedstock","\u76ee\u6807\u5143\u7d20":"Target element","\u6c61\u67d3\u7269/\u5bf9\u8c61":"Pollutant/target","\u73af\u5883\u529f\u80fd\u6750\u6599":"Environmental functional materials","\u9ad8\u9644\u52a0\u503c\u6750\u6599":"High-value-added materials","\u5efa\u6750\u5229\u7528":"Construction materials","\u5730\u805a\u7269\u4e0e\u78b1\u6fc0\u53d1\u6750\u6599":"Geopolymers and alkali-activated materials","\u5143\u7d20\u63d0\u53d6":"Element extraction","\u80fd\u6e90\u4e0e\u78b3\u76f8\u5173\u5229\u7528":"Energy- and carbon-related uses","\u751f\u6001\u4e0e\u56de\u586b\u5229\u7528":"Ecological and backfill uses","\u534f\u540c\u8d44\u6e90\u5316\u5229\u7528":"Collaborative valorization","\u73af\u5883\u5e94\u7528":"Environmental applications","\u6c61\u67d3\u7269\u53bb\u9664":"Pollutant removal","\u5de5\u7a0b\u5e94\u7528":"Engineering applications","\u751f\u6001\u5e94\u7528":"Ecological applications","\u78b3\u51cf\u6392":"Carbon mitigation","\u73af\u5883\u6027\u80fd":"Environmental performance","\u5de5\u7a0b\u6027\u80fd":"Engineering performance","\u73af\u5883\u98ce\u9669":"Environmental risk","\u8d44\u6e90\u56de\u6536\u6027\u80fd":"Resource-recovery performance","\u73af\u5883\u7ee9\u6548":"Environmental performance","\u8d44\u6e90\u6d88\u8017":"Resource consumption","\u7ecf\u6d4e\u8bc4\u4ef7":"Economic assessment","\u5de5\u7a0b\u7a33\u5b9a\u6027":"Engineering stability","\u5316\u5b66\u7ec4\u6210":"Chemical composition","\u78b3\u7ec4\u5206":"Carbon fraction","\u5f62\u8c8c\u7ec4\u5206":"Morphological component","\u7269\u7406\u6027\u8d28":"Physical properties","\u77ff\u7269\u7ec4\u6210":"Mineral composition","\u5316\u5b66\u6027\u8d28":"Chemical properties","\u5de5\u4e1a\u56fa\u5e9f":"Industrial solid waste","\u77ff\u4e1a\u56fa\u5e9f":"Mining waste","\u7070\u6e23\u7c7b\u56fa\u5e9f":"Ash-related solid waste","\u5206\u7c7b\u5b57\u6bb5":"Classification field","\u91cd\u91d1\u5c5e":"Heavy metals","\u67d3\u6599":"Dyes","\u7a00\u571f\u5143\u7d20":"Rare-earth elements","\u5173\u952e\u5143\u7d20":"Critical elements","\u94dd/\u6c27\u5316\u94dd":"Aluminum/alumina","\u9553":"Gallium","\u9502":"Lithium","\u57fa\u7840\u7814\u7a76":"Basic research","\u5b9e\u9a8c\u5ba4\u5236\u5907":"Laboratory preparation","\u5de5\u827a\u4f18\u5316":"Process optimization","\u5e94\u7528\u9a8c\u8bc1":"Application validation","\u4e2d\u8bd5/\u5de5\u7a0b\u793a\u8303":"Pilot/engineering demonstration","\u4ea7\u4e1a\u5316/\u5546\u4e1a\u5316":"Industrial/commercial application","\u589e\u5f3a\u6c61\u67d3\u7269\u53bb\u9664":"Enhanced pollutant removal","\u63d0\u9ad8\u5f3a\u5ea6/\u8010\u4e45\u6027":"Improved strength/durability","\u6210\u672c\u4e0e\u5e02\u573a\u9700\u6c42":"Cost and market demand","\u964d\u4f4e\u91cd\u91d1\u5c5e\u6d78\u51fa":"Reduced heavy-metal leaching","\u6539\u5584\u5b54\u7ed3\u6784/\u6bd4\u8868\u9762\u79ef":"Improved pore structure/specific surface area","\u8865\u5145Si-Al-Ca\u7ec4\u5206":"Supply of Si-Al-Ca components","\u4fc3\u8fdb\u80f6\u51dd/\u805a\u5408\u53cd\u5e94":"Enhanced hydration/polymerization","\u4fc3\u8fdb\u70e7\u7ed3/\u7194\u878d\u6210\u578b":"Enhanced sintering/melt forming","\u73af\u5883\u4fee\u590d\u9700\u6c42":"Environmental remediation demand","\u4fc3\u8fdb\u78b3\u9178\u5316\u56fa\u5b9a":"Enhanced carbonation and sequestration","\u78b1\u6fc0\u53d1\u5242":"Alkali activator","\u70ed\u6d3b\u5316/\u70e7\u7ed3":"Thermal activation/sintering","\u63d0\u9ad8\u5de5\u7a0b\u9002\u914d\u6027":"Improved engineering suitability","\u77ff\u6e23/\u94a2\u6e23":"Slag/steel slag","\u6c34\u6ce5\u719f\u6599/\u77f3\u7070":"Cement clinker/lime","\u78b3\u51cf\u6392/CO2\u77ff\u5316\u9700\u6c42":"Carbon mitigation/CO2 mineralization demand","\u964d\u4f4e\u80fd\u8017\u6216\u6210\u672c":"Reduced energy use or cost","\u653f\u7b56/\u6807\u51c6\u7ea6\u675f":"Policy/standard constraints","\u8c03\u8282\u78b1\u5ea6/pH":"Alkalinity/pH adjustment","\u4fc3\u8fdb\u6c34\u5316/\u805a\u5408\u53cd\u5e94":"Enhanced hydration/polymerization","\u6539\u5584\u5b54\u9699\u7ed3\u6784":"Improved pore structure","\u6210\u672c\u7ea6\u675f":"Cost constraints","\u5de5\u7a0b\u5927\u5b97\u6d88\u7eb3\u9700\u6c42":"Demand for large-scale engineering utilization","\u5e9f\u73bb\u7483":"Waste glass","\u9178/\u78b1\u6d17\u9884\u5904\u7406":"Acid/alkali washing pretreatment"}''')
    type_translations = {
        'Mineral-related': 'Mineral-related',
        '\u77ff\u7269\u4e0e\u6d3b\u6027': 'Mineralogy and reactivity',
        '\u7269\u7406\u7ed3\u6784': 'Physical structure',
        '\u73af\u5883\u98ce\u9669\u4e0e\u6742\u8d28': 'Environmental risks and impurities',
        '\u6709\u4ef7\u5143\u7d20\u8d4b\u5b58': 'Valuable-element occurrence',
        '\u78b3\u9178\u5316\u6f5c\u529b': 'Carbonation potential',
        '\u534f\u540c\u6750\u6599': 'Co-utilized materials',
        '\u5de5\u827a\u8c03\u63a7': 'Process control',
        '\u7ecf\u6d4e\u5236\u5ea6': 'Economic and institutional factors',
    }
    for definition in definitions:
        definition['Subgroup'] = translation.get(definition['Subgroup'], definition['Subgroup'])
        entity = definition['Entity']
        fallback = definition.get('English_Name', '')
        definition['Entity'] = translation.get(entity, fallback or entity)
        ty = definition['Type']
        definition['Type'] = translation.get(ty, type_translations.get(ty, ty))
    untranslated = [
        (definition['Dictionary'], field, definition[field])
        for definition in definitions
        for field in ('Subgroup', 'Entity', 'Type')
        if re.search(r'[\u3400-\u9fff]', str(definition[field]))
    ]
    if untranslated:
        preview = untranslated[:10]
        raise ValueError(
            'Some original dictionary labels do not yet have approved English equivalents. '
            f'Add approved English equivalents to the translation map before export. Examples: {preview}'
        )
    termsets=[[(v.lower(),v) for v in d['Patterns'] if v and v.strip()] for d in definitions]
    fields=['Paper_ID','Year','Dictionary','Source_Cell','Subgroup','Entity','Entity_Type','Evidence_Pattern']
    count=0;category=Counter()
    with out.open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader()
        for paper in papers:
            text=' '.join((paper.get(k,'') or '') for k in ('Title','Abstract','Keywords')).lower()
            for dic,terms in zip(definitions,termsets):
                hit=None
                for low,original in terms:
                    start=text.find(low)
                    if start < 0: continue
                    # Retain matched word-boundary semantics; if first occurrence fails,
                    # search later occurrences before deciding.
                    while start >= 0:
                        end=start+len(low)
                        a=(start==0 or not (text[start-1].isascii() and text[start-1].isalnum()))
                        b=(end==len(text) or not (text[end].isascii() and text[end].isalnum()))
                        if a and b:hit=original;break
                        start=text.find(low,start+1)
                    if hit:break
                if hit:
                    evidence_pattern = translation.get(hit, hit)
                    if re.search(r'[\u3400-\u9fff]', evidence_pattern):
                        raise ValueError(
                            'A matched dictionary pattern is still Chinese. '
                            f'Add an approved English equivalent before export: {hit!r}'
                        )
                    wr.writerow({'Paper_ID':paper.get('Paper_ID',''),'Year':paper.get('Year',''),
                                 'Dictionary':dic['Dictionary'],'Source_Cell':dic['Source_Cell'],
                                 'Subgroup':dic['Subgroup'],'Entity':dic['Entity'],
                                 'Entity_Type':dic['Type'],'Evidence_Pattern':evidence_pattern})
                    count+=1;category[dic['Subgroup']]+=1
    print(f'{len(papers)} papers; {len(definitions)} dictionary entity definitions; {count} candidate entity matches -> {out}')
    print('These are candidate lexical matches, not V2/V3-reviewed final relationships.')
if __name__=='__main__':main()
