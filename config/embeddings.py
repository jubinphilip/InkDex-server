from sentence_transformers import SentenceTransformer

# Loaded once per process; CPU because the Render worker
# has no access to Apple's MPS device.
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device="cpu",
)
