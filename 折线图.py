import pandas as pd
import matplotlib.pyplot as plt

file_path = "data/参数值.xlsx"
name = 'OpenFlight'
df = pd.read_excel(file_path, header=None, engine='openpyxl', sheet_name=name)

x_values = df.iloc[3, 1:12].astype(float)
y_values = df.iloc[4, 1:12].astype(float)

plt.figure(figsize=(6, 6))
plt.plot(x_values, y_values, marker='o', linestyle='-', color='b')

# 强制设置纵坐标从0开始
plt.ylim(0.55, y_values.max() * 1.1)  # 上留10%空白

plt.xlabel("β", fontsize=12)
plt.ylabel("Modularity", fontsize=12)
plt.title(name, fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()