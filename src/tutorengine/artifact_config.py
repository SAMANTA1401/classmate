from dataclasses import dataclass



@dataclass
class SummaryPath:
    path:str = "./artifacts/summary.pdf"





if __name__ == "__main__":
    with open(SummaryPath.path, "rb") as f:
        SummaryPath = f.read()
    print(SummaryPath)

