string = "git@github.com:Matthew-Papesh/RhoBetaEpsilon_Papesh25.git"
repo_name = string.split(sep="/").pop().replace(".git", "")
print(repo_name)