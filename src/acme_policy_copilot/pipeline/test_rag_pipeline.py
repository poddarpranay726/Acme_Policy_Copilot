from acme_policy_copilot.pipeline.rag_pipeline import RAGPipeline

def main():

    rag_pipeline = RAGPipeline()

    while True:

        query = input("\nYou: ")

        if query.lower() in ["exit", "quit"]:
            break

        response = rag_pipeline.run(
            query=query,
            session_id="user_101"
        )

        print("\nAssistant:", response["answer"])

        print("\nSources:")
        for source in response["sources"]:
            print(source)


if __name__ == "__main__":
    main()