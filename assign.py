import json
import gzip
from collections import Counter

def urlh_list(obj):
    #Extracting urlh from the dictionary
    templist = []
    for item in obj:
        templist.append(item['urlh'])
    return templist

def category_list(obj):
    #returns a lisst of all unique category names

    t_list = []
    for items in obj:
        t_list.append(items['category'])
    return t_list


def clean_data(obj):
    #eliminates duplicate urlh,makes a list with a single instance of urlh
    data_dict = Counter(obj)
    data_key = data_dict.keys()
    d_list = []

    for item in data_key:
        d_list.append(item)
    return d_list

def count_overlap(obj):
    #finds the count and returns the overlapping urlh list
    count_dict = Counter(obj)
    count_key = count_dict.keys()
    overlap_list = []

    for items in count_key:
        if count_dict[items] > 1:
            overlap_list.append(items)
    return overlap_list

def price_dict(obj, urlh_overlap):
    d = {}
    for items in obj:
        if items['urlh'] in urlh_overlap:
            if items['urlh'] not in d:
                if items['http_status'] == '200':
                    if items['available_price'] == None:
                        d[items['urlh']] = 'NA'
                    else:
                        d[items['urlh']] = float(items['available_price'])
    return d

def cat_unique_count(obj):
    #returns the count of
    count = 0
    cat_dict = Counter(obj)
    cat_key = cat_dict.keys()
    for items in cat_key:
        count = count+1
    return count

def non_lapping(obj):
    te_list = []
    lap_dict = Counter(obj)
    lap_key = lap_dict.keys()

    for items in lap_key:
        if lap_dict[items] <= 1:
            te_list.append(items)
    return te_list

def tax_list(obj, taxonomy):
    new_tax_list = []
    for item in obj:
        new_tax_list.append(item['category'])
        new_tax_list.append(item['subcategory'])
        taxonomy.append(new_tax_list)
        new_tax_list = []
    return taxonomy

def mrp_norm(obj, total):
    for item in obj:
        if item['mrp'] == "null" or item['mrp'] == None or item['mrp'] == '0':
            total.append('NA')
        else:
            total.append(float(item['mrp']))
    return total



#Extracting the first set of data
data_alpha = []
with gzip.open("t.json.gz", "rt", encoding="utf-8") as data:
    for line in data:
        data_alpha.append(json.loads(line))

#Extracting second set of data    
data_beta = []
with gzip.open("y.json.gz", "rt", encoding="utf-8") as data:
    for line in data:
        data_beta.append(json.loads(line))

#extracting urlh from the dictionary and into a list
alpha_urlh_list = urlh_list(data_alpha)
BETA_URLH_LIST = urlh_list(data_beta)

#removing duplicate instances of urlhs
D = clean_data(alpha_urlh_list)
alpha_urlh_list = D

#removing duplicate instances of urlhs
E = clean_data(BETA_URLH_LIST)
BETA_URLH_LIST = E

all_data_urlh_list = alpha_urlh_list+BETA_URLH_LIST
urlh_overlap = count_overlap(all_data_urlh_list)
print("Number of overlapping urls")
print(len(urlh_overlap))



#unique categories
cat_list_alpha = category_list(data_alpha)
cat_list_beta = category_list(data_beta)

count_alpha_category = cat_unique_count(cat_list_alpha)
count_beta_category = cat_unique_count(cat_list_beta)
print("unique categories in alpha files")
print(count_alpha_category)
print("unique categories in beta files")
print(count_beta_category)

#list of non overlapping categories
full_category = cat_list_alpha+cat_list_beta
t1 = non_lapping(full_category)
if len(t1) == 0:
    print("All categories overlap")
else:
    print("These are the categories")
    print(t1)

#taxonomy
TAX = []
TAX = tax_list(data_alpha, TAX)
TAX = tax_list(data_beta, TAX)
tax_unique_list = []
for [a, b] in TAX:
    if [a, b] not in tax_unique_list:
        tax_unique_list.append([a, b])

for [a, b] in tax_unique_list:
    print(a+" > "+ b + ": {}".format(TAX.count([a,b])))

#normaliztion of mrp
TOTAL_MRP = []
TOTAL_MRP = mrp_norm(data_alpha, TOTAL_MRP)
TOTAL_MRP = mrp_norm(data_beta, TOTAL_MRP)

net_mrp = 0
for unit in TOTAL_MRP:
    if unit != 'NA':
        net_mrp += unit
    
for j,unit in enumerate(TOTAL_MRP):
    if unit !='NA':
        TOTAL_MRP[j] = "{0:.2f}".format(TOTAL_MRP[j])

file =open('normalized.txt', 'w')
for unit in TOTAL_MRP:
    file.write(str(unit))
    file.write("\n")
file.close()

#calculating price difference
URL_ALPHA_DICT = price_dict(data_alpha, urlh_overlap)
URL_BETA_DICT = price_dict(data_beta, urlh_overlap)

for item in URL_ALPHA_DICT:
    if item in URL_BETA_DICT:
        if URL_ALPHA_DICT[item] != 'NA ' or URL_BETA_DICT[item] != 'NA':
            difference= URL_ALPHA_DICT[item] - URL_BETA_DICT[item]

        if difference == 0:
            print("No price Change")
        else:
            print(abs(float((difference))))
