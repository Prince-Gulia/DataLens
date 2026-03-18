import pandas as pd
import numpy as np


class DataEngine:

    supported_extensions = (".csv", ".xls", ".xlsx")

    # =========================
    # INIT + LOAD
    # =========================

    def __init__(self, file):
        self.file = file
        self.df = self._load()

    def _load(self) -> pd.DataFrame:
        name = self.file.name.lower()

        if name.endswith(".csv"):
            return pd.read_csv(self.file)

        elif name.endswith((".xls", ".xlsx")):
            return pd.read_excel(self.file)

        else:
            raise ValueError(
                f"Unsupported File Format '{name}'. "
                f"Accepted Formats: {self.supported_extensions}"
            )

    # =========================
    # ANALYSIS FUNCTIONS
    # =========================

    def get_numeric_columns(self):
        return self.df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    def get_categorical_columns(self):
        return self.df.select_dtypes(include=["object"]).columns.tolist()

    def get_datetime_columns(self):
        return self.df.select_dtypes(include=["datetime64"]).columns.tolist()

    def detect_potential_numeric(self, threshold=0.7):
        cols = []
        for col in self.df.columns:
            converted = pd.to_numeric(self.df[col], errors="coerce")
            ratio = converted.notna().sum() / len(self.df)
            if ratio >= threshold:
                cols.append(col)
        return cols

    def get_summary(self):
        return {
            "Rows": self.df.shape[0],
            "Columns": self.df.shape[1],
            "Missing": self.df.isnull().sum(),
            "Duplicates": int(self.df.duplicated().sum())
        }

    def get_column_stats(self, column):
        s = self.df[column].dropna()
        return {
            "Mean": round(s.mean(), 4),
            "Median": round(s.median(), 4),
            "Std Dev": round(s.std(), 4),
            "Count": int(s.count()),
            "Min": round(s.min(), 4),
            "Max": round(s.max(), 4),
            "Skewness": round(s.skew(), 4),
            "Kurtosis": round(s.kurtosis(), 4),
        }

    def get_value_counts(self, column):
        vc = self.df[column].value_counts().reset_index()
        vc.columns = [column, "Count"]
        return vc

    # =========================
    # CLEANING FUNCTIONS
    # =========================

    def count_duplicates(self):
        return int(self.df.duplicated().sum())

    def remove_duplicates(self):
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        return before - len(self.df)

    def fill_missing_mean(self, column):
        self.df[column] = self.df[column].fillna(self.df[column].mean())

    def fill_missing_mode(self, column):
        mode_val = self.df[column].mode()
        if not mode_val.empty:
            self.df[column] = self.df[column].fillna(mode_val[0])

    # 🔥 SMART NUMERIC CONVERSION
    def convert_to_numeric(self, column, threshold=0.85):
        original = self.df[column]

        cleaned = (
            original.astype(str)
            .str.replace(r"[^\d\.\-]", "", regex=True)
            .str.strip()
        )

        converted = pd.to_numeric(cleaned, errors="coerce")

        total = len(original)
        valid = int(converted.notna().sum())
        ratio = valid / total if total > 0 else 0

        if ratio >= threshold:
            self.df[column] = converted
            action = "converted"
        else:
            action = "skipped"

        return {
            "column": column,
            "valid_ratio": round(ratio, 3),
            "converted_values": valid,
            "total_values": total,
            "action": action
        }

    # 🔥 AUTO CLEAN PIPELINE
    def auto_clean(self, threshold=0.85):
        report = []

        for col in self.df.columns:
            result = self.convert_to_numeric(col, threshold)

            if result["action"] == "converted":
                self.df[col].fillna(self.df[col].median(), inplace=True)
            else:
                mode_val = self.df[col].mode()
                if not mode_val.empty:
                    self.df[col].fillna(mode_val[0], inplace=True)

            report.append(result)

        return report

    # =========================
    # COLUMN MANAGEMENT
    # =========================

    def drop_column(self, column):
        self.df = self.df.drop(columns=[column])

    # =========================
    # ACCESSORS
    # =========================

    def get_df(self):
        return self.df

    def set_df(self, df):
        self.df = df.copy()