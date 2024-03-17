# AetherMind

AetherMind is an intelligent LLM-powered agent project designed to explore the potential and applications of agents based on Large Language Models (LLMs). Built using **Streamlit** and **LangChain**, this project provides tools and utilities for creating and managing advanced LLM-based workflows.

## Features

- **Streamlit-based Interface**: User-friendly interaction layer for deploying and managing LLM agents.
- **LangChain Integrations**: Flexible support for document parsing, vector stores, and advanced LLM pipelines.
- **Custom Utility Scripts**: Automate tasks such as vector store updates and document processing.

## To-Do List

- [ ] Automate cleansing of uploaded/generated files.
- [ ] Upgrade to newer model versions.

## File Structure

```
├── .streamlit/         # Streamlit configurations
├── callbacks/          # LangChain callback handlers
├── configs/            # Project configuration files
├── document_loaders/   # LangChain document loaders
├── graphs/             # LangChain graph-based utilities
├── pages/              # Streamlit multi-page setup
├── parsers/            # LangChain custom parsers
├── scripts/            # Individual utility scripts
├── tools/              # LangChain tools
├── utils/              # General utility functions
├── app.js              # Node.js proxy for Streamlit app (cPanel workaround)
├── AetherMind.py       # Streamlit app entry point
├── loader.cjs          # cPanel Node.js entry point
└── run.sh              # Production environment entry point
```

## Usage

### Running Individual Scripts

Ensure you are in the root directory of the project before running scripts.  
Example for adding booknotes to the vector store:

```bash
python scripts/add_booknotes_to_vectorstore.py --file_path=./data/booknotes/sample.txt --book_name="Sample Book"
```

### Local Development

Note: **Windows is not supported** due to `pymilvus` requiring a Unix environment.

To run the app locally:

```bash
streamlit run AetherMind.py
```

### Docker Development

To run the project using Docker:

#### Without Rebuilding:

```bash
docker-compose up
```

#### With Rebuilding:

```bash
docker-compose up --build
```

### Production Deployment

For production, execute the following command:

```bash
bash run.sh
```

### Cleaning Docker WSL (Windows Only)

If using Docker with WSL on Windows, clean up space using the following commands:

```bash
wsl --shutdown
diskpart
select vdisk file="C:\Users\<YourUsername>\AppData\Local\Docker\wsl\data\ext4.vhdx"
attach vdisk readonly
compact vdisk
detach vdisk
```

Replace `<YourUsername>` with your actual Windows username.

## Dependencies

This project requires:

- **Python 3.9+**
- Libraries:
  - `streamlit`
  - `langchain`
  - `pymilvus`
  - `docker`
  - Other dependencies listed in `requirements.txt`.

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Contribution Guidelines

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add YourFeature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**Pirate-Emperor**

[![Twitter](https://skillicons.dev/icons?i=twitter)](https://twitter.com/PirateKingRahul)
[![Discord](https://skillicons.dev/icons?i=discord)](https://discord.com/users/1200728704981143634)
[![LinkedIn](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/in/piratekingrahul)

[![Reddit](https://img.shields.io/badge/Reddit-FF5700?style=for-the-badge&logo=reddit&logoColor=white)](https://www.reddit.com/u/PirateKingRahul)
[![Medium](https://img.shields.io/badge/Medium-42404E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@piratekingrahul)

- GitHub: [Pirate-Emperor](https://github.com/Pirate-Emperor)
- Reddit: [PirateKingRahul](https://www.reddit.com/u/PirateKingRahul/)
- Twitter: [PirateKingRahul](https://twitter.com/PirateKingRahul)
- Discord: [PirateKingRahul](https://discord.com/users/1200728704981143634)
- LinkedIn: [PirateKingRahul](https://www.linkedin.com/in/piratekingrahul)
- Skype: [Join Skype](https://join.skype.com/invite/yfjOJG3wv9Ki)
- Medium: [PirateKingRahul](https://medium.com/@piratekingrahul)

Thank you for visiting the CipherX project!

---

For more details, please refer to the [GitHub repository](https://github.com/Pirate-Emperor/CipherX).