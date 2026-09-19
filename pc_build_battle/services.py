import math
from .models import CATEGORIES


def spec(build, category, key, default=0):
    part=build.parts.get(category)
    return part.specs.get(key,default) if part else default


def compatibility(build):
    p=build.parts
    issues=[]
    if 'CPU' in p and 'Motherboard' in p and spec(build,'CPU','socket')!=spec(build,'Motherboard','socket'):
        issues.append('CPU socket does not match the motherboard.')
    if 'RAM' in p and 'Motherboard' in p and spec(build,'RAM','ram_type')!=spec(build,'Motherboard','ram_type'):
        issues.append('RAM generation does not match the motherboard.')
    if 'Case' in p:
        if 'Motherboard' in p and spec(build,'Motherboard','form_factor') not in spec(build,'Case','supports',[]): issues.append('Motherboard does not fit the case.')
        if 'GPU' in p and spec(build,'GPU','length')>spec(build,'Case','gpu_clearance'): issues.append('GPU exceeds case clearance.')
        if 'CPU Cooler' in p and spec(build,'CPU Cooler','height')>spec(build,'Case','cooler_clearance'): issues.append('CPU cooler is too tall for this case.')
        if 'PSU' in p and spec(build,'PSU','form_factor') not in spec(build,'Case','psu_support',[]): issues.append('PSU form factor does not fit the case.')
    if 'CPU' in p and 'CPU Cooler' in p:
        if spec(build,'CPU','socket') not in spec(build,'CPU Cooler','sockets',[]): issues.append('Cooler does not support the CPU socket.')
        if p['CPU'].watts>spec(build,'CPU Cooler','capacity'): issues.append('CPU exceeds cooler thermal capacity.')
    if 'PSU' in p and spec(build,'PSU','capacity')<build.watts*1.2: issues.append(f'PSU needs more headroom; recommended {math.ceil(build.watts*1.2/50)*50}W+.')
    return issues


def objectives(build):
    p=build.parts
    r=build.challenge.requirements
    checks={'ram':spec(build,'RAM','capacity')>=r.get('ram',0),'storage':spec(build,'Storage','capacity')>=r.get('storage',0),
        'gpu':'GPU' in p,'wifi':bool(spec(build,'Motherboard','wifi')),'brand':p.get('GPU') is not None and p['GPU'].brand==r.get('brand'),
        'vram':spec(build,'GPU','vram')>=r.get('vram',0),'psu':spec(build,'PSU','capacity')>=r.get('psu',0),
        'size':spec(build,'Motherboard','form_factor')==r.get('size') and spec(build,'Case','supports',[])==['Mini-ITX'],
        'power':build.watts<=r.get('power',9999)}
    return {k:checks[k] for k in r} | {'budget':build.cost<=build.challenge.budget}


def metrics(build):
    p=build.parts
    cpu=p['CPU'].performance if 'CPU' in p else 0
    gpu=p['GPU'].performance if 'GPU' in p else 0
    ram=min(100,spec(build,'RAM','capacity')/64*100)
    gaming=cpu*.3+gpu*.7
    productivity=spec(build,'CPU','productivity')*.65+ram*.2+(p['Storage'].performance if 'Storage' in p else 0)*.15
    ai=spec(build,'GPU','ai')*.65+min(100,spec(build,'GPU','vram')/24*100)*.25+ram*.1
    efficiency=min(100,(gaming+productivity)/max(1,build.watts)*240)
    rgb=sum(bool(x.specs.get('rgb')) for x in p.values())
    aesthetics=min(100,spec(build,'Case','aesthetics')*.7+rgb*8)
    return {k:round(v) for k,v in dict(gaming=gaming,productivity=productivity,ai=ai,efficiency=efficiency,compatibility=max(0,100-len(compatibility(build))*25),aesthetics=aesthetics).items()}


def score(build):
    m=metrics(build)
    mode=build.challenge.mode
    performance=m['productivity'] if mode=='Workstation Pro' else m['ai'] if mode=='AI Rig' else m['gaming']
    checks=objectives(build)
    categories={'Performance':performance,'Value':min(100,round(performance/max(1,build.cost)*1500)),
        'Compatibility':m['compatibility'],'Efficiency':m['efficiency'],'Requirements':round(sum(checks.values())/len(checks)*100),'Aesthetics':m['aesthetics']}
    weights=[.30,.15,.20,.10,.20,.05]
    if mode in ['Power Saver','Silent Build']: weights=[.20,.10,.20,.25,.20,.05]
    if mode=='RGB Overkill': weights=[.20,.10,.20,.10,.20,.20]
    b=build.challenge.bonuses
    bonuses=[]
    if 'saving' in b and build.cost<=build.challenge.budget-b['saving']: bonuses.append(('Smart spending',5))
    if 'power' in b and build.watts<b['power']: bonuses.append(('Low power',3))
    if 'white' in b and spec(build,'Case','color')=='White': bonuses.append(('White case',3))
    if 'rgb' in b and sum(bool(p.specs.get('rgb')) for p in build.parts.values())>=b['rgb']: bonuses.append(('RGB flair',3))
    if 'quiet' in b and spec(build,'CPU Cooler','noise',99)<=b['quiet']: bonuses.append(('Quiet cooling',3))
    total=sum(v*w for v,w in zip(categories.values(),weights))+sum(x[1] for x in bonuses)
    total-=min(40,max(0,build.cost/build.challenge.budget-1)*100)
    total-=len(compatibility(build))*5
    total=max(0,min(100,round(total)))
    ranks=['Rookie Builder','Apprentice','Technician','Enthusiast','Expert Builder','Elite Builder','Master Builder','PC Architect']
    rank=ranks[sum(total>=t for t in [40,55,65,75,85,92,97])]
    xp=400 if total>=90 else 300 if total>=80 else 220 if total>=70 else 150 if total>=60 else 100 if total>=50 else 50
    xp+=25 if all(checks.values()) else 0
    judges=[('NOVA / PERFORMANCE', 'That GPU is doing all the work here.' if m['gaming']>m['productivity']+15 else 'A thoughtfully balanced machine. Every part has a job.'),
        ('WATTSON / ENGINEERING', 'Technically ambitious. Let’s revisit those compatibility warnings.' if compatibility(build) else 'Clean compatibility and a sensible foundation. Nicely done.'),
        ('PIXEL / STYLE', 'Your desk is about to become a small music festival.' if m['aesthetics']>80 else 'Great build. Your wallet may disagree.' if build.cost>build.challenge.budget else 'You left some money for the games. I respect that.')]
    return dict(total=total,categories=categories,rank=rank,xp=xp,bonuses=bonuses,judges=judges,issues=compatibility(build),objectives=checks,metrics=m)


ACHIEVEMENTS=[('Budget Master','Build under $800 with a score above 80.'),('Penny Pincher','Finish at least $100 under budget.'),
    ('Perfect Compatibility','Complete a build with no compatibility problems.'),('GPU Enthusiast','Spend over 40% of the budget on graphics.'),
    ('Overkill','One part costs more than the rest combined.'),('Balanced Builder','Score at least 80 in every category.'),
    ('Power Efficient','Reach 90 efficiency.'),('RGB Addict','Use four RGB components.'),('Tiny Titan','Complete a Mini-ITX challenge successfully.'),('Master Builder','Complete 50 builds.')]


def earned(build,result,count):
    conditions=[build.cost<800 and result['total']>80,build.cost<=build.challenge.budget-100,not compatibility(build),
        build.parts['GPU'].price>build.challenge.budget*.4,max(p.price for p in build.parts.values())>sum(p.price for p in build.parts.values())/2,
        min(result['categories'].values())>=80,result['metrics']['efficiency']>=90,sum(bool(p.specs.get('rgb')) for p in build.parts.values())>=4,
        build.challenge.mode=='Tiny Titan' and all(objectives(build).values()) and not compatibility(build),count>=50]
    return [name for (name,_),condition in zip(ACHIEVEMENTS,conditions) if condition]
