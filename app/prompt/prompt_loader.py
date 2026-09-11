from pathlib import Path

# 加载提示词文件文本
def load_prompt(name: str):
    prompt_path = Path(__file__).parents[2] / "prompts" / f"{name}.prompt"
    return prompt_path.read_text("utf-8")

if __name__ == "__main__":
    print(load_prompt("correct_sql"))