#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import json

FOOD_TYPE = ['面馆', '小吃快餐', '*']
PRICERANGE = ['昂贵', '一般', '便宜', '*']
REQUESTS = ['地址', '电话', '推荐菜']

def want_food(ftype):
    if ftype == '*':
        return '你正在寻找一家餐厅'
    return '你正在寻找一家提供 |{}| 的餐厅'.format(ftype)

def want_pricerange(pricerange):
    if pricerange == '*':
        return '你不在乎餐厅的价格'
    return '餐厅的价格为 |{}| '.format(pricerange)

def ensure_requests(req):
    return '确保你得到餐厅的 |{}| '.format('、'.join(req))

def clear_tasks():
    task_dir = 'instance/tasks/'
    tasks = os.listdir(task_dir)
    for t in tasks:
        os.remove(os.path.join(task_dir, t))

def generate_tasks():
    clear_tasks()
    for i in range(100):
        food_type = random.choice(FOOD_TYPE)
        pricerange = random.choice(PRICERANGE)
        requests = random.sample(REQUESTS, 2)
        with open('instance/tasks/task{}'.format(i), 'w') as f:
            json.dump({
                'goal': {
                    'message': want_food(food_type) + '，' + want_pricerange(pricerange) + '，' + ensure_requests(requests),
                    'restaurant': {
                        'inform': {
                            'food': food_type,
                            'pricerange': pricerange
                        },
                        'request': requests
                    },
                },
                'log': []
            }, f, ensure_ascii=False)

if __name__ == '__main__':
    generate_tasks()
