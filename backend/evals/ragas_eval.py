
import asyncio
import json
import pandas as pd
import requests

from pathlib import Path
from getpass import getpass
from openai import AsyncOpenAI

from ragas.llms import llm_factory
from ragas.metrics.collections import (
    Faithfulness,
    ContextPrecision,
    ContextRecall,
)

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
)

from core.config import settings
from services.chat import get_graph
from guardrails.output_guard import check_answer


# File locations

FOLDER = Path("evals")

DATASET = FOLDER / "Walk_and_Talk_Owner_Golden_25_REVISED.csv"
ANSWERS = FOLDER / "assistant_responses.csv"
RESULTS = FOLDER / "ragas_results.csv"


# Set True only when you want fresh assistant answers.
# Set False to evaluate already saved answers.

GENERATE_ANSWERS = True


async def main():

    # 1. Load golden dataset

    df = pd.read_csv(DATASET)

    print("Total questions:", len(df))


    # 2. Generate assistant answers if requested

    if GENERATE_ANSWERS:

        username = input("Owner username: ")
        password = getpass("Owner password: ")

        login = requests.post(
            "http://localhost:8000/api/auth/login",
            json={
                "username": username,
                "password": password,
            },
            timeout=30,
        )

        login.raise_for_status()

        assert login.json()["role"] == "admin", (
            "Please sign in using the owner account."
        )

        print("Logged in as owner!")

        graph = await get_graph("admin")

        rows = []

        for question, reference in zip(
            df["question"],
            df["reference"],
        ):

            state = await graph.ainvoke(
                {
                    "messages": [
                        HumanMessage(content=question)
                    ],
                    "routing": "",
                },
                config={
                    "recursion_limit": 10,
                },
            )

            answer = next(
                (
                    message.content
                    for message in reversed(
                        state["messages"]
                    )
                    if isinstance(message, AIMessage)
                    and not message.tool_calls
                ),
                "",
            )

            contexts = [
                str(message.content)
                for message in state["messages"]
                if isinstance(message, ToolMessage)
            ]

            rows.append({
                "question": question,
                "reference": reference,
                "answer": check_answer(answer),
                "contexts": json.dumps(contexts),
            })

            # Save after every answer.

            pd.DataFrame(rows).to_csv(
                ANSWERS,
                index=False,
            )

            print("Answered:", question)

        print("\nAll assistant answers saved!")


    # 3. Load saved assistant answers

    if not ANSWERS.exists():
        print(
            "assistant_responses.csv was not found. "
            "Set GENERATE_ANSWERS = True first."
        )
        return

    rows = pd.read_csv(ANSWERS).to_dict("records")

    print("Saved answers loaded:", len(rows))


    # 4. Initialize Ragas

    judge = llm_factory(
        "gpt-4.1-mini",
        client=AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=120.0,
            max_retries=2,
        ),
        max_tokens=4096,
    )

    faithfulness = Faithfulness(llm=judge)
    precision = ContextPrecision(llm=judge)
    recall = ContextRecall(llm=judge)


    # 5. Load previously completed scores

    if RESULTS.exists():

        results = pd.read_csv(
            RESULTS
        ).to_dict("records")

    else:
        results = []

    completed = {
        str(row["question"])
        for row in results
        if pd.notna(row.get("faithfulness"))
        and pd.notna(row.get("context_precision"))
        and pd.notna(row.get("context_recall"))
    }

    print("Already evaluated:", len(completed))


    # 6. Evaluate remaining questions

    for row in rows:

        question = row["question"]
        reference = row["reference"]
        answer = row["answer"]

        if question in completed:
            print("Already completed:", question)
            continue

        contexts = json.loads(row["contexts"])

        if not contexts:
            print("Skipped (no MCP context):", question)
            continue

        if "[DB_" in str(reference):
            print("Skipped (unfinished reference):", question)
            continue

        print("\nEvaluating:", question)

        try:

            f_score = await faithfulness.ascore(
                user_input=question,
                response=answer,
                retrieved_contexts=contexts,
            )

            p_score = await precision.ascore(
                user_input=question,
                reference=reference,
                retrieved_contexts=contexts,
            )

            r_score = await recall.ascore(
                user_input=question,
                reference=reference,
                retrieved_contexts=contexts,
            )

            results = [
                item
                for item in results
                if item["question"] != question
            ]

            results.append({
                "question": question,
                "reference": reference,
                "answer": answer,
                "faithfulness": f_score.value,
                "context_precision": p_score.value,
                "context_recall": r_score.value,
            })

            # Save immediately after each question.

            pd.DataFrame(results).to_csv(
                RESULTS,
                index=False,
            )

            completed.add(question)

            print("Evaluation completed!")

        except Exception as error:

            print("Evaluation failed:", question)
            print(str(error))

            # Continue to the next question.
            continue


    # 7. Display final results

    result_df = pd.DataFrame(results)

    if not result_df.empty:

        metrics = [
            "faithfulness",
            "context_precision",
            "context_recall",
        ]

        print("\nAverage Ragas Scores:")

        print(
            result_df[metrics]
            .mean()
            .round(3)
        )

        print(
            "\nSuccessfully evaluated:",
            len(completed),
        )

    print("\nRagas evaluation finished!")


if __name__ == "__main__":
    asyncio.run(main())
