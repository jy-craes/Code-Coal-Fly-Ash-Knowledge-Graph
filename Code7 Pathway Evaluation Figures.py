#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Summarize valorization pathways and maturity in the frozen 3,075-paper corpus.
Reproduce selected statistical figures from Figs. 2 and 3.
Research heat and evidence-reporting frequency are bibliographic proxies, not
industrial consumption, cost, or measured engineering performance.
"""
from pathlib import Path
from collections import Counter
import csv,math,json,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
DATA=HERE/'inputs'
OUT=HERE/'outputs'/'Code7 Pathway Evaluation Figures'
OUT.mkdir(parents=True,exist_ok=True)

TERM_TRANSLATIONS = json.loads(r'''{"\u7c89\u7164\u7070":"Coal fly ash","\u5236\u5907":"produces","\u7528\u4e8e":"is used for","\u8bc4\u4ef7":"is evaluated by","\u53bb\u9664":"removes","\u56de\u6536":"recovers","\u534f\u540c":"co-processes","\u5173\u8054":"is associated with","\u5305\u542b":"includes","\u5438\u9644\u6750\u6599":"Adsorbents","\u6cb8\u77f3/\u5206\u5b50\u7b5b":"Zeolites/molecular sieves","\u5e9f\u6c34\u5904\u7406\u6750\u6599":"Wastewater-treatment materials","\u6c34\u6ce5/\u6df7\u51dd\u571f/\u7802\u6d46":"Cement/concrete/mortar","\u5730\u805a\u7269\u6750\u6599":"Geopolymer materials","\u78b1\u6fc0\u53d1\u6750\u6599":"Alkali-activated materials","\u9676\u74f7/\u73bb\u7483\u9676\u74f7":"Ceramics/glass-ceramics","\u7a00\u571f/\u5173\u952e\u5143\u7d20\u56de\u6536":"Rare-earth/critical-element recovery","\u94dd/\u6c27\u5316\u94dd\u63d0\u53d6":"Aluminum/alumina extraction","\u91d1\u5c5e\u56de\u6536":"Metal recovery","\u78b3\u6750\u6599":"Carbon materials","\u78b3\u6355\u96c6/\u77ff\u5316\u5c01\u5b58":"Carbon capture/mineral carbonation","\u571f\u58e4\u6539\u826f/\u7a33\u5b9a\u5316":"Soil amendment/stabilization","\u9aa8\u6599/\u8def\u57fa/\u9053\u8def\u6750\u6599":"Aggregates/road-base materials","\u7816/\u70e7\u7ed3\u5236\u54c1":"Bricks/sintered products","\u50ac\u5316/\u5149\u50ac\u5316\u6750\u6599":"Catalytic/photocatalytic materials","\u529f\u80fd\u586b\u6599/\u590d\u5408\u6750\u6599":"Functional fillers/composites","\u7a7a\u5fc3\u5fae\u73e0":"Cenospheres","\u672a\u71c3\u78b3\u56de\u6536/\u6d6e\u9009":"Unburned-carbon recovery/flotation","\u591a\u56fa\u5e9f\u534f\u540c":"Multi-solid-waste co-utilization","\u5e9f\u6c34\u5904\u7406":"Wastewater treatment","\u91cd\u91d1\u5c5e\u53bb\u9664":"Heavy-metal removal","\u67d3\u6599\u5438\u9644":"Dye adsorption","\u5efa\u7b51\u6750\u6599":"Building materials","\u9053\u8def\u5de5\u7a0b":"Road engineering","\u751f\u6001\u4fee\u590d":"Ecological restoration","CO2\u51cf\u6392":"CO2 mitigation","\u8d44\u6e90\u56de\u6536":"Resource recovery","\u5438\u9644\u5bb9\u91cf":"Adsorption capacity","\u53bb\u9664\u7387":"Removal efficiency","\u6297\u538b\u5f3a\u5ea6":"Compressive strength","\u6d78\u51fa\u6bd2\u6027":"Leaching toxicity","\u56de\u6536\u7387":"Recovery rate","\u78b3\u6392\u653e":"Carbon emissions","\u80fd\u8017":"Energy consumption","\u7269\u8017":"Material consumption","\u7ecf\u6d4e\u6027":"Economic performance","\u7a33\u5b9a\u6027":"Stability","SiO2/Al2O3":"SiO2/Al2O3","CaO":"CaO","Fe2O3":"Fe2O3","\u672a\u71c3\u78b3":"Unburned carbon","\u91cd\u91d1\u5c5e\u6d78\u51fa\u98ce\u9669":"Heavy-metal leaching risk","\u7c92\u5f84/\u7ec6\u5ea6":"Particle size/fineness","\u77ff\u7269\u76f8":"Mineral phases","\u78b1\u5ea6":"Alkalinity","\u77ff\u6e23":"Slag","\u94a2\u6e23":"Steel slag","\u8d64\u6ce5":"Red mud","\u8131\u786b\u77f3\u818f":"Desulfurization gypsum","\u6c61\u6ce5":"Sludge","\u6c34\u6ce5\u7a91\u7070":"Cement kiln dust","\u5c3e\u77ff":"Tailings","\u751f\u7269\u8d28\u7070":"Biomass ash","\u6280\u672f\u8def\u5f84":"Valorization pathway","\u5e94\u7528\u573a\u666f":"Application","\u8bc4\u4ef7\u6307\u6807":"Evaluation indicator","\u539f\u6599\u7279\u6027":"Feedstock property","\u534f\u540c\u56fa\u5e9f":"Co-utilized solid waste","\u539f\u6599":"Feedstock","\u76ee\u6807\u5143\u7d20":"Target element","\u6c61\u67d3\u7269/\u5bf9\u8c61":"Pollutant/target","\u73af\u5883\u529f\u80fd\u6750\u6599":"Environmental functional materials","\u9ad8\u9644\u52a0\u503c\u6750\u6599":"High-value-added materials","\u5efa\u6750\u5229\u7528":"Construction materials","\u5730\u805a\u7269\u4e0e\u78b1\u6fc0\u53d1\u6750\u6599":"Geopolymers and alkali-activated materials","\u5143\u7d20\u63d0\u53d6":"Element extraction","\u80fd\u6e90\u4e0e\u78b3\u76f8\u5173\u5229\u7528":"Energy- and carbon-related uses","\u751f\u6001\u4e0e\u56de\u586b\u5229\u7528":"Ecological and backfill uses","\u534f\u540c\u8d44\u6e90\u5316\u5229\u7528":"Collaborative valorization","\u73af\u5883\u5e94\u7528":"Environmental applications","\u6c61\u67d3\u7269\u53bb\u9664":"Pollutant removal","\u5de5\u7a0b\u5e94\u7528":"Engineering applications","\u751f\u6001\u5e94\u7528":"Ecological applications","\u78b3\u51cf\u6392":"Carbon mitigation","\u73af\u5883\u6027\u80fd":"Environmental performance","\u5de5\u7a0b\u6027\u80fd":"Engineering performance","\u73af\u5883\u98ce\u9669":"Environmental risk","\u8d44\u6e90\u56de\u6536\u6027\u80fd":"Resource-recovery performance","\u73af\u5883\u7ee9\u6548":"Environmental performance","\u8d44\u6e90\u6d88\u8017":"Resource consumption","\u7ecf\u6d4e\u8bc4\u4ef7":"Economic assessment","\u5de5\u7a0b\u7a33\u5b9a\u6027":"Engineering stability","\u5316\u5b66\u7ec4\u6210":"Chemical composition","\u78b3\u7ec4\u5206":"Carbon fraction","\u5f62\u8c8c\u7ec4\u5206":"Morphological component","\u7269\u7406\u6027\u8d28":"Physical properties","\u77ff\u7269\u7ec4\u6210":"Mineral composition","\u5316\u5b66\u6027\u8d28":"Chemical properties","\u5de5\u4e1a\u56fa\u5e9f":"Industrial solid waste","\u77ff\u4e1a\u56fa\u5e9f":"Mining waste","\u7070\u6e23\u7c7b\u56fa\u5e9f":"Ash-related solid waste","\u5206\u7c7b\u5b57\u6bb5":"Classification field","\u91cd\u91d1\u5c5e":"Heavy metals","\u67d3\u6599":"Dyes","\u7a00\u571f\u5143\u7d20":"Rare-earth elements","\u5173\u952e\u5143\u7d20":"Critical elements","\u94dd/\u6c27\u5316\u94dd":"Aluminum/alumina","\u9553":"Gallium","\u9502":"Lithium","\u57fa\u7840\u7814\u7a76":"Basic research","\u5b9e\u9a8c\u5ba4\u5236\u5907":"Laboratory preparation","\u5de5\u827a\u4f18\u5316":"Process optimization","\u5e94\u7528\u9a8c\u8bc1":"Application validation","\u4e2d\u8bd5/\u5de5\u7a0b\u793a\u8303":"Pilot/engineering demonstration","\u4ea7\u4e1a\u5316/\u5546\u4e1a\u5316":"Industrial/commercial application","\u589e\u5f3a\u6c61\u67d3\u7269\u53bb\u9664":"Enhanced pollutant removal","\u63d0\u9ad8\u5f3a\u5ea6/\u8010\u4e45\u6027":"Improved strength/durability","\u6210\u672c\u4e0e\u5e02\u573a\u9700\u6c42":"Cost and market demand","\u964d\u4f4e\u91cd\u91d1\u5c5e\u6d78\u51fa":"Reduced heavy-metal leaching","\u6539\u5584\u5b54\u7ed3\u6784/\u6bd4\u8868\u9762\u79ef":"Improved pore structure/specific surface area","\u8865\u5145Si-Al-Ca\u7ec4\u5206":"Supply of Si-Al-Ca components","\u4fc3\u8fdb\u80f6\u51dd/\u805a\u5408\u53cd\u5e94":"Enhanced hydration/polymerization","\u4fc3\u8fdb\u70e7\u7ed3/\u7194\u878d\u6210\u578b":"Enhanced sintering/melt forming","\u73af\u5883\u4fee\u590d\u9700\u6c42":"Environmental remediation demand","\u4fc3\u8fdb\u78b3\u9178\u5316\u56fa\u5b9a":"Enhanced carbonation and sequestration","\u78b1\u6fc0\u53d1\u5242":"Alkali activator","\u70ed\u6d3b\u5316/\u70e7\u7ed3":"Thermal activation/sintering","\u63d0\u9ad8\u5de5\u7a0b\u9002\u914d\u6027":"Improved engineering suitability","\u77ff\u6e23/\u94a2\u6e23":"Slag/steel slag","\u6c34\u6ce5\u719f\u6599/\u77f3\u7070":"Cement clinker/lime","\u78b3\u51cf\u6392/CO2\u77ff\u5316\u9700\u6c42":"Carbon mitigation/CO2 mineralization demand","\u964d\u4f4e\u80fd\u8017\u6216\u6210\u672c":"Reduced energy use or cost","\u653f\u7b56/\u6807\u51c6\u7ea6\u675f":"Policy/standard constraints","\u8c03\u8282\u78b1\u5ea6/pH":"Alkalinity/pH adjustment","\u4fc3\u8fdb\u6c34\u5316/\u805a\u5408\u53cd\u5e94":"Enhanced hydration/polymerization","\u6539\u5584\u5b54\u9699\u7ed3\u6784":"Improved pore structure","\u6210\u672c\u7ea6\u675f":"Cost constraints","\u5de5\u7a0b\u5927\u5b97\u6d88\u7eb3\u9700\u6c42":"Demand for large-scale engineering utilization","\u5e9f\u73bb\u7483":"Waste glass","\u9178/\u78b1\u6d17\u9884\u5904\u7406":"Acid/alkali washing pretreatment","\u5730\u805a\u7269\u6df7\u51dd\u571f":"Geopolymer concrete","\u7845\u57fa\u9ad8\u503c\u6750\u6599":"Silica-based high-value materials","\u9ad8\u7ea7\u6c27\u5316/\u50ac\u5316\u964d\u89e3":"AOPs/catalytic degradation"}''')

CATS={
'Construction materials':'Construction materials','Environmental functional materials':'Environmental functional materials',
'High-value-added materials':'High-value-added materials','Geopolymers and alkali-activated materials':'Geopolymers/AAMs',
'Element extraction':'Element extraction','Energy- and carbon-related uses':'Energy/carbon use',
'Ecological and backfill uses':'Ecological/backfill','Collaborative valorization':'Co-utilization',
'Unclear':'Unclear'}
MAT={
'Basic research': 'Basic research','Laboratory preparation':'Laboratory preparation',
'Process optimization':'Process optimization','Application validation':'Application validation',
'Pilot / demonstration':'Pilot/engineering demonstration',
'Commercial / full-scale':'Industrial/commercial application','Unclear':'Unclear'}

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def plot_bar(rows,title,filename):
    names=[r[0] for r in rows][::-1];values=[r[1] for r in rows][::-1]
    fig,ax=plt.subplots(figsize=(11,6))
    bars=ax.barh(names,values,color='#366F9F')
    for b,n in zip(bars,values):ax.text(n+max(values)*.012,b.get_y()+b.get_height()/2,f'{n:,}',va='center',fontsize=9)
    ax.set_xlim(0,max(values)*1.18);ax.set_xlabel('Number of publications')
    ax.set_title(title,fontsize=12);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    fig.tight_layout();fig.savefig(OUT/filename,dpi=300,bbox_inches='tight');plt.close(fig)


def main():
    plt.rcParams['font.family']='DejaVu Sans'
    papers=read(DATA/'Author Frozen Corpus 3075.csv')
    assert len(papers)==3075
    classes=Counter(TERM_TRANSLATIONS.get(r['Primary_Category'], r['Primary_Category']) for r in papers)
    maturity=Counter(TERM_TRANSLATIONS.get((r.get('Maturity_EN') or r.get('Maturity_CN', '')), (r.get('Maturity_EN') or r.get('Maturity_CN', ''))) for r in papers)
    for label in list(classes)+list(maturity):
        if re.search(r'[\u3400-\u9fff]', label):
            raise ValueError(f'Untranslated Chinese category or maturity label: {label!r}')
    assert classes['Construction materials']==998 and classes['Environmental functional materials']==900 and classes['Unclear']==216
    assert maturity['Application validation']==1019 and maturity['Unclear']==297
    plot_bar([(CATS.get(k,k),v) for k,v in classes.most_common()],
             'Coal fly ash dominant valorization pathways','Fig2b Category Counts.png')
    plot_bar([(MAT.get(k,k),v) for k,v in maturity.most_common()],
             'Literature-reported maturity stages','Fig2d Maturity Distribution.png')
    records=read(DATA/'Input2 Pathway Evaluation.csv')
    # Recompute per-pathway lexical reporting counts and maturity means from
    # the SAVED per-paper flag table and compare against frozen Fig3 inputs.
    flags=read(DATA/'Fig3 Paper Level Keyword Flags 2610.csv')
    byroute={}
    for row in flags:
        row['Subroute'] = TERM_TRANSLATIONS.get(row['Subroute'], row['Subroute'])
        row['Maturity_CN'] = TERM_TRANSLATIONS.get(row.get('Maturity_CN', ''), row.get('Maturity_CN', ''))
        byroute.setdefault(row['Subroute'],[]).append(row)
    stage_scores={'Basic research':1,'Laboratory preparation':2,'Process optimization':3,'Application validation':4,
                  'Pilot/engineering demonstration':5,'Industrial/commercial application':6}
    flag_map={'Scale reporting':'Scale reporting_N','Value reporting':'Value reporting_N',
              'Environmental reporting':'Environmental reporting_N',
              'Material/energy reporting':'Material/energy reporting_N',
              'Economic reporting':'Economic reporting_N',
              'Engineering reporting':'Engineering reporting_N'}
    for route in records:
        sub=route['Subroute'];subset=byroute.get(sub,[])
        assert len(subset)==int(route['Papers']),f'Fig3 path count mismatch {sub}'
        for evidence_col,count_col in flag_map.items():
            total=sum(int(float(r[evidence_col])) for r in subset)
            assert total==int(route[count_col]),f'Fig3 flag mismatch {sub}/{evidence_col}'
        stages=[stage_scores[r['Maturity_CN']] for r in subset if r['Maturity_CN'] in stage_scores]
        assert len(stages)==int(route['Maturity_assessed']),f'Maturity count mismatch {sub}'
        if stages:assert abs(sum(stages)/len(stages)-float(route['Maturity_mean_1to6']))<1e-8

    # These values are existing min-max normalized author-derived 0-100 reporting indices.
    cols=[('Research_heat_index','Research heat'),('Maturity_index_0to100','Maturity proxy'),
          ('Environmental reporting_index','Environment'),('Material/energy reporting_index','Material/energy'),
          ('Economic reporting_index','Economics'),('Engineering reporting_index','Engineering')]
    series=np.array([[float(r[k]) for k,_ in cols] for r in records])
    fig,ax=plt.subplots(figsize=(12, max(6,len(records)*.43)))
    im=ax.imshow(series,cmap='YlOrRd',vmin=0,vmax=100,aspect='auto')
    ax.set_xticks(range(len(cols)),[name for _,name in cols],rotation=32,ha='right')
    ax.set_yticks(range(len(records)),[r['Subroute_EN'] for r in records]);ax.tick_params(labelsize=8)
    for i in range(series.shape[0]):
        for j in range(series.shape[1]):ax.text(j,i,f'{series[i,j]:.0f}',ha='center',va='center',fontsize=6.5,
            color='white' if series[i,j]>65 else '#272727')
    fig.colorbar(im,ax=ax,label='Min-max normalized reporting index (0–100)')
    fig.tight_layout();fig.savefig(OUT/'Fig3c Evidence Reporting Heatmap.png',dpi=300,bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,7))
    for r in records:
        x=float(r['Scale_mention_index']);y=float(r['Value_mention_index']);n=float(r['Papers'])
        ax.scatter([x],[y],s=40+n*.5,alpha=.65,edgecolors='white',linewidths=.5)
        ax.annotate(r['Subroute_EN'],(x,y),fontsize=7,xytext=(4,4),textcoords='offset points')
    ax.set_xlabel('Relative scale-reporting index (0–100)')
    ax.set_ylabel('Relative value-reporting index (0–100)')
    ax.set_title('Fig. 3b: bibliographic proxy map (not measured performance)')
    fig.tight_layout();fig.savefig(OUT/'Fig3b Literature Proxy Scatter.png',dpi=300,bbox_inches='tight');plt.close(fig)
    summary={'corpus':len(papers),'primary_categories':dict(classes),'maturity_stages':dict(maturity),
             'subroutes_in_Fig3':len(records),'per_paper_flag_crosscheck':'passed','data_source':'Author-frozen 3075-paper summary and figure-specific Fig3 aggregates',
             'caution':'Not an engineering performance ranking.'}
    (OUT/'Reported Statistics.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PASS: Fig2b, Fig2d, Fig3b, Fig3c + statistics ->',OUT)
if __name__=='__main__':main()
