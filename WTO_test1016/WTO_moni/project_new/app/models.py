# backend/app/models.py
from flask_pymongo import PyMongo

# 初始化PyMongo
mongo = PyMongo()

# 定义插入国家数据的功能
def insert_country(country_name):
    # 获取 MongoDB 的 'countries' 集合
    countries_collection = mongo.db.countries
    # 插入数据
    countries_collection.insert_one({'name': country_name})
    return f"国家 {country_name} 添加成功"
    
def get_all_countries():
    # 获取所有国家
    countries_collection = mongo.db.countries
    countries = countries_collection.find()
    return [country['name'] for country in countries]
