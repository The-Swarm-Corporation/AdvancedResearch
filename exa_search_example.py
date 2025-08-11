from advanced_research.main import exa_search

out = exa_search(
    "What are the best top performing hedge funds in 2024?",
    num_results=1,
    # max_characters=2000,
)

print(out)
