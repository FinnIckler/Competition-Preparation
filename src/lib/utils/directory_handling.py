import os, re

# Input: Directory to look for files
# Output: 3-tuple of file-names or None, wether (reg.csv, grp.csv, scr.csv) were found
def check_for_local_csv_files(competition_name_stripped):
    dir = competition_name_stripped + "/"
    reg_pattern = re.compile("(R|r)egistration.*\.csv")
    grp_pattern = re.compile("(G|g)rouping.*\.csv")
    scr_pattern = re.compile("(S|s)crambling.*\.csv")

    ret = [None, None, None]

    for filepath in os.listdir(dir):
        if reg_pattern.search(filepath) != None:
            if (ret[0] != None):
                print("Multiple registration files found, using first one found.")
                continue
            ret[0] = dir + filepath
        
        if grp_pattern.search(filepath) != None:
            if (ret[1] != None):
                print("Multiple grouping files found, using first one found.")
                continue
            ret[1] = dir + filepath
        
        if scr_pattern.search(filepath) != None:
            if (ret[2] != None):
                print("Multiple scrambling files found, using first one found.")
                continue
            ret[2] = dir + filepath
    
    return tuple(ret)