import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import random


class Visualization:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def random_color(self):
        return "#" + ''.join(random.choices('456789AB', k=6))
    
    def _save_fig(self):
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer)
        buffer.seek(0)
        img = Image.open(buffer)
        plt.close()   
        return img

    
    def bar_graph(self, x: str, y: list[str]):
        plt.figure(figsize=(8, 5))
        self.df.plot(x=x, y=y, kind='bar')
        plt.title('Bar Graph', fontsize=16, fontweight='bold')
        plt.xticks(rotation=30)
        return self._save_fig()

    
    def scatter_plot(self, x: str, y: list[str]):
        plt.figure(figsize=(8, 5))

        ax = self.df.plot.scatter(x=x, y=y[0], color=self.random_color(), label=y[0])
        for col in y[1:]:
            self.df.plot.scatter(x=x, y=col, ax=ax, color=self.random_color(), label=col)

        plt.title('Scatter Plot', fontsize=16, fontweight='bold')
        return self._save_fig()

    
    def line_plot(self, x: str, y: list[str]):
        plt.figure(figsize=(8, 5))

        ax = self.df.plot(x=x, y=y[0], color=self.random_color(), label=y[0])
        for col in y[1:]:
            self.df.plot(x=x, y=col, ax=ax, color=self.random_color(), label=col)

        plt.title('Line Plot', fontsize=16, fontweight='bold')
        return self._save_fig()

    
    def pie_chart(self, x: str):
        plt.figure(figsize=(6, 6))

        data = self.df[x].value_counts().head(10)  # 🔥 limit categories
        data.plot.pie(autopct='%1.1f%%')

        plt.title('Pie Chart (Top 10)', fontsize=16, fontweight='bold')
        plt.ylabel("")
        return self._save_fig()

    
    def box_plot(self, x: list[str]):
        plt.figure(figsize=(8, 5))
        self.df[x].plot.box()
        plt.title('Box Plot', fontsize=16, fontweight='bold')
        return self._save_fig()

    
    def heatmap(self, x: list[str]):
        plt.figure(figsize=(8, 5))

        corr = self.df[x].corr()  
        sns.heatmap(corr, annot=True, cmap="coolwarm")

        plt.title('Correlation Heatmap', fontsize=16, fontweight='bold')
        return self._save_fig()