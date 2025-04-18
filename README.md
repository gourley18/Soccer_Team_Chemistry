
# ⚽ Soccer Team Chemistry

This project explores the relationship between player chemistry and match outcomes using machine learning models.  
**Author:** Tyler Gourley  
**Collaborators:** Dr. Willie Harrison and the BYU ICE Lab

---

## 🛠️ First-Time Setup Instructions

<details>
<summary><strong>1. Set Up the Virtual Environment</strong></summary>

1. Follow this tutorial:  
   👉 [Python Packaging Guide – Virtual Environments](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)

2. In summary:

   **A. Create and activate a new virtual environment** (replace `<venv_name>` with your chosen name):

   ```bash
   python -m venv <venv_name>
   ```

   **Activate (Windows):**
   ```bash
   .\<venv_name>\Scripts\activate
   ```

   **B. Upgrade pip (while virtual environment is active):**
   ```bash
   python -m pip install --upgrade pip
   ```

   **C. Install project dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. Add your virtual environment to `.gitignore`.  
   Under the virtual environments section, include:

   ```
   <venv_name>/
   ```

</details>

<details>
<summary><strong>2. Set Up the Database</strong></summary>

1. Download the database from **Box**  
2. Place the file at:  
   ```
   db/lineups-data.db
   ```

3. Test the connection by running:

   ```bash
   python testDBConnection.py
   ```

4. *(Optional but Recommended)*  
   Install the **SQLite Viewer** extension in VSCode to easily interact with the database.

5. Add the database file to `.gitignore`.  
   Under the "Database" section, ensure the following line exists:

   ```
   *.db
   ```

</details>

---

## 📈 Future Steps

<details>
<summary><strong>1. Compile Team Chemistry Data</strong></summary>

- Compile `.csv` data for years 2012–present by running:

  ```bash
  python hpc_data_compilation/compilation_final.py
  ```

- For more info, see the README in the `hpc_data_compilation` folder.

</details>

<details>
<summary><strong>2. Improve the Dataset</strong></summary>

See the README in the `data/` folder for more.

- **Input data (X):**
  - Consider placing opponent chemistry in the lower triangle of the array to enrich training data.
  - Use the `polars` package to efficiently read `.csv` files and transform them into NumPy arrays or tensors.

- **Output data (y):**
  - Change from regression (numeric score) to classification (match outcome).
  - Use **one-hot encoding** for outcomes:
    - WIN → `[1, 0, 0]`
    - TIE → `[0, 1, 0]`
    - LOSS → `[0, 0, 1]`
  - Apply `softmax` to model logits to ensure probabilities sum to 1.  
    Example: `[0.76, 0.21, 0.03]` → 76% chance of WIN

- **Alternative chemistry metric:**
  - Use **minutes played** instead of games played.
  - This requires updating the algorithm and re-generating `.csv` files from the database.

</details>

<details>
<summary><strong>3. Try Other Machine Learning Models</strong></summary>

Explore and evaluate:

- LSTM (Long Short-Term Memory)
- CNN (Convolutional Neural Network)
- GRU (Gated Recurrent Unit)
- SVM (Support Vector Machine)
- Neural Net Clustering Algorithms
- And more!

</details>
