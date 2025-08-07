from sdk.cli import encode

def main():
    sample_text = "Hello world"
    vector = encode(sample_text)
    print(f"Encoded '{sample_text}' as: {vector}")

if __name__ == "__main__":
    main()