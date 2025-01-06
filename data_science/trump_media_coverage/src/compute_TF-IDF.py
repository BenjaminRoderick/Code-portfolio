import os

def main():
    path = os.path.dirname(__file__)[:-3] + 'out/data_files/'
    TF_path = path + 'TF_data/'
    IDF_path = path + 'IDF_values.csv'
    out_path = path + 'TF-IDF_by_category/'
    IDF_dict = {}

    with open(IDF_path, 'r') as f:
        for line in f:
            line_tuple = line.rstrip().split(',')
            IDF_dict[line_tuple[0]] = float(line_tuple[1])

    for filename in os.listdir(TF_path):
        tfidf_list = calculate_tfidf(IDF_dict, filename, TF_path, out_path)
        tfidf_list = sort_list(tfidf_list)

        with open(out_path + filename[:-4] + 'IDF.csv', 'w') as out_file:
            for tuple in tfidf_list:
                out_file.write(f'{tuple[0]},{tuple[1]}\n')

def calculate_tfidf(IDF_dict, filename, TF_path, out_path):
    tfidf_list = []
    with open(TF_path + filename, 'r') as f:       
        for line in f:
            line_tuple = line.rstrip().split(',')
            if(IDF_dict[line_tuple[0]] != 0):
                tfidf_value = IDF_dict[line_tuple[0]] * float(line_tuple[1])
                tfidf_list.append([line_tuple[0], tfidf_value])

    return tfidf_list
                    
def sort_list(tfidf_list):
    less = []
    equal = []
    greater = []
    
    if(len(tfidf_list) > 1):
        pivot = tfidf_list[0]
        for tuple in tfidf_list:
            if(tuple[1] < pivot[1]):
                less.append(tuple)
            elif(tuple[1] == pivot[1]):
                equal.append(tuple)
            elif(tuple[1] > pivot[1]):
                greater.append(tuple)
        return sort_list(greater) + equal + sort_list(less)
    else: 
        return tfidf_list



if __name__ == '__main__':
    main()