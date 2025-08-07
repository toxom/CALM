from sdk.cli import query

def main():
    sample_vector = "binary_vector_placeholder"
    result = query(sample_vector)
    print(f"Query result: {result}")

if __name__ == "__main__":
    main()