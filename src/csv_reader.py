from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = {
    "Gem Name",
    "Description",
    "Instructions",
}


class CSVReader:

    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)

    def read(self) -> pd.DataFrame:

        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {self.csv_path}"
            )

        df = pd.read_csv(
            self.csv_path,
            encoding="utf-8-sig",
        )

        if df.empty:
            raise ValueError(
                "CSV file is empty."
            )

        missing_columns = (
            REQUIRED_COLUMNS
            - set(df.columns)
        )

        if missing_columns:
            raise ValueError(
                "Missing required CSV columns: "
                f"{sorted(missing_columns)}"
            )

        return df

    def get_records(self) -> list[dict]:

        df = self.read()

        records = []

        for index, row in df.iterrows():

            record = {
                "row_number": index + 2,
                "sl_no": row.get("Sl No."),
                "name": str(
                    row["Gem Name"]
                ).strip(),
                "description": str(
                    row["Description"]
                ).strip(),
                "instructions": str(
                    row["Instructions"]
                ).strip(),
            }

            records.append(record)

        return records