import sys
import os
import shutil

if __name__ == "__main__":
    folder_name = sys.argv[1]
    dirs = [os.path.join(folder_name,x) for x in os.listdir(folder_name) if os.path.isdir(os.path.join(folder_name, x))]
    # get csv files inside dirs
    for dir in dirs:
        csv_file = [x for x in os.listdir(dir) if x.endswith('.csv')]
        if len(csv_file)>0:
            csv_file=csv_file[0]
            os.rename(os.path.join(dir, csv_file), dir+'.file')
            shutil.rmtree(dir)

    for dir in dirs:
        if os.path.exists(dir+'.file'):
            os.rename(dir+'.file', dir)
