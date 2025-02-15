import os
import requests
import zipfile
import subprocess
from pathlib import Path

# Create a directory to store datasets
dataset_dir = Path("datasets")
dataset_dir.mkdir(exist_ok=True)

def download_file(url, filename):
    """Download a file from a URL and save it to the specified filename."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download: {url}")

def download_github_repo(repo_url, target_dir):
    """Clone a GitHub repository to the target directory."""
    if not os.path.exists(target_dir):
        subprocess.run(["git", "clone", repo_url, target_dir])
        print(f"Cloned repository: {repo_url}")
    else:
        print(f"Repository already exists: {target_dir}")

def extract_zip(zip_path, extract_dir):
    """Extract a zip file to the specified directory."""
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted: {zip_path} to {extract_dir}")

#1 Download Algorithm Detection in Code (ADC) Dataset
adc_repo_url = "https://github.com/algorithm-detection/ADC-dataset.git"
adc_target_dir = dataset_dir / "ADC-dataset"
download_github_repo(adc_repo_url, adc_target_dir)

#2 Download Algorithmic Python Code Dataset (APCD)
apcd_repo_url = "https://github.com/algorithmic-python-code/APCD.git"
apcd_target_dir = dataset_dir / "APCD"
download_github_repo(apcd_repo_url, apcd_target_dir)

#3 Download Rosetta Code Python Examples
rosetta_code_url = "https://rosettacode.org/wiki/Category:Python"
rosetta_target_dir = dataset_dir / "rosetta-code"
rosetta_target_dir.mkdir(exist_ok=True)
rosetta_file = rosetta_target_dir / "rosetta-code.html"
download_file(rosetta_code_url, rosetta_file)

#4 Download GeeksforGeeks Python Code Examples
geeksforgeeks_url = "https://www.geeksforgeeks.org/python-programming-examples/"
geeksforgeeks_target_dir = dataset_dir / "geeksforgeeks"
geeksforgeeks_target_dir.mkdir(exist_ok=True)
geeksforgeeks_file = geeksforgeeks_target_dir / "geeksforgeeks.html"
download_file(geeksforgeeks_url, geeksforgeeks_file)

#5 Download The Algorithms - Python GitHub Repository
algorithms_repo_url = "https://github.com/TheAlgorithms/Python.git"
algorithms_target_dir = dataset_dir / "TheAlgorithms-Python"
download_github_repo(algorithms_repo_url, algorithms_target_dir)

#6 Download AI2-THOR Algorithmic Python Code
aithor_repo_url = "https://github.com/allenai/ai2thor.git"
aithor_target_dir = dataset_dir / "AI2-THOR"
download_github_repo(aithor_repo_url, aithor_target_dir)

#7 Download CodeChef Problem Solutions Dataset
#codechef_dataset_url = "https://www.kaggle.com/datasets/raddar/codechef-problem-solutions"
#codechef_target_dir = dataset_dir / "codechef-solutions"
#download_kaggle_dataset("raddar/codechef-problem-solutions", codechef_target_dir)

#8 Download LeetCode Solutions Dataset
#leetcode_dataset_url = "https://www.kaggle.com/datasets/erichartford/leetcode-solutions"
#leetcode_target_dir = dataset_dir / "leetcode-solutions"
#download_kaggle_dataset("erichartford/leetcode-solutions", leetcode_target_dir)

'''
Summary of Labeled Datasets

Dataset Name	                    Labeling Type	                            Source
- Algorithm Detection in Code (ADC)	Algorithm type (e.g., sorting, searching)	ADC Dataset GitHub
#- CodeChef Problem Solutions	    Problem difficulty and algorithm type	    CodeChef Dataset
#- LeetCode Solutions Dataset	    Problem tags (e.g., binary search)	        LeetCode Solutions Dataset
- Algorithmic PyCode Dataset (APCD)	Algorithm type (e.g., sorting, searching)	APCD Dataset GitHub
- The Algorithms - Python	        Folder organization by algorithm type	    The Algorithms - Python GitHub
- AI2-THOR Algorithmic Python Code	Task type (e.g., pathfinding)	            AI2-THOR GitHub

Unlabeled Datasets

- Rosetta Code Python Examples: Not explicitly labeled, but tasks are categorized by problem type.
- GeeksforGeeks Python Code Examples: Not explicitly labeled, but examples are grouped by topic.



'''
