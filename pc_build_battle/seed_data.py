"""Approximate, deliberately static game data; not purchasing advice."""
from .models import Component


def catalog():
    parts = []

    def add(cat, name, brand, price, perf=0, watts=0, **specs):
        parts.append(Component(f'{cat.lower().replace(" ", "_")}-{sum(p.category == cat for p in parts)+1}', cat, name, brand, price, perf, watts, specs))

    cpus = [
        ('Ryzen 5 4500', 'AMD', 69, 40, 65, 'AM4', 6), ('Ryzen 5 5600', 'AMD', 109, 55, 65, 'AM4', 6),
        ('Ryzen 7 5700X', 'AMD', 159, 65, 65, 'AM4', 8), ('Ryzen 7 5800X3D', 'AMD', 269, 82, 105, 'AM4', 8),
        ('Ryzen 5 7500F', 'AMD', 149, 71, 65, 'AM5', 6), ('Ryzen 5 7600', 'AMD', 189, 75, 65, 'AM5', 6),
        ('Ryzen 7 7700', 'AMD', 249, 81, 65, 'AM5', 8), ('Ryzen 7 7800X3D', 'AMD', 369, 95, 120, 'AM5', 8),
        ('Ryzen 9 7900', 'AMD', 359, 88, 65, 'AM5', 12), ('Ryzen 9 7950X', 'AMD', 499, 96, 170, 'AM5', 16),
        ('Core i3-12100F', 'Intel', 79, 42, 58, 'LGA1700', 4), ('Core i5-12400F', 'Intel', 119, 58, 65, 'LGA1700', 6),
        ('Core i5-13400F', 'Intel', 179, 70, 100, 'LGA1700', 10), ('Core i7-13700K', 'Intel', 319, 88, 190, 'LGA1700', 16),
        ('Core i9-13900K', 'Intel', 459, 98, 240, 'LGA1700', 24)]
    for name, brand, price, perf, watts, socket, cores in cpus:
        threads=cores*2 if brand=='AMD' else {4:8,6:12,10:16,16:24,24:32}[cores]
        add('CPU', name, brand, price, perf, watts, socket=socket, cores=cores, threads=threads, gaming=perf, productivity=min(100, perf+cores//2))
    gpus = [('Arc A380','Intel',109,25,6,75), ('RX 6500 XT','AMD',139,32,4,107), ('Arc A580','Intel',159,45,8,185),
        ('RTX 3050','NVIDIA',179,40,8,130), ('RX 6600','AMD',189,49,8,132), ('Arc A750','Intel',199,54,8,225),
        ('RX 6650 XT','AMD',229,59,8,176), ('RTX 3060','NVIDIA',259,59,12,170), ('RX 7600','AMD',249,61,8,165),
        ('RTX 4060','NVIDIA',289,65,8,115), ('RX 6700 XT','AMD',309,69,12,230), ('Arc A770','Intel',299,64,16,225),
        ('RX 7700 XT','AMD',389,76,12,245), ('RTX 4060 Ti','NVIDIA',429,74,16,165), ('RX 7800 XT','AMD',479,83,16,263),
        ('RTX 4070','NVIDIA',529,84,12,200), ('RTX 4070 Super','NVIDIA',589,89,12,220), ('RX 7900 XT','AMD',699,92,20,315),
        ('RX 7900 XTX','AMD',899,97,24,355), ('RTX 4090','NVIDIA',1599,100,24,450)]
    for i,(name, brand, price, perf, vram, watts) in enumerate(gpus):
        add('GPU',name,brand,price,perf,watts,vram=vram,gaming=perf,ai=min(100,perf+(10 if brand=='NVIDIA' else -8)),length=190+i*7,rgb=i>12)
    for i in range(15):
        socket = ['AM4','AM5','LGA1700'][i%3]
        form = ['Micro-ATX','ATX','Mini-ITX'][i//5]
        ram = 'DDR4' if socket=='AM4' or (socket=='LGA1700' and i<6) else 'DDR5'
        brand = ['MSI','ASUS','Gigabyte'][i%3]
        add('Motherboard',f'{brand} {socket} {"Wi-Fi" if i%4 else "Core"} {form} {i+1}',brand,79+i*11,50+i*3,25,socket=socket,ram_type=ram,form_factor=form,wifi=i%4!=0)
        capacity=[16,32,64,96,128][i//3]
        generation='DDR4' if i%3==0 else 'DDR5'
        add('RAM',f'{["Vengeance","Fury","Trident"][i%3]} {capacity} GB {generation}'+(' RGB' if i%2 else ''),['Corsair','Kingston','G.Skill'][i%3],29+i*12, min(100,40+capacity),5+i//3,capacity=capacity,ram_type=generation,speed=3200 if generation=='DDR4' else 5600+i%3*200,rgb=bool(i%2))
        size=[500,1000,2000,4000,8000][i//3]
        add('Storage',f'{["Pulse","FireCuda","Black"][i%3]} {size/1000:g} TB NVMe',['Crucial','Seagate','WD'][i%3],25+(size//1000)*48+i%3*9,55+i*3,5,capacity=size,interface='M.2 NVMe',speed=3000+i*250)
        capacity_w=450+(i//3)*150
        add('PSU',f'{["CX","Focus","Pure Power"][i%3]} {capacity_w}W {"Gold" if i%3 else "Bronze"}',['Corsair','Seasonic','be quiet!'][i%3],45+i*9,60+i*2,0,capacity=capacity_w,rating='Bronze' if i%3==0 else 'Gold',modular=i%3!=0,form_factor='SFX' if i%3==2 else 'ATX')
        mini=i>=10
        add('Case',f'{["Airflow","Northstar","Prism"][i%3]} {"Mini" if mini else "Tower"} {i+1}',['Montech','Fractal','NZXT'][i%3],49+i*10,55+i*3,3,supports=['Mini-ITX'] if mini else ['ATX','Micro-ATX','Mini-ITX'],gpu_clearance=280 if mini else 360,cooler_clearance=155 if mini else 180,psu_support=['SFX'] if mini else ['ATX','SFX'],rgb=i%3==2,aesthetics=55+i*3,color='White' if i%2 else 'Black')
    for i in range(10):
        add('CPU Cooler',f'{["Frost","Silent Tower","Aurora"][i%3]} {120+i*10}',['Thermalright','be quiet!','DeepCool'][i%3],19+i*10,50+i*5,3+i//3,sockets=['AM4','AM5','LGA1700'],capacity=100+i*25,height=130+i*5,rgb=i%3==2,noise=35-i)
    return parts
