#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Field-level audit of V2/V3 author-review decisions and the frozen 2000-2025 graph.

The audit replays recorded V2/V3 files, 42 author-confirmed paper exclusions,
five held candidate relations, and the final 19,177 relation-support records.
It does not infer or recreate unrecorded human judgments.
"""
from pathlib import Path
import csv,json,hashlib,re
from collections import Counter
TERM_TRANSLATIONS = json.loads('{"\\u7c89\\u7164\\u7070": "Coal fly ash", "\\u5236\\u5907": "produces", "\\u7528\\u4e8e": "is used for", "\\u8bc4\\u4ef7": "is evaluated by", "\\u53bb\\u9664": "removes", "\\u56de\\u6536": "recovers", "\\u534f\\u540c": "co-processes", "\\u5173\\u8054": "is associated with", "\\u5305\\u542b": "includes", "\\u5438\\u9644\\u6750\\u6599": "Adsorbents", "\\u6cb8\\u77f3/\\u5206\\u5b50\\u7b5b": "Zeolites/molecular sieves", "\\u5e9f\\u6c34\\u5904\\u7406\\u6750\\u6599": "Wastewater-treatment materials", "\\u6c34\\u6ce5/\\u6df7\\u51dd\\u571f/\\u7802\\u6d46": "Cement/concrete/mortar", "\\u5730\\u805a\\u7269\\u6750\\u6599": "Geopolymer materials", "\\u78b1\\u6fc0\\u53d1\\u6750\\u6599": "Alkali-activated materials", "\\u9676\\u74f7/\\u73bb\\u7483\\u9676\\u74f7": "Ceramics/glass-ceramics", "\\u7a00\\u571f/\\u5173\\u952e\\u5143\\u7d20\\u56de\\u6536": "Rare-earth/critical-element recovery", "\\u94dd/\\u6c27\\u5316\\u94dd\\u63d0\\u53d6": "Aluminum/alumina extraction", "\\u91d1\\u5c5e\\u56de\\u6536": "Metal recovery", "\\u78b3\\u6750\\u6599": "Carbon materials", "\\u78b3\\u6355\\u96c6/\\u77ff\\u5316\\u5c01\\u5b58": "Carbon capture/mineral carbonation", "\\u571f\\u58e4\\u6539\\u826f/\\u7a33\\u5b9a\\u5316": "Soil amendment/stabilization", "\\u9aa8\\u6599/\\u8def\\u57fa/\\u9053\\u8def\\u6750\\u6599": "Aggregates/road-base materials", "\\u7816/\\u70e7\\u7ed3\\u5236\\u54c1": "Bricks/sintered products", "\\u50ac\\u5316/\\u5149\\u50ac\\u5316\\u6750\\u6599": "Catalytic/photocatalytic materials", "\\u529f\\u80fd\\u586b\\u6599/\\u590d\\u5408\\u6750\\u6599": "Functional fillers/composites", "\\u7a7a\\u5fc3\\u5fae\\u73e0": "Cenospheres", "\\u672a\\u71c3\\u78b3\\u56de\\u6536/\\u6d6e\\u9009": "Unburned-carbon recovery/flotation", "\\u591a\\u56fa\\u5e9f\\u534f\\u540c": "Multi-solid-waste co-utilization", "\\u5e9f\\u6c34\\u5904\\u7406": "Wastewater treatment", "\\u91cd\\u91d1\\u5c5e\\u53bb\\u9664": "Heavy-metal removal", "\\u67d3\\u6599\\u5438\\u9644": "Dye adsorption", "\\u5efa\\u7b51\\u6750\\u6599": "Building materials", "\\u9053\\u8def\\u5de5\\u7a0b": "Road engineering", "\\u751f\\u6001\\u4fee\\u590d": "Ecological restoration", "CO2\\u51cf\\u6392": "CO2 mitigation", "\\u8d44\\u6e90\\u56de\\u6536": "Resource recovery", "\\u5438\\u9644\\u5bb9\\u91cf": "Adsorption capacity", "\\u53bb\\u9664\\u7387": "Removal efficiency", "\\u6297\\u538b\\u5f3a\\u5ea6": "Compressive strength", "\\u6d78\\u51fa\\u6bd2\\u6027": "Leaching toxicity", "\\u56de\\u6536\\u7387": "Recovery rate", "\\u78b3\\u6392\\u653e": "Carbon emissions", "\\u80fd\\u8017": "Energy consumption", "\\u7269\\u8017": "Material consumption", "\\u7ecf\\u6d4e\\u6027": "Economic performance", "\\u7a33\\u5b9a\\u6027": "Stability", "SiO2/Al2O3": "SiO2/Al2O3", "CaO": "CaO", "Fe2O3": "Fe2O3", "\\u672a\\u71c3\\u78b3": "Unburned carbon", "\\u91cd\\u91d1\\u5c5e\\u6d78\\u51fa\\u98ce\\u9669": "Heavy-metal leaching risk", "\\u7c92\\u5f84/\\u7ec6\\u5ea6": "Particle size/fineness", "\\u77ff\\u7269\\u76f8": "Mineral phases", "\\u78b1\\u5ea6": "Alkalinity", "\\u77ff\\u6e23": "Slag", "\\u94a2\\u6e23": "Steel slag", "\\u8d64\\u6ce5": "Red mud", "\\u8131\\u786b\\u77f3\\u818f": "Desulfurization gypsum", "\\u6c61\\u6ce5": "Sludge", "\\u6c34\\u6ce5\\u7a91\\u7070": "Cement kiln dust", "\\u5c3e\\u77ff": "Tailings", "\\u751f\\u7269\\u8d28\\u7070": "Biomass ash", "\\u6280\\u672f\\u8def\\u5f84": "Valorization pathway", "\\u5e94\\u7528\\u573a\\u666f": "Application", "\\u8bc4\\u4ef7\\u6307\\u6807": "Evaluation indicator", "\\u539f\\u6599\\u7279\\u6027": "Feedstock property", "\\u534f\\u540c\\u56fa\\u5e9f": "Co-utilized solid waste", "\\u539f\\u6599": "Feedstock", "\\u76ee\\u6807\\u5143\\u7d20": "Target element", "\\u6c61\\u67d3\\u7269/\\u5bf9\\u8c61": "Pollutant/target", "\\u73af\\u5883\\u529f\\u80fd\\u6750\\u6599": "Environmental functional materials", "\\u9ad8\\u9644\\u52a0\\u503c\\u6750\\u6599": "High-value-added materials", "\\u5efa\\u6750\\u5229\\u7528": "Construction materials", "\\u5730\\u805a\\u7269\\u4e0e\\u78b1\\u6fc0\\u53d1\\u6750\\u6599": "Geopolymers and alkali-activated materials", "\\u5143\\u7d20\\u63d0\\u53d6": "Element extraction", "\\u80fd\\u6e90\\u4e0e\\u78b3\\u76f8\\u5173\\u5229\\u7528": "Energy- and carbon-related uses", "\\u751f\\u6001\\u4e0e\\u56de\\u586b\\u5229\\u7528": "Ecological and backfill uses", "\\u534f\\u540c\\u8d44\\u6e90\\u5316\\u5229\\u7528": "Collaborative valorization", "\\u73af\\u5883\\u5e94\\u7528": "Environmental applications", "\\u6c61\\u67d3\\u7269\\u53bb\\u9664": "Pollutant removal", "\\u5de5\\u7a0b\\u5e94\\u7528": "Engineering applications", "\\u751f\\u6001\\u5e94\\u7528": "Ecological applications", "\\u78b3\\u51cf\\u6392": "Carbon mitigation", "\\u73af\\u5883\\u6027\\u80fd": "Environmental performance", "\\u5de5\\u7a0b\\u6027\\u80fd": "Engineering performance", "\\u73af\\u5883\\u98ce\\u9669": "Environmental risk", "\\u8d44\\u6e90\\u56de\\u6536\\u6027\\u80fd": "Resource-recovery performance", "\\u73af\\u5883\\u7ee9\\u6548": "Environmental performance", "\\u8d44\\u6e90\\u6d88\\u8017": "Resource consumption", "\\u7ecf\\u6d4e\\u8bc4\\u4ef7": "Economic assessment", "\\u5de5\\u7a0b\\u7a33\\u5b9a\\u6027": "Engineering stability", "\\u5316\\u5b66\\u7ec4\\u6210": "Chemical composition", "\\u78b3\\u7ec4\\u5206": "Carbon fraction", "\\u5f62\\u8c8c\\u7ec4\\u5206": "Morphological component", "\\u7269\\u7406\\u6027\\u8d28": "Physical properties", "\\u77ff\\u7269\\u7ec4\\u6210": "Mineral composition", "\\u5316\\u5b66\\u6027\\u8d28": "Chemical properties", "\\u5de5\\u4e1a\\u56fa\\u5e9f": "Industrial solid waste", "\\u77ff\\u4e1a\\u56fa\\u5e9f": "Mining waste", "\\u7070\\u6e23\\u7c7b\\u56fa\\u5e9f": "Ash-related solid waste", "\\u5206\\u7c7b\\u5b57\\u6bb5": "Classification field", "\\u91cd\\u91d1\\u5c5e": "Heavy metals", "\\u67d3\\u6599": "Dyes", "\\u7a00\\u571f\\u5143\\u7d20": "Rare-earth elements", "\\u5173\\u952e\\u5143\\u7d20": "Critical elements", "\\u94dd/\\u6c27\\u5316\\u94dd": "Aluminum/alumina", "\\u9553": "Gallium", "\\u9502": "Lithium", "\\u57fa\\u7840\\u7814\\u7a76": "Basic research", "\\u5b9e\\u9a8c\\u5ba4\\u5236\\u5907": "Laboratory preparation", "\\u5de5\\u827a\\u4f18\\u5316": "Process optimization", "\\u5e94\\u7528\\u9a8c\\u8bc1": "Application validation", "\\u4e2d\\u8bd5/\\u5de5\\u7a0b\\u793a\\u8303": "Pilot/engineering demonstration", "\\u4ea7\\u4e1a\\u5316/\\u5546\\u4e1a\\u5316": "Industrial/commercial application", "\\u589e\\u5f3a\\u6c61\\u67d3\\u7269\\u53bb\\u9664": "Enhanced pollutant removal", "\\u63d0\\u9ad8\\u5f3a\\u5ea6/\\u8010\\u4e45\\u6027": "Improved strength/durability", "\\u6210\\u672c\\u4e0e\\u5e02\\u573a\\u9700\\u6c42": "Cost and market demand", "\\u964d\\u4f4e\\u91cd\\u91d1\\u5c5e\\u6d78\\u51fa": "Reduced heavy-metal leaching", "\\u6539\\u5584\\u5b54\\u7ed3\\u6784/\\u6bd4\\u8868\\u9762\\u79ef": "Improved pore structure/specific surface area", "\\u8865\\u5145Si-Al-Ca\\u7ec4\\u5206": "Supply of Si-Al-Ca components", "\\u4fc3\\u8fdb\\u80f6\\u51dd/\\u805a\\u5408\\u53cd\\u5e94": "Enhanced hydration/polymerization", "\\u4fc3\\u8fdb\\u70e7\\u7ed3/\\u7194\\u878d\\u6210\\u578b": "Enhanced sintering/melt forming", "\\u73af\\u5883\\u4fee\\u590d\\u9700\\u6c42": "Environmental remediation demand", "\\u4fc3\\u8fdb\\u78b3\\u9178\\u5316\\u56fa\\u5b9a": "Enhanced carbonation and sequestration", "\\u78b1\\u6fc0\\u53d1\\u5242": "Alkali activator", "\\u70ed\\u6d3b\\u5316/\\u70e7\\u7ed3": "Thermal activation/sintering", "\\u63d0\\u9ad8\\u5de5\\u7a0b\\u9002\\u914d\\u6027": "Improved engineering suitability", "\\u77ff\\u6e23/\\u94a2\\u6e23": "Slag/steel slag", "\\u6c34\\u6ce5\\u719f\\u6599/\\u77f3\\u7070": "Cement clinker/lime", "\\u78b3\\u51cf\\u6392/CO2\\u77ff\\u5316\\u9700\\u6c42": "Carbon mitigation/CO2 mineralization demand", "\\u964d\\u4f4e\\u80fd\\u8017\\u6216\\u6210\\u672c": "Reduced energy use or cost", "\\u653f\\u7b56/\\u6807\\u51c6\\u7ea6\\u675f": "Policy/standard constraints", "\\u8c03\\u8282\\u78b1\\u5ea6/pH": "Alkalinity/pH adjustment", "\\u4fc3\\u8fdb\\u6c34\\u5316/\\u805a\\u5408\\u53cd\\u5e94": "Enhanced hydration/polymerization", "\\u6539\\u5584\\u5b54\\u9699\\u7ed3\\u6784": "Improved pore structure", "\\u6210\\u672c\\u7ea6\\u675f": "Cost constraints", "\\u5de5\\u7a0b\\u5927\\u5b97\\u6d88\\u7eb3\\u9700\\u6c42": "Demand for large-scale engineering utilization", "\\u5e9f\\u73bb\\u7483": "Waste glass", "\\u9178/\\u78b1\\u6d17\\u9884\\u5904\\u7406": "Acid/alkali washing pretreatment"}')

TERM_TRANSLATIONS.update(json.loads('{"\\u5730\\u805a\\u7269\\u6df7\\u51dd\\u571f": "Geopolymer concrete", "\\u5730\\u805a\\u7269\\u7802\\u6d46": "Geopolymer mortar", "\\u9ad8\\u7ea7\\u6c27\\u5316/\\u50ac\\u5316\\u964d\\u89e3": "Advanced oxidation/catalytic degradation", "\\u7845\\u57fa\\u9ad8\\u503c\\u6750\\u6599": "High-value silicon-based materials", "\\u571f\\u5730\\u590d\\u57a6/\\u751f\\u6001\\u4fee\\u590d": "Land reclamation/ecological restoration", "\\u9553/\\u9517/\\u9502\\u7b49\\u6218\\u7565\\u91d1\\u5c5e": "Strategic metals (Ga/Ge/Li etc.)", "\\u52a0\\u6c14\\u6df7\\u51dd\\u571f": "Aerated concrete", "\\u77ff\\u5c71\\u56de\\u586b": "Mine backfilling", "\\u5ca9\\u571f\\u5de5\\u7a0b\\u5229\\u7528": "Geotechnical engineering applications"}'))
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'inputs';OUT=ROOT/'outputs'/'Code4 Author Review Audit'

def read(n):
    path=DATA/n
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        rdr=csv.DictReader(f);return rdr.fieldnames,list(rdr)

def key(row):return (row['Paper_ID'],row['Source'],row['Relation'],row['Target'])

def same_rows(actual,reference):
    columns=list(reference[0])
    ca=Counter(tuple((r.get(c,'') or '') for c in columns) for r in actual)
    cr=Counter(tuple((r.get(c,'') or '') for c in columns) for r in reference)
    if ca!=cr:
        raise ValueError(f'FULL-ROW mismatch: extra {(ca-cr).total()} missing {(cr-ca).total()}')

def dump(file,columns,rows):
    with file.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(rows)

# Author-review actions are audit labels; do not reinterpret the author's decisions.
ACTION_ENGLISH = json.loads('{"\\u4fdd\\u7559\\u539f\\u5173\\u7cfb": "Original relation retained", "\\u4fdd\\u7559\\u539f\\u5173\\u7cfb\\uff1b\\u5206\\u7c7b\\u540c\\u6b65": "Original relation retained; category synchronized", "\\u4f5c\\u8005\\u786e\\u8ba4\\u66f4\\u6b63\\u65b9\\u5411\\uff1b\\u5df2\\u6620\\u5c04\\u65e2\\u6709\\u6807\\u51c6\\u5b9e\\u4f53\\uff08\\u5f85\\u518d\\u6b21\\u6838\\u67e5\\u5168\\u6587\\uff09": "Author-confirmed correction direction; mapped to existing canonical entity (full-text verification pending)"}')

def has_cjk(value):
    return bool(re.search(r'[\u3400-\u9fff]',str(value)))

def english_action(value):
    if value in ACTION_ENGLISH:return ACTION_ENGLISH[value]
    if not has_cjk(value):return value
    raise ValueError('Unmapped author-action label; approval required to translate it.')

def approved_label(value):
    translated=TERM_TRANSLATIONS.get(value,value)
    if has_cjk(translated):
        raise ValueError('Unmapped entity, type, or pathway label; no silent relabeling is allowed.')
    return translated

def source_row_hash(row,columns):
    payload=json.dumps([row.get(x,'') or '' for x in columns],ensure_ascii=False,separators=(',',':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def checked_english_dump(path,columns,rows):
    if any(has_cjk(value) for row in rows for value in row.values()):
        raise ValueError('Untranslated characters in the intended English audit output')
    dump(path,columns,rows)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    _,v2=read('V2 Author Approved Graph 21269.csv')
    v3_cols,v3=read('V3 Author Revised Graph 21204.csv')
    cols3422,ref3422=read('V3 3422 Papers 20858 Relations.csv')
    _,removed=read('Author Confirmed Exclusions 42 Papers.csv')
    finalcols,final=read('Final Graph Triples 19177.csv')
    _,papers=read('Author Frozen Corpus 3075.csv')
    _,edges=read('Input1 Knowledge Graph Edges 198.csv')
    assert len(v2)==21269 and len(v3)==21204 and len(removed)==42
    eids={r['Paper_ID'] for r in removed};assert len(eids)==42
    held=[r for r in v3 if r.get('V3_Action','').startswith('\u4f5c\u8005\u786e\u8ba4\u66f4\u6b63\u65b9\u5411')]
    assert len(held)==5
    after42=[r for r in v3 if r['Paper_ID'] not in eids]
    afterheld=[r for r in after42 if not r.get('V3_Action','').startswith('\u4f5c\u8005\u786e\u8ba4\u66f4\u6b63\u65b9\u5411')]
    assert len(after42)==20863 and len(afterheld)==20858
    same_rows(afterheld,ref3422)
    kept_ids={r['Paper_ID'] for r in papers}
    kept=[r for r in afterheld if r['Paper_ID'] in kept_ids]
    same_rows(kept,final)
    assert len(papers)==3075 and len(kept)==19177
    calc=Counter((
        TERM_TRANSLATIONS.get(r['Source'], r['Source']),
        TERM_TRANSLATIONS.get(r['Relation'], r['Relation']),
        TERM_TRANSLATIONS.get(r['Target'], r['Target'])
    ) for r in kept)
    saved={(r['Source'],r['Relation'],r['Target']):int(r['Weight']) for r in edges}
    assert len(calc)==198 and calc==saved
    # Report V2/V3 author-approved changes without assuming candidate keys are all valid.
    v2keys=Counter(key(r) for r in v2);v3keys=Counter(key(r) for r in v3)
    actions=Counter(english_action(r.get('V3_Action','')) for r in v3)
    report={'V2_approved':len(v2),'V3_after_author_revision':len(v3),
        'V2_only_relation_keys':sum((v2keys-v3keys).values()),
        'V3_only_relation_keys':sum((v3keys-v2keys).values()),
        'V3_action_counts':dict(actions),'author_scope_excluded_papers':42,
        'V3_after_scope_exclusions':len(after42),'five_held_candidate_relations':len(held),
        'V3_after_holding_candidates':len(afterheld),'outside_window_relation_supports':len(afterheld)-len(kept),
        'final_papers':len(papers),'final_relations':len(final),'final_edges':len(calc),
        'full_row_equality_to_frozen':True,'edge_weight_equality':True,
        'caution':'Replays recorded decisions; does NOT reconstruct or authenticate unrecorded human judgments.'}
    # Export an English relational index rather than silently translating free-text
    # evidence, author comments, and non-English bibliographic titles. The exact
    # unmodified 21-column inputs have already been checked by same_rows().
    # Source_Row_SHA256 lets authorized reviewers trace each row back to the
    # original full record without publishing author notes or copyrighted text.
    index_cols=['Paper_ID','Year','Source','Relation','Target','Source_Type',
                'Target_Type','Primary_Category','Subroute','Confidence','Need_Check',
                'V3_Action_EN','Source_Row_SHA256']
    def to_index(row):
        values={x:approved_label(row.get(x,'') or '') for x in index_cols[:11]}
        values['V3_Action_EN']=english_action(row.get('V3_Action','') or '')
        values['Source_Row_SHA256']=source_row_hash(row,finalcols)
        return values
    english_held=[to_index(r) for r in held]
    checked_english_dump(OUT/'V3 Held Candidate Relation Index 5.csv',
                         index_cols,english_held)
    english_kept=[to_index(r) for r in kept]
    checked_english_dump(OUT/'Final Reviewed Relation Index 3075 Papers.csv',
                         index_cols,english_kept)
    report['english_export_scope']='English relational indexes and row hashes only; original titles, evidence texts, and review notes remain private and unchanged.'
    report['original_full_row_semantics']='Frozen full-row equality checked before any English presentation conversion.'
    (OUT/'V2 V3 Audit Trail.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='V3_action_counts'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
