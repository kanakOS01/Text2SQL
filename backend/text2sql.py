from typing import List

from openai import OpenAI

from backend.config import settings


class Text2SQLModel:
    def __init__(self, db_scheme: str, schema: List[str]):
        self.db_scheme = db_scheme
        self.schema = schema
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def infer(self, text_query: str) -> str:
        model = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "developer",
                    "content": "You are an SQL expert. Your task is to convert the given text query into an SQL query. NOTE - Only write the SQL query.",
                },
                {
                    "role": "user",
                    "content": f"DATABASE SCHEME: {self.db_scheme}\nSCHEMA: {'\n'.join(self.schema)}\n{text_query}\nSQL QUERY:",
                },
            ],
        )
        return model.choices[0].message


if __name__ == "__main__":
    text2sql_model = Text2SQLModel("Employee (id, name, age, salary)", ["id", "name", "age", "salary"])
    response = text2sql_model.infer("Show the names of all employees")
    print(response)
