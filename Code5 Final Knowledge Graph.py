#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WM-26-2894 | final paper-linked knowledge-graph deterministic aggregation.

Input is a *frozen author-corrected* 2000–2025 corpus and triple-support table.
This script validates ID links, publication year, unique supports, recomputes
weighted directed edges, nodes, relation reports, and optionally GraphML.

This does NOT create V2/V3 review decisions or independently verify semantics.

Run:
  python "Code5 Final Knowledge Graph.py" \
    --papers inputs/Author Frozen Corpus 3075.csv \
    --triples inputs/Final Graph Triples 19177.csv \
    --compare-edges inputs/Input1 Knowledge Graph Edges 198.csv --strict
"""
import argparse,csv,json,collections,hashlib,sys,re
from pathlib import Path

TERM_TRANSLATIONS = json.loads('{"\\u7c89\\u7164\\u7070": "Coal fly ash", "\\u5236\\u5907": "produces", "\\u7528\\u4e8e": "is used for", "\\u8bc4\\u4ef7": "is evaluated by", "\\u53bb\\u9664": "removes", "\\u56de\\u6536": "recovers", "\\u534f\\u540c": "co-processes", "\\u5173\\u8054": "is associated with", "\\u5305\\u542b": "includes", "\\u5438\\u9644\\u6750\\u6599": "Adsorbents", "\\u6cb8\\u77f3/\\u5206\\u5b50\\u7b5b": "Zeolites/molecular sieves", "\\u5e9f\\u6c34\\u5904\\u7406\\u6750\\u6599": "Wastewater-treatment materials", "\\u6c34\\u6ce5/\\u6df7\\u51dd\\u571f/\\u7802\\u6d46": "Cement/concrete/mortar", "\\u5730\\u805a\\u7269\\u6750\\u6599": "Geopolymer materials", "\\u78b1\\u6fc0\\u53d1\\u6750\\u6599": "Alkali-activated materials", "\\u9676\\u74f7/\\u73bb\\u7483\\u9676\\u74f7": "Ceramics/glass-ceramics", "\\u7a00\\u571f/\\u5173\\u952e\\u5143\\u7d20\\u56de\\u6536": "Rare-earth/critical-element recovery", "\\u94dd/\\u6c27\\u5316\\u94dd\\u63d0\\u53d6": "Aluminum/alumina extraction", "\\u91d1\\u5c5e\\u56de\\u6536": "Metal recovery", "\\u78b3\\u6750\\u6599": "Carbon materials", "\\u78b3\\u6355\\u96c6/\\u77ff\\u5316\\u5c01\\u5b58": "Carbon capture/mineral carbonation", "\\u571f\\u58e4\\u6539\\u826f/\\u7a33\\u5b9a\\u5316": "Soil amendment/stabilization", "\\u9aa8\\u6599/\\u8def\\u57fa/\\u9053\\u8def\\u6750\\u6599": "Aggregates/road-base materials", "\\u7816/\\u70e7\\u7ed3\\u5236\\u54c1": "Bricks/sintered products", "\\u50ac\\u5316/\\u5149\\u50ac\\u5316\\u6750\\u6599": "Catalytic/photocatalytic materials", "\\u529f\\u80fd\\u586b\\u6599/\\u590d\\u5408\\u6750\\u6599": "Functional fillers/composites", "\\u7a7a\\u5fc3\\u5fae\\u73e0": "Cenospheres", "\\u672a\\u71c3\\u78b3\\u56de\\u6536/\\u6d6e\\u9009": "Unburned-carbon recovery/flotation", "\\u591a\\u56fa\\u5e9f\\u534f\\u540c": "Multi-solid-waste co-utilization", "\\u5e9f\\u6c34\\u5904\\u7406": "Wastewater treatment", "\\u91cd\\u91d1\\u5c5e\\u53bb\\u9664": "Heavy-metal removal", "\\u67d3\\u6599\\u5438\\u9644": "Dye adsorption", "\\u5efa\\u7b51\\u6750\\u6599": "Building materials", "\\u9053\\u8def\\u5de5\\u7a0b": "Road engineering", "\\u751f\\u6001\\u4fee\\u590d": "Ecological restoration", "CO2\\u51cf\\u6392": "CO2 mitigation", "\\u8d44\\u6e90\\u56de\\u6536": "Resource recovery", "\\u5438\\u9644\\u5bb9\\u91cf": "Adsorption capacity", "\\u53bb\\u9664\\u7387": "Removal efficiency", "\\u6297\\u538b\\u5f3a\\u5ea6": "Compressive strength", "\\u6d78\\u51fa\\u6bd2\\u6027": "Leaching toxicity", "\\u56de\\u6536\\u7387": "Recovery rate", "\\u78b3\\u6392\\u653e": "Carbon emissions", "\\u80fd\\u8017": "Energy consumption", "\\u7269\\u8017": "Material consumption", "\\u7ecf\\u6d4e\\u6027": "Economic performance", "\\u7a33\\u5b9a\\u6027": "Stability", "SiO2/Al2O3": "SiO2/Al2O3", "CaO": "CaO", "Fe2O3": "Fe2O3", "\\u672a\\u71c3\\u78b3": "Unburned carbon", "\\u91cd\\u91d1\\u5c5e\\u6d78\\u51fa\\u98ce\\u9669": "Heavy-metal leaching risk", "\\u7c92\\u5f84/\\u7ec6\\u5ea6": "Particle size/fineness", "\\u77ff\\u7269\\u76f8": "Mineral phases", "\\u78b1\\u5ea6": "Alkalinity", "\\u77ff\\u6e23": "Slag", "\\u94a2\\u6e23": "Steel slag", "\\u8d64\\u6ce5": "Red mud", "\\u8131\\u786b\\u77f3\\u818f": "Desulfurization gypsum", "\\u6c61\\u6ce5": "Sludge", "\\u6c34\\u6ce5\\u7a91\\u7070": "Cement kiln dust", "\\u5c3e\\u77ff": "Tailings", "\\u751f\\u7269\\u8d28\\u7070": "Biomass ash", "\\u6280\\u672f\\u8def\\u5f84": "Valorization pathway", "\\u5e94\\u7528\\u573a\\u666f": "Application", "\\u8bc4\\u4ef7\\u6307\\u6807": "Evaluation indicator", "\\u539f\\u6599\\u7279\\u6027": "Feedstock property", "\\u534f\\u540c\\u56fa\\u5e9f": "Co-utilized solid waste", "\\u539f\\u6599": "Feedstock", "\\u76ee\\u6807\\u5143\\u7d20": "Target element", "\\u6c61\\u67d3\\u7269/\\u5bf9\\u8c61": "Pollutant/target", "\\u73af\\u5883\\u529f\\u80fd\\u6750\\u6599": "Environmental functional materials", "\\u9ad8\\u9644\\u52a0\\u503c\\u6750\\u6599": "High-value-added materials", "\\u5efa\\u6750\\u5229\\u7528": "Construction materials", "\\u5730\\u805a\\u7269\\u4e0e\\u78b1\\u6fc0\\u53d1\\u6750\\u6599": "Geopolymers and alkali-activated materials", "\\u5143\\u7d20\\u63d0\\u53d6": "Element extraction", "\\u80fd\\u6e90\\u4e0e\\u78b3\\u76f8\\u5173\\u5229\\u7528": "Energy- and carbon-related uses", "\\u751f\\u6001\\u4e0e\\u56de\\u586b\\u5229\\u7528": "Ecological and backfill uses", "\\u534f\\u540c\\u8d44\\u6e90\\u5316\\u5229\\u7528": "Collaborative valorization", "\\u73af\\u5883\\u5e94\\u7528": "Environmental applications", "\\u6c61\\u67d3\\u7269\\u53bb\\u9664": "Pollutant removal", "\\u5de5\\u7a0b\\u5e94\\u7528": "Engineering applications", "\\u751f\\u6001\\u5e94\\u7528": "Ecological applications", "\\u78b3\\u51cf\\u6392": "Carbon mitigation", "\\u73af\\u5883\\u6027\\u80fd": "Environmental performance", "\\u5de5\\u7a0b\\u6027\\u80fd": "Engineering performance", "\\u73af\\u5883\\u98ce\\u9669": "Environmental risk", "\\u8d44\\u6e90\\u56de\\u6536\\u6027\\u80fd": "Resource-recovery performance", "\\u73af\\u5883\\u7ee9\\u6548": "Environmental performance", "\\u8d44\\u6e90\\u6d88\\u8017": "Resource consumption", "\\u7ecf\\u6d4e\\u8bc4\\u4ef7": "Economic assessment", "\\u5de5\\u7a0b\\u7a33\\u5b9a\\u6027": "Engineering stability", "\\u5316\\u5b66\\u7ec4\\u6210": "Chemical composition", "\\u78b3\\u7ec4\\u5206": "Carbon fraction", "\\u5f62\\u8c8c\\u7ec4\\u5206": "Morphological component", "\\u7269\\u7406\\u6027\\u8d28": "Physical properties", "\\u77ff\\u7269\\u7ec4\\u6210": "Mineral composition", "\\u5316\\u5b66\\u6027\\u8d28": "Chemical properties", "\\u5de5\\u4e1a\\u56fa\\u5e9f": "Industrial solid waste", "\\u77ff\\u4e1a\\u56fa\\u5e9f": "Mining waste", "\\u7070\\u6e23\\u7c7b\\u56fa\\u5e9f": "Ash-related solid waste", "\\u5206\\u7c7b\\u5b57\\u6bb5": "Classification field", "\\u91cd\\u91d1\\u5c5e": "Heavy metals", "\\u67d3\\u6599": "Dyes", "\\u7a00\\u571f\\u5143\\u7d20": "Rare-earth elements", "\\u5173\\u952e\\u5143\\u7d20": "Critical elements", "\\u94dd/\\u6c27\\u5316\\u94dd": "Aluminum/alumina", "\\u9553": "Gallium", "\\u9502": "Lithium", "\\u57fa\\u7840\\u7814\\u7a76": "Basic research", "\\u5b9e\\u9a8c\\u5ba4\\u5236\\u5907": "Laboratory preparation", "\\u5de5\\u827a\\u4f18\\u5316": "Process optimization", "\\u5e94\\u7528\\u9a8c\\u8bc1": "Application validation", "\\u4e2d\\u8bd5/\\u5de5\\u7a0b\\u793a\\u8303": "Pilot/engineering demonstration", "\\u4ea7\\u4e1a\\u5316/\\u5546\\u4e1a\\u5316": "Industrial/commercial application", "\\u589e\\u5f3a\\u6c61\\u67d3\\u7269\\u53bb\\u9664": "Enhanced pollutant removal", "\\u63d0\\u9ad8\\u5f3a\\u5ea6/\\u8010\\u4e45\\u6027": "Improved strength/durability", "\\u6210\\u672c\\u4e0e\\u5e02\\u573a\\u9700\\u6c42": "Cost and market demand", "\\u964d\\u4f4e\\u91cd\\u91d1\\u5c5e\\u6d78\\u51fa": "Reduced heavy-metal leaching", "\\u6539\\u5584\\u5b54\\u7ed3\\u6784/\\u6bd4\\u8868\\u9762\\u79ef": "Improved pore structure/specific surface area", "\\u8865\\u5145Si-Al-Ca\\u7ec4\\u5206": "Supply of Si-Al-Ca components", "\\u4fc3\\u8fdb\\u80f6\\u51dd/\\u805a\\u5408\\u53cd\\u5e94": "Enhanced hydration/polymerization", "\\u4fc3\\u8fdb\\u70e7\\u7ed3/\\u7194\\u878d\\u6210\\u578b": "Enhanced sintering/melt forming", "\\u73af\\u5883\\u4fee\\u590d\\u9700\\u6c42": "Environmental remediation demand", "\\u4fc3\\u8fdb\\u78b3\\u9178\\u5316\\u56fa\\u5b9a": "Enhanced carbonation and sequestration", "\\u78b1\\u6fc0\\u53d1\\u5242": "Alkali activator", "\\u70ed\\u6d3b\\u5316/\\u70e7\\u7ed3": "Thermal activation/sintering", "\\u63d0\\u9ad8\\u5de5\\u7a0b\\u9002\\u914d\\u6027": "Improved engineering suitability", "\\u77ff\\u6e23/\\u94a2\\u6e23": "Slag/steel slag", "\\u6c34\\u6ce5\\u719f\\u6599/\\u77f3\\u7070": "Cement clinker/lime", "\\u78b3\\u51cf\\u6392/CO2\\u77ff\\u5316\\u9700\\u6c42": "Carbon mitigation/CO2 mineralization demand", "\\u964d\\u4f4e\\u80fd\\u8017\\u6216\\u6210\\u672c": "Reduced energy use or cost", "\\u653f\\u7b56/\\u6807\\u51c6\\u7ea6\\u675f": "Policy/standard constraints", "\\u8c03\\u8282\\u78b1\\u5ea6/pH": "Alkalinity/pH adjustment", "\\u4fc3\\u8fdb\\u6c34\\u5316/\\u805a\\u5408\\u53cd\\u5e94": "Enhanced hydration/polymerization", "\\u6539\\u5584\\u5b54\\u9699\\u7ed3\\u6784": "Improved pore structure", "\\u6210\\u672c\\u7ea6\\u675f": "Cost constraints", "\\u5de5\\u7a0b\\u5927\\u5b97\\u6d88\\u7eb3\\u9700\\u6c42": "Demand for large-scale engineering utilization", "\\u5e9f\\u73bb\\u7483": "Waste glass", "\\u9178/\\u78b1\\u6d17\\u9884\\u5904\\u7406": "Acid/alkali washing pretreatment"}')

PAPER_ID=('Paper_ID','Paper ID','paper_id','ID')
YEAR=('Year','Year_clean','Publication Year','year')
SRC=('Source','Source_Entity','source')
REL=('Relation','Predicate','relation')
DST=('Target','Target_Entity','target')
SW=('Weight','weight','Triple_Count','Support_Count')

def load(path):
    with open(path,'r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames:raise ValueError(f'Empty header: {path}')
        rows=[{(k or '').strip(): str(v or '').strip() for k,v in row.items()} for row in reader]
    return rows

def field(rows,aliases,path):
    if not rows:raise ValueError(f'Empty input file {path}')
    for v in aliases:
        if v in rows[0]:return v
    raise ValueError(f'Missing one of columns {aliases} in {path}: {list(rows[0])}')

def write(path,records,columns):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(records)

def weight_num(x):
    try: return int(float(x))
    except ValueError:return -1

def audit(papers,triples,expected_edges=None,strict=False):
    pk=field(papers,PAPER_ID,'papers');yk=field(papers,YEAR,'papers')
    tk=field(triples,PAPER_ID,'triples');sk=field(triples,SRC,'triples');rk=field(triples,REL,'triples');dk=field(triples,DST,'triples')
    pids=[r[pk] for r in papers]
    if len(set(pids))!=len(pids):raise ValueError('Duplicate Paper_ID within frozen corpus')
    if not all(2000<=int(r[yk])<=2025 for r in papers if r[yk].isdigit()):
        raise ValueError('Publication year outside 2000–2025 detected')
    if any(not r[yk].isdigit() for r in papers):raise ValueError('Missing/non-numeric Year in final corpus')
    ps=set(pids)
    orphan=[r[tk] for r in triples if r[tk] not in ps]
    if orphan:raise ValueError(f'{len(orphan)} triples reference excluded Paper_IDs, examples: {orphan[:5]}')
    key_set=set();duplicates=[]; edges=collections.defaultdict(set); relation_counts=collections.Counter()
    node_stat=collections.Counter();node_types=collections.defaultdict(collections.Counter)
    fromclass=('Source_Type','SourceType');toclass=('Target_Type','TargetType')
    source_type=next((v for v in fromclass if v in triples[0]),None)
    target_type=next((v for v in toclass if v in triples[0]),None)
    for r in triples:
        p=r[tk];raw_src=r[sk];raw_rel=r[rk];raw_tar=r[dk]
        if not raw_src or not raw_rel or not raw_tar:raise ValueError(f'Empty graph relation in record {r}')
        key=(p,raw_src,raw_rel,raw_tar)
        if key in key_set:duplicates.append(key)
        key_set.add(key)
        src=TERM_TRANSLATIONS.get(raw_src,raw_src)
        rel=TERM_TRANSLATIONS.get(raw_rel,raw_rel)
        tar=TERM_TRANSLATIONS.get(raw_tar,raw_tar)
        edges[(src,rel,tar)].add(p)
        relation_counts[rel]+=1
        node_stat[src]+=1;node_stat[tar]+=1
        if source_type and r[source_type]:
            node_types[src][TERM_TRANSLATIONS.get(r[source_type],r[source_type])]+=1
        if target_type and r[target_type]:
            node_types[tar][TERM_TRANSLATIONS.get(r[target_type],r[target_type])]+=1
    if duplicates:raise ValueError(f'{len(duplicates)} duplicate paper-linked (Paper_ID,Source,Relation,Target) keys; review dedup logic first. Example {duplicates[:2]}')
    edge_rows=[{'Source':a,'Relation':b,'Target':c,'Weight':len(ids),'Paper_Count':len(ids)}
             for (a,b,c),ids in edges.items()]
    edge_rows.sort(key=lambda r:(-r['Weight'],r['Source'],r['Relation'],r['Target']))
    node_rows=[{'Node':n,'Frequency':f,'Node_Type':(node_types[n].most_common(1)[0][0] if node_types[n] else '')}
               for n,f in node_stat.items()]
    node_rows.sort(key=lambda r:(-r['Frequency'],r['Node']))
    rel_rows=[{'Relation':k,'Support_Instances':v,'Unique_Source_Papers':len({r[tk] for r in triples if TERM_TRANSLATIONS.get(r[rk],r[rk])==k})}
              for k,v in sorted(relation_counts.items(),key=lambda t:-t[1])]
    for collection_name, collection in (('edges', edge_rows), ('nodes', node_rows), ('relations', rel_rows)):
        for record in collection:
            for column, value in record.items():
                if isinstance(value, str) and re.search(r'[\u3400-\u9fff]', value):
                    raise ValueError(
                        f'Chinese text remains in generated {collection_name} field {column!r}: {value!r}. '
                        'Add an approved English equivalent to TERM_TRANSLATIONS.'
                    )
    if expected_edges:
        ek=field(expected_edges,SRC,'expected edges');rk_e=field(expected_edges,REL,'expected edges');dk_e=field(expected_edges,DST,'expected edges')
        wk=field(expected_edges,SW,'expected edges')
        expected={(r[ek],r[rk_e],r[dk_e]):weight_num(r[wk]) for r in expected_edges}
        calculated={(r['Source'],r['Relation'],r['Target']):r['Weight'] for r in edge_rows}
        if expected!=calculated:
            missing=set(expected)-set(calculated);added=set(calculated)-set(expected)
            differing=[(k,expected[k],calculated[k]) for k in expected.keys()&calculated.keys() if expected[k]!=calculated[k]]
            raise ValueError(f'Frozen edge comparison FAILED; missing={list(missing)[:4]}, new={list(added)[:4]}, weight_differences={differing[:5]}')
    status={'papers':len(papers),'papers_with_supports':len({r[tk] for r in triples}),
            'paper_linked_relation_supports':len(triples),'distinct_aggregate_edges':len(edge_rows),
            'weight_sum':sum(x['Weight'] for x in edge_rows),'nodes':len(node_rows),
            'publication_period':'2000-2025','edge_comparison': 'matched' if expected_edges else 'not_provided',
            'scope':'Data and weight validation, NOT independent relation-level scientific precision assessment'}
    if strict and (status['papers'],status['paper_linked_relation_supports'],status['distinct_aggregate_edges'])!=(3075,19177,198):
        raise ValueError(f'STRICT FROZEN COUNTS FAILED: actual = {status}; expected papers=3075 supports=19177 aggregate_edges=198')
    return edge_rows,node_rows,rel_rows,status

def main():
    pa=argparse.ArgumentParser();pa.add_argument('--papers',default=str(Path(__file__).resolve().parent/'inputs'/'Author Frozen Corpus 3075.csv'));pa.add_argument('--triples',default=str(Path(__file__).resolve().parent/'inputs'/'Final Graph Triples 19177.csv'))
    pa.add_argument('--compare-edges',default=str(Path(__file__).resolve().parent/'inputs'/'Input1 Knowledge Graph Edges 198.csv'));pa.add_argument('--out',default=str(Path(__file__).resolve().parent/'outputs'/'Code5 Final Knowledge Graph'));pa.add_argument('--no-strict',dest='strict',action='store_false',help='Disable the frozen-count check for exploratory inputs.');pa.set_defaults(strict=True);arg=pa.parse_args()
    papers=load(arg.papers);tri=load(arg.triples)
    comp=load(arg.compare_edges) if arg.compare_edges else None
    edges,nodes,rels,stats=audit(papers,tri,comp,strict=arg.strict)
    dest=Path(arg.out);dest.mkdir(parents=True,exist_ok=True)
    write(dest/'KG 3075 Edges Recomputed.csv',edges,['Source','Relation','Target','Weight','Paper_Count'])
    write(dest/'KG 3075 Nodes Recomputed.csv',nodes,['Node','Frequency','Node_Type'])
    write(dest/'KG 3075 Relation Stats.csv',rels,['Relation','Support_Instances','Unique_Source_Papers'])
    stats['inputs_sha256']={x:hashlib.sha256(Path(x).read_bytes()).hexdigest() for x in [arg.papers,arg.triples]+([arg.compare_edges] if arg.compare_edges else [])}
    (dest/'Audit 3075.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
    try:
        import networkx as nx
        # Use MultiDiGraph so parallel relations between the same nodes are retained.
        multidigraph=nx.MultiDiGraph()
        for n in nodes:multidigraph.add_node(n['Node'],Frequency=n['Frequency'],node_type=n['Node_Type'])
        for e in edges:multidigraph.add_edge(e['Source'],e['Target'],key=e['Relation'],weight=e['Weight'],relation=e['Relation'])
        nx.write_graphml(multidigraph,dest/'Knowledge Graph 3075 Multirelational.graphml')
    except ImportError:
        print('networkx not installed; graphml omitted. CSV & audit are complete.')
    print(json.dumps(stats,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
