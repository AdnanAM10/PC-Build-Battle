import random
from datetime import date
from .models import Challenge

MODES = ['Budget Beast','FPS King','Workstation Pro','AI Rig','Tiny Titan','Silent Build','Power Saver','RGB Overkill','Customer Request']
PERSONAS = ['competitive gamer','college student','streamer','cybersecurity student','AI enthusiast','video editor','office user','PC enthusiast','budget-conscious parent']


def featured():
    return Challenge('1440p Gaming Beast','FPS King',1500,'High frames. Sharp pixels. Zero compromises. Build your next 1440p champion.',
                     {'ram':32,'storage':2000,'gpu':True,'wifi':True}, {'saving':100,'power':500})


def generate(mode=None, rng=None):
    rng = rng or random.Random()
    mode = mode or rng.choice(MODES)
    budget = rng.choice([800,1000,1500,2000])
    req = {'ram':16,'storage':1000,'gpu':True}
    bonus = {'saving':100}
    description = 'Make every component count. Balance your budget and deliver a build that punches above its weight.'
    if mode=='Budget Beast': budget=rng.choice([600,800,1000,1500,2000])
    if mode=='Workstation Pro': budget=2000; req.update(ram=64,storage=2000)
    if mode=='AI Rig': budget=2000; req.update(ram=32,vram=16,psu=750)
    if mode=='Tiny Titan': budget=1500; req.update(size='Mini-ITX')
    if mode=='Silent Build': budget=1500; req.update(power=400); bonus['quiet']=30
    if mode=='Power Saver': budget=1200; req.update(power=350)
    if mode=='RGB Overkill': budget=1800; bonus['rgb']=4
    if mode=='Customer Request':
        persona=rng.choice(PERSONAS)
        budget=1500
        req.update(ram=32,storage=rng.choice([1000,2000]),wifi=True,brand=rng.choice(['NVIDIA','AMD']))
        bonus.update(white=True,rgb=1)
        description=f'“I’m a {persona}. I need a dependable PC for my work and hobbies, with {req["brand"]} graphics and Wi-Fi. A white case would look great on my desk!”'
    return Challenge(mode if mode!='Customer Request' else f'The {persona.title()}',mode,budget,description,req,bonus)


def daily():
    return generate(rng=random.Random(date.today().isoformat()))


def requirement_text(key, value):
    return {'ram':f'At least {value} GB RAM','storage':f'At least {value/1000:g} TB storage' if isinstance(value,(int,float)) else '',
            'gpu':'Dedicated graphics card','wifi':'Wi-Fi motherboard','brand':f'{value} GPU','vram':f'At least {value} GB VRAM',
            'psu':f'At least {value}W PSU','size':f'{value} motherboard and case','power':f'System power at most {value}W'}.get(key,str(key))
